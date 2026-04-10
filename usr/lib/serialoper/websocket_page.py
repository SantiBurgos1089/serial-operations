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

        # Seccion central donde ira la pagina de preferencias
        self.ws_central_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self.ws_central_box.set_hexpand(True)
        self.ws_central_box.set_vexpand(True)

        # PreferencesPage definition
        self.websocket_page = Adw.PreferencesPage()
        self.websocket_page.set_title("Websocket RS232")

        # Serial port section
        self.serial_group = Adw.PreferencesGroup()
        self.serial_group.set_title("Configuracion puerto serial")
        self.serial_group.set_description("Coloque los parametros para poder leer informacion en base " \
        "al equipo desde el cual desea leer.")

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
        self.websocket_group.set_description("Coloque los parametros adicionales para que el equipo " \
        "funcione como transmision a otros dispositivos.")

        # ComboRow para direccion IP del equipo y como mostrarse
        self.ipport_row = Adw.ComboRow()
        self.ipport_row.set_title("Direccion IP")
        #self.ipport_row.set_subtitle("Seleccione como mostrar su equipo")
        self.local_ip = genset.get_local_ip()
        self.ipport_string_list = Gtk.StringList.new([
            "127.0.0.1",
            self.local_ip,
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
        self.process_button.connect("clicked", self.ws_log_data)
        #self.process_button.connect("clicked", self.ws_toggle_log)
        self.process_row.add_suffix(self.data_label)
        self.process_row.add_suffix(self.process_button)

        # Add row to section
        self.websocket_group.add(self.process_row)

        # Add section with all controls to page
        self.websocket_page.add(self.websocket_group)

        # Añadiendo la seccion de contenido a la seccion central
        self.ws_central_box.append(self.websocket_page)

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

        # 3. Reemplazamos el modelo del ComboRow
        self.rsport_row.set_model(self.ws_port_string_list)

        ## 4. Notificamos al usuario (opcional)
        #genset.send_notifications("Estado", "Lista de puertos actualizada")
        #print("[Sistema] Puertos seriales refrescados."

    def ws_toggle_log(self, button):
        # Cambiamos el estado del estado de logging
        self.logging = not self.logging

        # Obtiene todos los controles creados hasta el momento que puedan ser
        # manipulados por el usuario, otros controles no son considerados
        gtk_controls = [
            self.rsport_row,
            self.baudrate_row,
            self.databits_row,
            self.parity_row,
            self.stopbits_row,
            self.flowcontrol_row,
            self.timeout_row,
            self.ipport_row,
            self.wsport_row
        ]

        for controls in gtk_controls:
            if self.logging:
                self.process_row.set_subtitle("Parar WebSocket")
                button.set_icon_name("xsi-media-playback-stop-symbolic")
                controls.set_sensitive(False)
            else:
                self.process_row.set_subtitle("Iniciar WebSocket")
                button.set_icon_name("xsi-media-playback-start-symbolic")
                controls.set_sensitive(True)

    def update_data_label(self, value):
        self.data_label.set_label(value)

    def ws_log_data(self, button):
        ## Cambiamos el estado del estado de logging
        #self.logging = not self.logging

        # Obtengo el dato seleccionado del ComboRow, para ello realizo lo siguiente
        # Obtengo el numero del elemento seleccionado
        # En base a ese numero, obtengo dicho elemento del StringList como valor
        # Se obtiene un texto de lo seleccionado y se convertira en numerico en la funcion
        rsport_info = self.rsport_row.get_selected()
        rsport_info = self.rsport_string_list.get_string(rsport_info)

        baudrate_info = self.baudrate_row.get_selected()
        baudrate_info = self.baudrate_string_list.get_string(baudrate_info)

        databits_info = self.databits_row.get_selected()
        databits_info = self.databits_string_list.get_string(databits_info)

        parity_info = self.parity_row.get_selected()
        parity_info = self.parity_string_list.get_string(parity_info)

        stopbits_info = self.stopbits_row.get_selected()
        stopbits_info = self.stopbits_string_list.get_string(stopbits_info)

        flowcontrol_info = self.flowcontrol_row.get_selected()
        flowcontrol_info = self.flowcontrol_string_list.get_string(flowcontrol_info)

        timeout_info = self.time_scale.get_value()

        ipport_info = self.ipport_row.get_selected()
        ipport_info = self.ipport_string_list.get_string(ipport_info)

        wsport_info = self.wsport_row.get_selected()
        wsport_info = self.wsport_string_list.get_string(wsport_info)

        # Obtiene todos los controles creados hasta el momento que puedan ser
        # manipulados por el usuario, otros controles no son considerados
        gtk_controls = [
            self.rsport_row,
            self.baudrate_row,
            self.databits_row,
            self.parity_row,
            self.stopbits_row,
            self.flowcontrol_row,
            self.timeout_row,
            self.ipport_row,
            self.wsport_row
        ]

        if not self.logging:
            self.logging = True
            self.process_row.set_subtitle("Parar WebSocket")
            button.set_icon_name("xsi-media-playback-stop-symbolic")
            genset.send_notifications("Estado", "Iniciando Websocket")

            for controls in gtk_controls:
                controls.set_sensitive(False)

            serws.start_serial_monitor(self.update_data_label,
                                       rsport_info,
                                       baudrate_info,
                                       databits_info,
                                       parity_info,
                                       stopbits_info,
                                       flowcontrol_info,
                                       timeout_info,
                                       ipport_info,
                                       wsport_info 
            )
            
        else:
            self.logging = False
            self.process_row.set_subtitle("Iniciar WebSocket")
            self.data_label.set_label("LecturaWS: 0")
            button.set_icon_name("xsi-media-playback-start-symbolic")
            genset.send_notifications("Estado", "Deteniendo Websocket")

            for control in gtk_controls:
                control.set_sensitive(True)

            serws.stop_rs()
