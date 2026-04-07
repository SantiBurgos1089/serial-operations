import gi
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
