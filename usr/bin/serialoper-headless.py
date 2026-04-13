#!/usr/bin/env python3

import json
import os
import sys
import signal
import time
from serialoper.common.serial_operations import SerialWebsocket

# Asegura que Python encuentre tu paquete
sys.path.append("/usr/lib/serialoper")

# Descomentar la variable necesaria o escribir la ubicacion manualmente si no
# se encuentra en algunas rutas predefinidas aca abajo.
#CONFIG_PATH = "/etc/serialoper/config.json"
CONFIG_PATH = os.path.expanduser("~/.config/serialoper/config.json")

class SerialHeadless:
    def __init__(self):
        self.running = True
        self.serws = SerialWebsocket()

        self.setup_signal_handlers()

    # Se configuran la captura de señales de apagado/reinicio enviadas
    # por medio de systemd
    def setup_signal_handlers(self):
        signal.signal(signal.SIGINT, self.signal_handler) # Captura Ctrl+C (SIGINT)
        signal.signal(signal.SIGTERM, self.signal_handler) # Captura el "stop" enviado por systemd

    # Funciona cuando se envia una señal de apagado (SIGINT o SIGTERM) por medio
    # de systemd para detener el servicio de forma ordenada
    def signal_handler(self, sig, frame):
        print("[Headless] Recibida señal de apagado. Deteniendo operaciones...")
        self.running = False

    # Cargo configuracion de archivo JSON para procesamiento
    # Con esto cargo los datos requeridos de mi archivo JSON creado para revision
    def load_config(self):
        if not os.path.exists(CONFIG_PATH):
            print("[Config] No se encontró archivo de configuración")
        else:
            try:
                with open(CONFIG_PATH, "r") as file:
                    return json.load(file)
            
            except FileNotFoundError:
                print("[Config] Archivo de configuración no encontrado")
                sys.exit(1)

            except json.JSONDecodeError:
                print("[Config] El archivo no tiene un formato JSON valido")
                sys.exit(1)

            except Exception as error_exception:
                print(f"[Config] Error inesperado al cargar configuración: {error_exception}")
                sys.exit(1)

    # Metodo principal que ejecuta la logica del servicio
    def run(self):
        print("[Service] Iniciando serialoper-headless...")

        config = self.load_config()

        if not config:
            print("[Service] No se encontró configuración válida. Saliendo.")
            sys.exit(1)

        serial_conf = config.get("serial", {})
        ws_conf = config.get("websocket", {})

        try:
            # Extraer configuración del archivo JSON correspondiente
            # Configuracion para puerto serie
            rs_port = serial_conf.get("port")
            rs_baudrate = serial_conf.get("baudrate")
            rs_databits = serial_conf.get("databits")
            rs_parity = serial_conf.get("parity")
            rs_stopbits = serial_conf.get("stopbits")
            rs_flow = serial_conf.get("flowcontrol")
            rs_timeout = serial_conf.get("timeout")

            # Configuracion para Websocket
            ws_host = ws_conf.get("host")
            ws_port = ws_conf.get("port")

            print(f"[Service] Serial: {rs_port} @ {rs_baudrate}")
            print(f"[Service] WebSocket: ws://{ws_host}:{ws_port}")

            # IMPORTANTE:
            # No hay GTK → callback = None
            self.serws.start_serial_monitor(
                gtk_callback=None,
                rs_port=rs_port,
                rs_baudrate=rs_baudrate,
                rs_databits=rs_databits,
                rs_parity=rs_parity,
                rs_stopbits=rs_stopbits,
                rs_hwflowcontrol=rs_flow,
                rs_timeout=rs_timeout,
                ws_host=ws_host,
                ws_port=ws_port
            )

            # Loop principal (mantiene el proceso corriendo infinitamente hasta recibir señal de apagado)
            while self.running:
                time.sleep(2)

            # Limpiando recursos y deteniendo el servicio de forma ordenada
            print("[Service] Deteniendo servicio...")
            self.serws.stop_rs()

        except Exception as error_exception:
            print(f"[Service] Error en el servicio: {error_exception}")
            sys.exit(1)

if __name__ == "__main__":
    app = SerialHeadless()
    app.run()