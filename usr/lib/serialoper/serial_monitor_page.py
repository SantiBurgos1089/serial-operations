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
from common.serial_operations import SerialReader

# Variables adicionales
genset = GeneralSettings()
seroper = SerialReader()

# Configuracion de la seccion central donde iran todas las subsecciones
class SerialMonitorPage(Adw.NavigationPage):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Boton para refrescar puertos disponibles
        self.refresh_ports_button = Gtk.Button()
        self.refresh_ports_button.set_icon_name("xsi-view-refresh-symbolic")
        self.refresh_ports_button.set_tooltip_text("Refrescar puertos disponibles")
        self.refresh_ports_button.connect("clicked", self.sm_refresh_ports)
        
        self.sm_headerbar = Adw.HeaderBar()
        self.sm_headerbar.pack_start(self.refresh_ports_button)

        self.logging = False

        # Seccion central donde ira cada subseccion
        self.sm_central_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self.sm_central_box.set_hexpand(True)
        self.sm_central_box.set_vexpand(True)

        # Seccion de contenido donde ira cada subseccion
        self.sm_content_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        self.sm_content_box.set_hexpand(True)
        self.sm_content_box.set_vexpand(True)

        # Creando subseccion izquierda
        # Subseccion izquierda con sus controles
        self.sm_leftbox_section = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self.sm_leftbox_section.set_hexpand(True)
        self.sm_leftbox_section.set_vexpand(True)

        # TextView para mostrar datos recibidos del puerto serial (izquierda)
        self.sm_data_textview = Gtk.TextView()
        self.sm_data_textview.set_wrap_mode(Gtk.WrapMode.WORD)
        self.sm_data_textview.set_editable(False)
        self.sm_data_textview.set_hexpand(True)
        self.sm_data_textview.set_vexpand(True)

        # ScrolledWindow para que el TextView pueda mostrar barras de desplazamiento
        # al querer mostrar los datos leidos en pantalla
        self.sm_scrollview = Gtk.ScrolledWindow()
        self.sm_scrollview.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.sm_scrollview.set_hexpand(True)
        self.sm_scrollview.set_vexpand(True)
        self.sm_scrollview.set_child(self.sm_data_textview)

        # Label
        self.data_label = Gtk.Label()
        self.data_label.set_label("Lectura")

        # Añadiendo controles a la subseccion
        self.sm_leftbox_section.append(self.data_label)
        self.sm_leftbox_section.append(self.sm_scrollview)
        
        # Creando subseccion derecha
        # Subseccion derecha con sus controles
        self.sm_rightbox_section = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self.sm_rightbox_section.set_hexpand(True)
        self.sm_rightbox_section.set_vexpand(True)

        # Label y DropDown para puertos disponibles
        self.sm_ports_label = Gtk.Label()
        self.sm_ports_label.set_label("Puertos disponibles")
        self.sm_port_string_list = Gtk.StringList.new()
        self.available_ports = genset.get_serial_ports()
        for port in self.available_ports:
            self.sm_port_string_list.append(port)
        self.sm_port_dropdown = Gtk.DropDown.new(self.sm_port_string_list)

        # Label y DropDown para baudrate
        # Se deja 9600 por defecto por ser el valor mas utilizado en equipos
        self.sm_baudrate_label = Gtk.Label()
        self.sm_baudrate_label.set_label("Baudrate")
        self.sm_baudrate_string_list = Gtk.StringList.new(["100", "300", "600", "1200", "2400", "4800", "9600", "14400",
                     "19200", "38400", "56000", "57600", "115200", "128000", "256000"])
        self.sm_baudrate_dropdown = Gtk.DropDown.new(self.sm_baudrate_string_list)
        self.sm_baudrate_dropdown.set_selected(6)

        # Label y DropDown para data bits
        self.sm_databits_label = Gtk.Label()
        self.sm_databits_label.set_label("Data bits")
        self.sm_databits_string_list = Gtk.StringList.new(["5", "6", "7", "8"])
        self.sm_databits_dropdown = Gtk.DropDown.new(self.sm_databits_string_list)
        self.sm_databits_dropdown.set_selected(3)

        # Label y DropDown para paridad
        # Se deja "Ninguna" por defecto por ser el valor mas utilizado en equipos
        self.sm_parity_label = Gtk.Label()
        self.sm_parity_label.set_label("Paridad")
        self.sm_parity_string_list = Gtk.StringList.new(["Ninguna", "Par", "Impar", "Espacio", "Marca"])
        self.sm_parity_dropdown = Gtk.DropDown.new(self.sm_parity_string_list)
        self.sm_parity_dropdown.set_selected(0)

        # Label y DropDown para bits de parada
        self.sm_stopbits_label = Gtk.Label()
        self.sm_stopbits_label.set_label("Bit parada")
        self.sm_stopbits_string_list = Gtk.StringList.new(["1", "1.5", "2"])
        self.sm_stopbits_dropdown = Gtk.DropDown.new(self.sm_stopbits_string_list)

        # Label y DropDown para control de flujo
        # Se deja "Ninguno" por defecto por ser el valor mas utilizado en equipos
        self.sm_flowcontrol_label = Gtk.Label()
        self.sm_flowcontrol_label.set_label("Control de flujo")
        self.sm_flowcontrol_string_list = Gtk.StringList.new(["Ninguno", "Hardware", "Xon/Xoff"])
        self.sm_flowcontrol_dropdown = Gtk.DropDown.new(self.sm_flowcontrol_string_list)
        self.sm_flowcontrol_dropdown.set_selected(0)

        # Boton para iniciar lectura del puerto serial
        self.sm_log_data_button = Gtk.Button()
        self.sm_log_data_button.set_icon_name("xsi-media-playback-start-symbolic")
        self.sm_log_data_button.set_label("Iniciar Log")
        self.sm_log_data_button.connect("clicked", self.sm_log_data)

        # Boton para limpiar TextView
        self.sm_clear_data_button = Gtk.Button()
        self.sm_clear_data_button.set_icon_name("xsi-edit-clear-symbolic")
        self.sm_clear_data_button.set_label("Limpiar lectura")
        self.sm_clear_data_button.connect("clicked", self.sm_clear_data)

        # Añadiendo todos los controles a la subseccion derecha
        self.sm_rightbox_section.append(self.sm_ports_label)
        self.sm_rightbox_section.append(self.sm_port_dropdown)
        self.sm_rightbox_section.append(self.sm_baudrate_label)
        self.sm_rightbox_section.append(self.sm_baudrate_dropdown)
        self.sm_rightbox_section.append(self.sm_databits_label)
        self.sm_rightbox_section.append(self.sm_databits_dropdown)
        self.sm_rightbox_section.append(self.sm_parity_label)
        self.sm_rightbox_section.append(self.sm_parity_dropdown)
        self.sm_rightbox_section.append(self.sm_stopbits_label)
        self.sm_rightbox_section.append(self.sm_stopbits_dropdown)
        self.sm_rightbox_section.append(self.sm_flowcontrol_label)
        self.sm_rightbox_section.append(self.sm_flowcontrol_dropdown)
        self.sm_rightbox_section.append(self.sm_log_data_button)
        self.sm_rightbox_section.append(self.sm_clear_data_button)

        # Añadiendo las subsecciones izquierda y derecha a la seccion de contenido
        self.sm_content_box.append(self.sm_leftbox_section)
        self.sm_content_box.append(self.sm_rightbox_section)

        # Añadiendo la seccion de contenido al contenido principal
        self.sm_central_box.append(self.sm_content_box)

        # Añadiendo la cabecera y contenido
        self.sm_toolbar = Adw.ToolbarView()
        self.sm_toolbar.add_top_bar(self.sm_headerbar)
        self.sm_toolbar.set_content(self.sm_central_box)

        self.set_title("Monitor RS232")
        self.set_child(self.sm_toolbar)

    def sm_refresh_ports(self, button):
        # 1. Obtenemos la lista de puertos actualizada
        self.available_ports = genset.get_serial_ports()

        # 2. Creamos un nuevo StringList con los datos frescos
        self.sm_port_string_list = Gtk.StringList.new(self.available_ports)

        # 3. Reemplazamos el modelo del DropDown
        self.sm_port_dropdown.set_model(self.sm_port_string_list)

        # 4. Si hay puertos disponibles, seleccionamos el primero para evitar que quede en blanco
        if self.available_ports:
            self.sm_port_dropdown.set_selected(0)

        ## 5. Notificamos al usuario
        #genset.send_notifications("Estado", "Lista de puertos actualizada")
        #print("[Sistema] Puertos seriales refrescados."

    def sm_toggle_log(self, button):
        # Cambiamos el estado del estado de logging
        self.logging = not self.logging

        # Obtiene todos los controles creados hasta el momento que puedan ser
        # manipulados por el usuario, otros controles no son considerados
        gtk_controls = [
            self.refresh_ports_button,
            self.sm_port_dropdown,
            self.sm_baudrate_dropdown,
            self.sm_databits_dropdown,
            self.sm_parity_dropdown,
            self.sm_stopbits_dropdown,
            self.sm_flowcontrol_dropdown,
            self.sm_clear_data_button

        ]

        for control in gtk_controls:
            if self.logging:
                button.set_label("Parar Log")
                control.set_sensitive(False)
            else:
                button.set_label("Iniciar Log")
                control.set_sensitive(True)

    def sm_log_data (self, button):
        info_ports = self.sm_port_dropdown.get_selected()
        info_ports = self.sm_port_string_list.get_string(info_ports)

        info_baudrate = self.sm_baudrate_dropdown.get_selected()
        info_baudrate = self.sm_baudrate_string_list.get_string(info_baudrate)

        info_databits = self.sm_databits_dropdown.get_selected()
        info_databits = self.sm_databits_string_list.get_string(info_databits)

        info_parity = self.sm_parity_dropdown.get_selected()
        info_parity = self.sm_parity_string_list.get_string(info_parity)

        info_stopbits = self.sm_stopbits_dropdown.get_selected()
        info_stopbits = self.sm_stopbits_string_list.get_string(info_stopbits)

        info_flowcontrol = self.sm_flowcontrol_dropdown.get_selected()
        info_flowcontrol = self.sm_flowcontrol_string_list.get_string(info_flowcontrol)

        # Obtiene todos los controles creados hasta el momento que puedan ser
        # manipulados por el usuario, otros controles no son considerados
        gtk_controls = [
            self.refresh_ports_button,
            self.sm_port_dropdown,
            self.sm_baudrate_dropdown,
            self.sm_databits_dropdown,
            self.sm_parity_dropdown,
            self.sm_stopbits_dropdown,
            self.sm_flowcontrol_dropdown,
            self.sm_clear_data_button

        ]

        if not self.logging:
            self.logging = True
            button.set_label("Parar Log")
            genset.send_notifications("Estado", "Iniciando log...")

            for control in gtk_controls:
                control.set_sensitive(False)

            seroper.logs_serial_monitor(self.show_in_textview, 
                                        info_ports, 
                                        info_baudrate, 
                                        info_databits, 
                                        info_parity, 
                                        info_stopbits, 
                                        info_flowcontrol,
                                        "Xon/Xoff")
            
        else:
            self.logging = False
            button.set_label("Iniciar Log")
            genset.send_notifications("Estado", "Deteniendo log")

            for control in gtk_controls:
                control.set_sensitive(True)

            seroper.stop_read_serial()
            
    def show_in_textview(self, text):
        buffer = self.sm_data_textview.get_buffer()
        buffer.insert(buffer.get_end_iter(), text + "\n")

    def sm_clear_data(self, widget):
        buffer = self.sm_data_textview.get_buffer()
        buffer.set_text("")
        genset.send_notifications("Estado", "Limpiando datos")