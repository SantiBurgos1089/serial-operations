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
