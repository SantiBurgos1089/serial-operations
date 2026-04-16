import json
import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Gio, GLib

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

# Configuracion de la seccion central donde iran todas las subsecciones
class ServicePage(Adw.NavigationPage):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Boton para refrescar puertos disponibles
        self.refresh_ports_button = Gtk.Button()
        self.refresh_ports_button.set_icon_name("xsi-view-refresh-symbolic")
        self.refresh_ports_button.set_tooltip_text("Refrescar puertos disponibles")
        self.refresh_ports_button.connect("clicked", self.sm_refresh_ports)

        self.ws_headerbar = Adw.HeaderBar()
        self.ws_headerbar.pack_start(self.refresh_ports_button)

        # Seccion central donde ira la pagina de preferencias
        self.ws_central_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self.ws_central_box.set_hexpand(True)
        self.ws_central_box.set_vexpand(True)

        # PreferencesPage definition
        self.service_page = Adw.PreferencesPage()
        self.service_page.set_title("Configuracion para servicio sistema")

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
        self.parity_row.set_model(self.parity_string_list)

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
        self.service_page.add(self.serial_group)


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

        # Add section with all controls to page
        self.service_page.add(self.websocket_group)


        # Service section
        self.service_group = Adw.PreferencesGroup()
        self.service_group.set_title("Configuracion para el servicio systemd")
        self.service_group.set_description("Se exportaran los parametros colocados en las secciones " \
        "de puerto serial y websocket para ser utilizados por el servicio de systemd correspondiente.")

        # Row para exportar configuracion
        self.export_row = Adw.ActionRow()
        self.export_row.set_title("Exportar configuracion actual")
        self.export_row.set_subtitle("Exporta o sobreescribe la configuracion actual" \
        " a un archivo json")
        self.export_button = Gtk.Button()
        self.export_button.set_icon_name("xsi-document-save-as-symbolic")
        self.export_button.connect("clicked", self.export_conf)
        self.export_row.add_suffix(self.export_button)

        # Add row to section
        self.service_group.add(self.export_row)

        ## Row para importar configuracion
        #self.import_row = Adw.ActionRow()
        #self.import_row.set_title("Importar configuracion actual")
        #self.import_row.set_subtitle("Importa configuracion desde un archivo json")
        #self.import_button = Gtk.Button()
        #self.import_button.set_icon_name("xsi-document-open-symbolic")
        #self.import_button.connect("clicked", self.import_conf)
        #self.import_row.add_suffix(self.import_button)

        ## Add row to section
        #self.service_group.add(self.import_row)

        # Add section with all controls to page
        self.service_page.add(self.service_group)

        # Añadiendo la seccion de contenido a la seccion central
        self.ws_central_box.append(self.service_page)

        # Añadiendo la cabecera y contenido
        self.ws_toolbar = Adw.ToolbarView()
        self.ws_toolbar.add_top_bar(self.ws_headerbar)
        self.ws_toolbar.set_content(self.ws_central_box)

        self.set_title("Configuracion para servicio sistema")
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

    def export_conf(self, button):
        # Obtengo el dato seleccionado del ComboRow, para ello realizo lo siguiente
        # Obtengo el numero del elemento seleccionado
        # En base a ese numero, obtengo dicho elemento del StringList como valor
        # Todo esto recopila la informacion necesaria para el archivo json posterior
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

        # Recopilamos la informacion necesaria para el archivo json en base a lo anterior
        self.json_config_data = {
            "serial":{
                "serial_port": rsport_info,
                "baudrate": int(baudrate_info),
                "databits": databits_info,
                "parity": parity_info,
                "stopbits": stopbits_info,
                "flowcontrol": flowcontrol_info,
                "timeout": float(timeout_info)
            },
            "websocket": {
                "ip_port": ipport_info,
                "ws_port": int(wsport_info)
            }
        }

        # Configuramos el dialogo para guardar en una ruta
        save_dialog = Gtk.FileDialog.new()
        save_dialog.set_title("Guardar configuración actual como...")
        save_dialog.set_initial_name("serial_ws_config.json") # Nombre sugerido por defecto

        # Filtro para sugiera .json como extension
        file_filter = Gtk.FileFilter()
        file_filter.set_name("Archivos JSON")
        file_filter.add_pattern("*.json")

        filter_ls = Gio.ListStore.new(Gtk.FileFilter)
        filter_ls.append(file_filter)
        save_dialog.set_filters(filter_ls)

        # Abrimos el dialogo de forma asincrona
        save_window = self.get_root()
        save_dialog.save(save_window, None, self.export_is_ready)

    def export_is_ready(self, dialog, result):
        try:
            # Obtiene el objeto Gio.File seleccionado por el usuario
            file = dialog.save_finish(result)

            if file is not None:
                save_path = file.get_path()

                # Si el usuario no le puso extensión .json, se la agregamos por seguridad
                if not save_path.endswith('.json'):
                    save_path += '.json'

                with open(save_path, "w") as json_file:
                    json.dump(self.json_config_data, json_file, indent=4)

                genset.send_notifications("Finalizado", f"Configuración exportada a {file.get_basename()}")
                #print(f"[Sistema] Archivo exportado correctamente en: {save_path}")

        # El usuario canceló o cerró la ventana de guardado
        except GLib.Error:
            #print("[Sistema] Operación de exportación cancelada por el usuario.")
            pass

        except Exception as error_exception:
            genset.send_notifications("Error", f"No se pudo guardar: {error_exception}", "xsi-dialog-error-symbolic")
            #print(f"[Error Exportación] {error_exception}")
