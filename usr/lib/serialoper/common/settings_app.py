import gi
import json
import os
import re
import socket
gi.require_version('Notify', '0.7')
from gi.repository import Notify

# ──────────────────────────────────────────────────────────────────────────────
# Clase general: centraliza todos los metodos del programa que no se encuentren
# asociados a métodos o funciones de pyserial, websocket, monitoreo o similares.
# Depende solo de librerias internas de Python o librerias utilizadas en Linux.
# ──────────────────────────────────────────────────────────────────────────────
class GeneralSettings():
    def __init__(self):
        pass

    # Envia notificaciones de sistema operativo para dar aviso de acciones varias
    # por medio de la libreria libnotify de Linux
    def send_notifications(self, gs_title, gs_message, gs_icon="xsi-firmware-symbolic"):
        Notify.init("Operaciones RS232")
        notification = Notify.Notification.new(gs_title, gs_message, gs_icon)
        notification.show()

    # Obtiene la IP local del equipo para mostrar
    # Se crea un socket temporal para intentar conectarse a un servidor conocido (DNS de Google)
    # Se obtiene la direccion IP utilizada para este proceso
    # Si hay algun error, se coloca una IP 0.0.0.0 para error.
    # Puede actualizarse el DNS a utilizar si se necesitan otras pruebas adicionales.
    def get_local_ip(self):
        local_ip = None
        socket_connection = None

        try:
            socket_connection = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            socket_connection.connect(("8.8.8.8", 80))
            local_ip = socket_connection.getsockname()[0]
        except:
            local_ip = '0.0.0.0'
        finally:
            if socket_connection:
                socket_connection.close()

        return local_ip

    # Busco todos los puertos seriales detectados por el sistema, estos pueden aparecer como:
    # /dev/ttyS[0-9] para los puertos seriales integrados en el equipo
    # /dev/ttyUSB[0-9] para adaptadores USB a serie RS232
    # /dev/ttyACM* para otros microcontroladores como dispositivos Arduino
    def get_serial_ports(self):
        detected_ports = []

        for port in os.listdir('/dev'):
            if re.match(r'^ttyUSB\d+$', port):
                detected_ports.append(f"/dev/{port}")

            if re.match(r'^ttyS\d+$', port):
                detected_ports.append(f"/dev/{port}")

            if re.match(r'^ttyACM\d+$', port):
                detected_ports.append(f"/dev/{port}")

        return detected_ports
    
    # Cargo configuracion de archivo JSON
    # Con esto cargo los datos requeridos de mi archivo JSON creado para revision
    # Este metodo se utiliza principalmente para el servicio en consola, sin embargo, 
    # se puede pasar True como parametro adicional (se toma como False por defecto)
    def load_config(self, use_gui = False):
        config_path = None
        system_path = "/etc/serialoper/config.json"
        user_path = os.path.expanduser("~/.config/serialoper/config.json")

        if os.path.exists(user_path):
            config_path = user_path
        elif os.path.exists(system_path):
            config_path = system_path
        else:
            config_path = None

        if config_path is None:
            if use_gui is False:
                print("[Config] No se encontró archivo de configuración, usando valores por defecto")
            else:
                self.send_notifications("Error Config","No se encontró archivo de configuración, usando valores por defecto")
            return None
        
        try:
            with open(config_path, "r") as f:
                config_data = json.load(f)
                return config_data

        except Exception as error_exception:
            return None
