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

import common.serial_operations
import common.settings_app

# Variables adicionales
genset = common.settings_app.GeneralSettings()
serws = common.serial_operations.SerialWebsocket()

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

        # Seccion central donde ira cada grupo
        self.ws_central_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self.ws_central_box.set_hexpand(True)
        self.ws_central_box.set_vexpand(True)

        # PreferencesPage definition
        self.websocket_page = Adw.PreferencesPage()
        self.websocket_page.set_title("Websocket RS232")

        # Serial port section
        self.serial_group = Adw.PreferencesGroup()
        self.serial_group.set_title("Configuracion puerto serial")

        # ComboRow para puertos disponibles
        self.rsport_row = Adw.ComboRow()
        self.rsport_row.set_title("Puertos disponibles")
        self.rsport_row.set_subtitle("Seleccione puerto del listado")
        self.available_ports = genset.get_serial_ports()
        self.rsport_string_list = Gtk.StringList.new()
        for port in self.available_ports:
            self.rsport_string_list.append(port)
        self.rsport_row.set_model(self.rsport_string_list)

        # Add row to section
        self.serial_group.add(self.rsport_row)

        # ComboRow para baudrate
        # Se deja 9600 por defecto por ser el valor mas utilizado en equipos
        self.baudrate_row = Adw.ComboRow()
        self.baudrate_row.set_title("Baudrate")
        self.baudrate_row.set_subtitle("Si no conoce valor puede dejar el valor 9600")
        self.baudrate_string_list = Gtk.StringList.new()
        for baudrate in common.serial_operations.BAUDRATE:
            self.baudrate_string_list.append(baudrate)
        self.baudrate_row.set_model(self.baudrate_string_list)
        self.baudrate_row.set_selected(6)

        # Add row to section
        self.serial_group.add(self.baudrate_row)

        # ComboRow para data bits
        self.databits_row = Adw.ComboRow()
        self.databits_row.set_title("Data bits")
        self.databits_row.set_subtitle("Si no conoce valor puede dejar el valor 8")
        self.databits_string_list = Gtk.StringList.new()
        for databits in common.serial_operations.DATA_BITS:
            self.databits_string_list.append(databits)
        self.databits_row.set_model(self.databits_string_list)
        self.databits_row.set_selected(3)

        # Add row to section
        self.serial_group.add(self.databits_row)

        # ComboRow para paridad
        self.parity_row = Adw.ComboRow()
        self.parity_row.set_title("Paridad")
        self.parity_string_list = Gtk.StringList.new()
        for parity in common.serial_operations.PARITY:
            self.parity_string_list.append(parity)
        self.parity_row.set_model(self.databits_string_list)

        # Add row to section
        self.serial_group.add(self.parity_row)

        # ComboRow para bits de parada
        self.stopbits_row = Adw.ComboRow()
        self.stopbits_row.set_title("Bit de parada")
        self.stopbits_string_list = Gtk.StringList.new()
        for stopbits in common.serial_operations.STOP_BITS:
            self.stopbits_string_list.append(stopbits)
        self.stopbits_row.set_model(self.stopbits_string_list)

        # Add row to section
        self.serial_group.add(self.stopbits_row)

        # ComboRow para control de flujo
        self.flowcontrol_row = Adw.ComboRow()
        self.flowcontrol_row.set_title("Control de flujo")
        self.flowcontrol_string_list = Gtk.StringList.new()
        for flowcontrol in common.serial_operations.FLOW_CONTROL:
            self.flowcontrol_string_list.append(flowcontrol)
        self.flowcontrol_row.set_model(self.flowcontrol_string_list)

        # Add row to section
        self.serial_group.add(self.flowcontrol_row)

        # Row para timeout
        self.timeout_row = Adw.ActionRow()
        self.timeout_row.set_title("Timeout")
        self.timeout_row.set_subtitle("Tiempo de espera en segundos")
        self.time_scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0.0, 5.0, 0.5)
        self.time_scale.set_value(1)
        self.time_scale.set_hexpand(True)
        self.time_scale.set_draw_value(True)
        self.timeout_row.add_suffix(self.time_scale)

        # Add row to section
        self.serial_group.add(self.timeout_row)

        # Add section with all controls to page
        self.websocket_page.add(self.serial_group)






        # Websocket section
        self.websocket_group = Adw.PreferencesGroup()
        self.websocket_group.set_title("Configuracion Websocket")

        # ComboRow para direccion IP del equipo y como mostrarse
        self.ipport_row = Adw.ComboRow()
        self.ipport_row.set_title("Direccion IP")
        #self.ipport_row.set_subtitle("Seleccione como mostrar su equipo")
        self.local_ip = genset.get_local_ip()
        self.ipport_string_list = Gtk.StringList.new([
            self.local_ip, 
            "127.0.0.1", 
            "0.0.0.0"])
        self.ipport_row.set_model(self.ipport_string_list)

        # Add row to section
        self.websocket_group.add(self.ipport_row)

        # ComboRow para puerto de red del websocket a configurar
        self.wsport_row = Adw.ComboRow()
        self.wsport_row.set_title("Puerto de red a utilizar WebSocket")
        self.wsport_string_list = Gtk.StringList.new()
        for wsport in common.serial_operations.WEBSOCKET_PORT:
            self.wsport_string_list.append(wsport)
        self.wsport_row.set_model(self.wsport_string_list)
        self.wsport_row.set_selected(0)

        # Add row to section
        self.websocket_group.add(self.wsport_row)

        # Row para proceso de inicio websocket
        self.process_row = Adw.ActionRow()
        self.process_row.set_title("Gestiona el inicio y finalizacion del websocket")
        self.process_row.set_subtitle("Iniciar WebSocket")
        self.data_label = Gtk.Label()
        self.data_label.set_label("Lectura WS: 0")
        self.process_button = Gtk.Button()
        #self.process_button.set_label("Iniciar WebSocket")
        self.process_button.set_icon_name("xsi-media-playback-start-symbolic")
        #self.process_button.connect("clicked", self.ws_log_data)
        self.process_row.add_suffix(self.data_label)
        self.process_row.add_suffix(self.process_button)

        # Add row to section
        self.websocket_group.add(self.process_row)

        # Add section with all controls to page
        self.websocket_page.add(self.websocket_group)










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
        self.ws_central_box.append(self.websocket_page)
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
