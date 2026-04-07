#!/usr/bin/python3

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk

try:
    # Importing libAdapta first
    gi.require_version('Adap', '1')
    from gi.repository import Adap as Adw
except(ValueError, ImportError):
    # Importing libAdwaita second
    gi.require_version('Adw', '1')
    from gi.repository import Adw

from common.settings_app import GeneralSettings
from common.serial_operations import SerialWebsocket

# Variables adicionales
genset = GeneralSettings()
serws = SerialWebsocket()

# Configuracion de la seccion central donde iran todas las subsecciones
class WebsocketPage(Adw.NavigationPage):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Boton para refrescar puertos disponibles
        self.refresh_ports_button = Gtk.Button()
        self.refresh_ports_button.set_icon_name("xsi-view-refresh-symbolic")
        self.refresh_ports_button.set_tooltip_text("Refrescar puertos disponibles")
        self.refresh_ports_button.connect("clicked", self.sm_refresh_ports)

        self.ws_headerbar = Adw.HeaderBar()
        self.ws_headerbar.pack_start(self.refresh_ports_button)

        self.logging = False

        # Seccion central donde ira cada subseccion
        self.ws_central_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self.ws_central_box.set_hexpand(True)
        self.ws_central_box.set_vexpand(True)

        # Seccion de contenido donde ira cada subseccion
        self.ws_content_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        self.ws_content_box.set_hexpand(True)
        self.ws_content_box.set_vexpand(True)

        # Creando subseccion izquierda
        # Subseccion izquierda con sus controles
        self.ws_leftbox_section = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self.ws_leftbox_section.set_hexpand(True)
        self.ws_leftbox_section.set_vexpand(True)

        # Label para designar seccion de configuracion de puerto RS232
        self.ws_serial_label = Gtk.Label()
        self.ws_serial_label.set_label("Configuracion puerto RS232")

        # Label y DropDown para puertos disponibles
        self.ws_ports_label = Gtk.Label()
        self.ws_ports_label.set_label("Puertos disponibles")
        self.available_ports = genset.get_serial_ports()
        self.ws_port_string_list = Gtk.StringList.new()
        for port in self.available_ports:
            self.ws_port_string_list.append(port)
        self.ws_ports_dropdown = Gtk.DropDown.new(self.ws_port_string_list)

        # Label y DropDown para baudrate
        # Se deja 9600 por defecto por ser el valor mas utilizado en equipos
        self.ws_baudrate_label = Gtk.Label()
        self.ws_baudrate_label.set_label("Baudrate")
        self.ws_baudrate_string_list = Gtk.StringList.new(["100", "300", "600", "1200", "2400", "4800", "9600", "14400",
                     "19200", "38400", "56000", "57600", "115200", "128000", "256000"])
        self.ws_baudrate_dropdown = Gtk.DropDown.new(self.ws_baudrate_string_list)
        self.ws_baudrate_dropdown.set_selected(6)

        # Label y DropDown para data bits
        self.ws_databits_label = Gtk.Label()
        self.ws_databits_label.set_label("Data Bits")
        self.ws_databits_string_list = Gtk.StringList.new(["5", "6", "7", "8"])
        self.ws_databits_dropdown = Gtk.DropDown.new(self.ws_databits_string_list)
        self.ws_databits_dropdown.set_selected(3)

        # Label y DropDown para paridad
        # Se deja "Ninguna" por defecto por ser el valor mas utilizado en equipos
        self.ws_parity_label = Gtk.Label()
        self.ws_parity_label.set_label("Paridad")
        self.ws_parity_string_list = Gtk.StringList.new(["Ninguna", "Par", "Impar", "Espacio", "Marca"])
        self.ws_parity_dropdown = Gtk.DropDown.new(self.ws_parity_string_list)
        self.ws_parity_dropdown.set_selected(0)

        # Label y DropDown para bits de parada
        self.ws_stopbits_label = Gtk.Label()
        self.ws_stopbits_label.set_label("Bit parada")
        self.ws_stopbits_string_list = Gtk.StringList.new(["1", "1.5", "2"])
        self.ws_stopbits_dropdown = Gtk.DropDown.new(self.ws_stopbits_string_list)

        # Label y DropDown para control de flujo
        self.ws_flowcontrol_label = Gtk.Label()
        self.ws_flowcontrol_label.set_label("Control de flujo")
        self.ws_flowcontrol_string_list = Gtk.StringList.new(["Ninguno", "Hardware", "Xon/Xoff"])
        self.ws_flowcontrol_dropdown = Gtk.DropDown.new(self.ws_flowcontrol_string_list)

        # Añadiendo controles a la subseccion izquierda
        self.ws_leftbox_section.append(self.ws_serial_label)
        self.ws_leftbox_section.append(self.ws_ports_label)
        self.ws_leftbox_section.append(self.ws_ports_dropdown)
        self.ws_leftbox_section.append(self.ws_baudrate_label)
        self.ws_leftbox_section.append(self.ws_baudrate_dropdown)
        self.ws_leftbox_section.append(self.ws_databits_label)
        self.ws_leftbox_section.append(self.ws_databits_dropdown)
        self.ws_leftbox_section.append(self.ws_parity_label)
        self.ws_leftbox_section.append(self.ws_parity_dropdown)
        self.ws_leftbox_section.append(self.ws_stopbits_label)
        self.ws_leftbox_section.append(self.ws_stopbits_dropdown)
        self.ws_leftbox_section.append(self.ws_flowcontrol_label)
        self.ws_leftbox_section.append(self.ws_flowcontrol_dropdown)

        # Creando subseccion izquierda
        # Subseccion izquierda con sus controles
        self.ws_rightbox_section = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self.ws_rightbox_section.set_hexpand(True)
        self.ws_rightbox_section.set_vexpand(True)

        # Label para designar seccion de configuracion de puerto RS232
        self.ws_websocket_label = Gtk.Label()
        self.ws_websocket_label.set_label("Configuracion WebSocket")

        # Label y Entry para designar mi direccion IP actual
        self.ws_ip_label = Gtk.Label()
        self.ws_ip_label.set_label("Mi direccion IP actual: ")
        self.ws_ip_entry = Gtk.Entry()
        self.ws_ip_entry.set_sensitive(False)
        self.ws_ip_entry.set_text(genset.get_local_ip())
        #self.ws_ip_entry.set_placeholder_text("127.0.0.1")

        # TODO 1: ¿Considerar un campo de entrada o una lista desplegable?
        # TODO 2: ¿Enviar un dato por defecto para pruebas?
        # Label y DropDown para configuracion de puerto websocket
        self.ws_ipport_label = Gtk.Label()
        self.ws_ipport_label.set_label("Puerto a utilizar WebSocket")
        self.ws_ipport_string_list = Gtk.StringList.new(["5050", "8765", "8080", "9000"])
        self.ws_ipport_dropdown = Gtk.DropDown.new(self.ws_ipport_string_list)

        # Boton para ejecutar el log de datos
        self.ws_data_button = Gtk.Button()
        self.ws_data_button.set_label("Iniciar WebSocket")
        self.ws_data_button.connect("clicked", self.ws_log_data)

        # Label para lectura visual opcional del websocket
        self.ws_data_label = Gtk.Label()
        self.ws_data_label.set_label("Lectura WS: 0")

        # Añadiendo controles a la subseccion derecha
        self.ws_rightbox_section.append(self.ws_websocket_label)
        self.ws_rightbox_section.append(self.ws_ip_label)
        self.ws_rightbox_section.append(self.ws_ip_entry)
        self.ws_rightbox_section.append(self.ws_ipport_label)
        self.ws_rightbox_section.append(self.ws_ipport_dropdown)
        self.ws_rightbox_section.append(self.ws_data_button)
        self.ws_rightbox_section.append(self.ws_data_label)

        # Añadiendo las subsecciones izquierda y derecha a la seccion de contenido
        self.ws_content_box.append(self.ws_leftbox_section)
        self.ws_content_box.append(self.ws_rightbox_section)

        # Añadiendo la seccion de contenido a la seccion central
        self.ws_central_box.append(self.ws_content_box)

        # Añadiendo la cabecera y contenido
        self.ws_toolbar = Adw.ToolbarView()
        self.ws_toolbar.add_top_bar(self.ws_headerbar)
        self.ws_toolbar.set_content(self.ws_central_box)

        self.set_title("Websocket RS232")
        self.set_child(self.ws_toolbar)

    def sm_refresh_ports(self, button):
        # 1. Obtenemos la lista de puertos actualizada
        self.available_ports = genset.get_serial_ports()

        # 2. Creamos un nuevo StringList con los datos frescos
        self.ws_port_string_list = Gtk.StringList.new(self.available_ports)

        # 3. Reemplazamos el modelo del DropDown
        self.ws_ports_dropdown.set_model(self.ws_port_string_list)

        # 4. Si hay puertos disponibles, seleccionamos el primero para evitar que quede en blanco
        if self.available_ports:
            self.ws_ports_dropdown.set_selected(0)

        ## 5. Notificamos al usuario
        #genset.send_notifications("Estado", "Lista de puertos actualizada")
        #print("[Sistema] Puertos seriales refrescados."

    def ws_toggle_log(self, button):
        # Cambiamos el estado del estado de logging
        self.logging = not self.logging

        # Obtiene todos los controles creados hasta el momento que puedan ser
        # manipulados por el usuario, otros controles no son considerados
        gtk_controls = [
            self.ws_ports_dropdown,
            self.ws_ipport_dropdown,
            self.ws_baudrate_dropdown,
            self.ws_databits_dropdown,
            self.ws_parity_dropdown,
            self.ws_stopbits_dropdown,
            self.ws_flowcontrol_dropdown,
            self.refresh_ports_button
        ]

        for control in gtk_controls:
            if self.logging:
                button.set_label("Parar WebSocket")
                control.set_sensitive(False)
            else:
                button.set_label("Iniciar WebSocket")
                control.set_sensitive(True)

    def update_ws_label(self, value):
        self.ws_data_label.set_label(value)

    def ws_log_data(self, button):
        info_rs_port = self.ws_ports_dropdown.get_selected()
        info_rs_port = self.ws_port_string_list.get_string(info_rs_port)

        info_baudrate = self.ws_baudrate_dropdown.get_selected()
        info_baudrate = self.ws_baudrate_string_list.get_string(info_baudrate)

        info_databits = self.ws_databits_dropdown.get_selected()
        info_databits = self.ws_databits_string_list.get_string(info_databits)

        info_parity = self.ws_parity_dropdown.get_selected()
        info_parity = self.ws_parity_string_list.get_string(info_parity)

        info_stopbits = self.ws_stopbits_dropdown.get_selected()
        info_stopbits = self.ws_stopbits_string_list.get_string(info_stopbits)

        info_flowcontrol = self.ws_flowcontrol_dropdown.get_selected()
        info_flowcontrol = self.ws_flowcontrol_string_list.get_string(info_flowcontrol)

        info_ip_port = self.ws_ip_entry.get_text()
        info_ws_port = self.ws_ipport_dropdown.get_selected()
        info_ws_port = int(self.ws_ipport_string_list.get_string(info_ws_port))

                # Obtiene todos los controles creados hasta el momento que puedan ser
        # manipulados por el usuario, otros controles no son considerados
        gtk_controls = [
            self.ws_ports_dropdown,
            self.ws_ipport_dropdown,
            self.ws_baudrate_dropdown,
            self.ws_databits_dropdown,
            self.ws_parity_dropdown,
            self.ws_stopbits_dropdown,
            self.ws_flowcontrol_dropdown,
            self.refresh_ports_button
        ]

        if not self.logging:
            self.logging = True
            button.set_label("Parar WebSocket")
            genset.send_notifications("Estado", "Iniciando Websocket")

            for control in gtk_controls:
                control.set_sensitive(False)

            serws.start_serial_monitor(self.update_ws_label, 
                                       info_rs_port, 
                                       info_baudrate, 
                                       info_databits, 
                                       info_parity, 
                                       info_stopbits, 
                                       info_flowcontrol, 
                                       "Xon/Xoff", 
                                       info_ip_port, 
                                       info_ws_port)
            
        else:
            self.logging = False
            button.set_label("Iniciar WebSocket")
            genset.send_notifications("Estado", "Deteniendo Websocket")

            for control in gtk_controls:
                control.set_sensitive(True)

            serws.stop_rs()
            self.ws_data_label.set_label("LecturaWS: 0")
