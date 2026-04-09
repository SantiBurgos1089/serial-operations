import asyncio
import re
import serial
import threading
import websockets
from gi.repository import GLib
from .settings_app import GeneralSettings

# ──────────────────────────────────────────────────────────────────────────────
# Valores de configuracion de puerto serial a controles en frontend.
# Si un valor segun su frontend utilizado no corresponde en texto puede hacer el
# cambio de manera manual en el diccionario si asi es requerido, pero estos deben
# ser valores validos y existentes en base a la libreria pyserial.
# ──────────────────────────────────────────────────────────────────────────────

# Data bits
DATABITS_MAP = {
    "5": serial.FIVEBITS,
    "6": serial.SIXBITS,
    "7": serial.SEVENBITS,
    "8": serial.EIGHTBITS,
    }

# Paridad
PARITY_MAP = {
    "Ninguna": serial.PARITY_NONE,
    "Par":     serial.PARITY_EVEN,
    "Impar":   serial.PARITY_ODD,
    "Espacio": serial.PARITY_SPACE,
    "Marca":   serial.PARITY_MARK,
    }

# Bit de parada
STOPBITS_MAP = {
    "1":   serial.STOPBITS_ONE,
    "1.5": serial.STOPBITS_ONE_POINT_FIVE,
    "2":   serial.STOPBITS_TWO,
    }

# Control de flujo
# Se almacena como tupla para poder asignar ambos parámetros a serial.Serial
# en un único acceso al diccionario, evitando dos búsquedas separadas.
FLOWCONTROL_MAP = {
    "Ninguno":  False,
    "Hardware": True,
    "Xon/Xoff": False,
    }

# ──────────────────────────────────────────────────────────────────────────────
# Valores de configuracion de valores en equipos seriales RS232
# Los datos aca descritos son valores generales existentes en varios equipos en 
# base a configuraciones existentes, no hay un estandar definido y puede agregar 
# otros valores que considere que no existan si asi lo considera necesario para
# su frontend ocupado.
# ──────────────────────────────────────────────────────────────────────────────

# Baudrate de equipos seriales
BAUDRATE = [
    "100", "300", "600", "1200", "2400", "4800",
    "9600", "14400", "19200", "38400", "56000", 
    "57600", "115200", "128000", "256000"
]

# Databits
DATA_BITS = ["5", "6", "7", "8"]

# Paridad
PARITY = ["Ninguna", "Par", "Impar", "Espacio", "Marca"]

# Bit parada
STOP_BITS = ["1", "1.5", "2"]

# Control de flujo
FLOW_CONTROL = ["Ninguno", "Hardware", "Xon/Xoff"]

# Puerto websocket
WEBSOCKET_PORT = ["5050", "8765", "9000"]


genset = GeneralSettings()

# ──────────────────────────────────────────────────────────────────────────────
# Clase base: centraliza toda la configuración compartida de pyserial.
# SerialReader y SerialWebsocket heredan de aquí para no duplicar
# los mapeos ni la lógica de apertura del puerto.
# ──────────────────────────────────────────────────────────────────────────────
class SerialConfig():
    def __init__(self):
        self.serial_port = None
        self.is_running = False

    # Recibe los parametros de configuracion del puerto serial desde el frontend, mapeandolos a valores compatibles con pyserial
    # utilizando los diccionarios de mapeo definidos en el constructor, y luego construye el objeto con esos valores.
    def build_serial_port(self, port, baudrate, databits, parity="Ninguna", stopbits="1", 
                          hw_flowcontrol="Ninguno", sw_flowcontrol="Xon/Xoff", hw_timeout=1):
        # Obtiene los valores del diccionario en base a lo recibido como parametro inicial y lo asigna al mismo parametro
        # Caso contrario, retorna un valor por defecto o el valor que, idealmente, no afecte operatividad
        baudrate = int(baudrate)
        databits = int(DATABITS_MAP.get(databits, serial.EIGHTBITS))
        parity = PARITY_MAP.get(parity, serial.PARITY_NONE)
        stopbits = STOPBITS_MAP.get(stopbits, serial.STOPBITS_ONE)
        hw_flowcontrol = FLOWCONTROL_MAP.get(hw_flowcontrol, False)
        sw_flowcontrol = FLOWCONTROL_MAP.get(sw_flowcontrol, False)
        hw_timeout = float(hw_timeout)

        try:
            self.serial_port = serial.Serial(
                port=port,
                baudrate=baudrate,
                bytesize=databits,
                parity=parity,
                stopbits=stopbits,
                rtscts=hw_flowcontrol, # Control de flujo por hardware
                xonxoff=sw_flowcontrol, # Control de flujo por software
                timeout=hw_timeout
            )
            #print(f"Puerto serial {port} configurado y abierto exitosamente.")
            self.is_running = True
            return True

        except serial.SerialException as serial_error_exception:
            #print(f"Error al configurar el puerto serial: {serial_error_exception}")
            genset.send_notifications("Error", f"Error al configurar el puerto serial: {serial_error_exception}", "xsi-dialog-error-symbolic")
            self.serial_port = None
            self.is_running = False
            return False
        
    # Cierra el puerto serial de forma segura si está abierto
    def close_serial_port(self):
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
        
# ──────────────────────────────────────────────────────────────────────────────
# Monitoreo del puerto serial
# Hereda la configuración de SerialConfig; su responsabilidad es
# leer datos del puerto de forma continua y enviarlos al callback de GTK.
# ──────────────────────────────────────────────────────────────────────────────
class SerialReader(SerialConfig):
    def __init__(self):
        super().__init__()

        self.callback = None
        self.logging = False
        self.read_thread = None

    # Configura el puerto con build_serial_port (heredado) e inicia el hilo de lectura.
    def logs_serial_monitor(self, callback, sm_port, sm_baudrate, sm_databits, sm_parity, 
                            sm_stopbits, sm_hwflowcontrol, sm_swflowcontrol, sm_timeout):
        self.callback = callback
        self.is_running = True

        serial_reader = self.build_serial_port(
            port = sm_port,
            baudrate = sm_baudrate,
            databits = sm_databits,
            parity = sm_parity,
            stopbits = sm_stopbits,
            hw_flowcontrol = sm_hwflowcontrol,
            sw_flowcontrol= sm_swflowcontrol,
            hw_timeout = sm_timeout
        )

        if not serial_reader:
            self.is_running = False
            return
        
        self.read_thread = threading.Thread(target=self.read_from_serial, daemon=True)
        self.read_thread.start()

    # Lectura continua del puerto serial mientras la comunicación esté habilitada.
    def read_from_serial(self):
        while self.is_running and self.serial_port and self.serial_port.is_open:
            try:
                if self.serial_port.in_waiting > 0:
                    serial_data = self.serial_port.readline().decode("utf-8", errors="ignore").strip()
                    if self.callback:
                        GLib.idle_add(self.callback, serial_data)

            except serial.SerialException as serial_error_exception:
                #print(serial_error_exception)
                genset.send_notifications("Error", f"Error al leer el puerto: {serial_error_exception}", "xsi-dialog-error-symbolic")
                break

            except Exception as error_exception:
                #print(error_exception)
                genset.send_notifications("Error", f"Error inesperado: {error_exception}", "xsi-dialog-error-symbolic")
                break

    def stop_read_serial(self):
        self.is_running = False
        self.close_serial_port()

# ──────────────────────────────────────────────────────────────────────────────
# WebSocket + lectura serial en paralelo
# Hereda la configuración de SerialConfig; su responsabilidad es
# retransmitir los datos leídos del puerto a los clientes WebSocket conectados.
# ──────────────────────────────────────────────────────────────────────────────
class SerialWebsocket(SerialConfig):
    def __init__(self):
        super().__init__()
        self.serial_port = None
        self.clients = set()
        self.is_running = False
        self.loop = None

    async def ws_handler(self, websocket):
        self.clients.add(websocket)
        try:
            # Prueba en consola: total clientes conectados
            print(f"[WebSocket] Cliente conectado. Total clientes: {len(self.clients)}")
            # Mantiene la conexión abierta esperando a que el cliente se desconecte
            await websocket.wait_closed()
        finally:
            self.clients.remove(websocket)
            # Prueba en consola: total clientes desconectados
            print(f"[WebSocket] Cliente desconectado. Total clientes: {len(self.clients)}")

    async def start_ws_server(self, host, port):
        try:
            async with websockets.serve(self.ws_handler, host, port):
                # Prueba en consola: direccion y puerto que se escucha al correr el programa
                print(f"[WebSocket] Servidor escuchando en ws://{host}:{port}")
                await asyncio.Future() # se corre de manera infinita

        except OSError as os_error:
            error_msg = error_msg = f"El puerto {port} está ocupado. Favor verificar o cambiar puerto."
            print(f"[Error WebSocket] {error_msg} - {os_error}")

            # Se notifica a la interfaz gráfica de forma segura desde el hilo asincrono
            GLib.idle_add(genset.send_notifications, "Error de Red", error_msg, "xsi-dialog-error-symbolic")

            # Detenemos la lectura del puerto serial porque el WS falló
            self.stop_rs()


    def start_serial_monitor(self, gtk_callback, rs_port, rs_baudrate, rs_databits, rs_parity, 
                             rs_stopbits, rs_hwflowcontrol, rs_swflowcontrol, rs_timeout, ws_host, ws_port):
        self.is_running = True

        serial_reader = self.build_serial_port(
            port = rs_port,
            baudrate = rs_baudrate,
            databits = rs_databits,
            parity = rs_parity,
            stopbits = rs_stopbits,
            hw_flowcontrol = rs_hwflowcontrol,
            sw_flowcontrol = rs_swflowcontrol,
            hw_timeout = rs_timeout
        )

        if not serial_reader:
            self.is_running = False
            return
        
        # Crear loop asyncio una sola vez
        self.loop = asyncio.new_event_loop()

        # Inicia el hilo del servidor WebSocket
        threading.Thread(target=self.start_ws_loop, args=(ws_host, ws_port), daemon=True).start()

        # Inicia el hilo de lectura del puerto RS232
        threading.Thread(target=self.start_rs_loop, args=(gtk_callback,), daemon=True).start()

    def start_ws_loop(self, host, port):
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.start_ws_server(host, port))

    def start_rs_loop(self, gtk_callback):
        while self.is_running and self.serial_port and self.serial_port.is_open:

            try:
                serial_raw_data = self.serial_port.readline().decode("utf-8",errors="ignore").strip()

                # Si por el timeout la lectura viene vacia, volvemos a intentar:
                if not serial_raw_data:
                    continue

                # Extraer solamente numero
                match = re.search(r"[-+]?\d*\.?\d+", serial_raw_data)

                if not match:
                    continue

                final_value = match.group(0)

                # Seccion para enviar a la interfaz GTK
                if gtk_callback:
                    GLib.idle_add(gtk_callback, final_value)

                # Transmitir a todos los clientes WebSocket de forma segura entre hilos
                if self.loop and self.loop.is_running() and self.clients:
                    asyncio.run_coroutine_threadsafe(self.broadcast(final_value), self.loop)

            except serial.SerialException as serial_error_exception:
                print(f"[Error RS232 WS] {serial_error_exception}")
                break

            except Exception as error_exception:
                print(f"[Error Inesperado WS] {error_exception}")
                break

    async def broadcast(self, value):
        if self.clients:
            await asyncio.gather(
                *(client.send(value) for client in self.clients),
                return_exceptions=True
            )

    def stop_rs(self):
        self.is_running = False
        self.close_serial_port()

