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

# Importacion de secciones
from instructions_page import InstructionsPage
from monitor_page import MonitorPage
from websocket_page import WebsocketPage
from service_page import ServicePage

# Application ID
app_id = "xyz.agatinos.serialoper"

class MainWindow(Adw.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Informacion general de la ventana de aplicacion e icono opcional
        self.set_title("Operaciones RS232")
        self.set_default_size(800, 750)
        self.set_icon_name("application-x-firmware")

        # Variables generales

        # Crear overlay split view visible hacia otros metodos por medio de self
        self.split_view = Adw.OverlaySplitView()
        self.split_view.set_max_sidebar_width(280)
        self.split_view.set_show_sidebar(True)

        # Construir el sidebar
        self.side_page = self.sidebar_page()
        self.split_view.set_sidebar(self.side_page)

        # Mostrar un contenido inicial al abrir el programa
        initial_page = InstructionsPage()

        self.split_view.set_content(initial_page)
        self.set_content(self.split_view)

    def sidebar_page(self):
        sidebar_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        sidebar_box.set_vexpand(True)

        sidebar_listbox = Gtk.ListBox()
        sidebar_listbox.add_css_class("navigation-sidebar")
        sidebar_listbox.set_selection_mode(Gtk.SelectionMode.SINGLE)

        # ActionRow para la seccion de Serial Monitor
        monitor_row = Adw.ActionRow()
        monitor_row.set_title("Monitor RS232")
        monitor_icon = Gtk.Image.new_from_icon_name("xsi-network-receive-symbolic")
        monitor_row.add_prefix(monitor_icon)
        sidebar_listbox.append(monitor_row)

        # ActionRow para la seccion de Configuracion de Websocket
        ws_row = Adw.ActionRow()
        ws_row.set_title("Websocket RS232")
        ws_icon = Gtk.Image.new_from_icon_name("xsi-network-wired-symbolic")
        ws_row.add_prefix(ws_icon)
        sidebar_listbox.append(ws_row)

        # ActionRow para la seccion de Configuracion de servicio
        sys_row = Adw.ActionRow()
        sys_row.set_title("Configuracion servicio")
        sys_icon = Gtk.Image.new_from_icon_name("xsi-sharedlib-symbolic")
        sys_row.add_prefix(sys_icon)
        sidebar_listbox.append(sys_row)

        # Manejo de la navegacion por cada ActionRow definido
        def on_row_selected(listbox, row):
            if row == monitor_row:
                self.split_view.set_content(MonitorPage())
            elif row == ws_row:
                self.split_view.set_content(WebsocketPage())
            elif row == sys_row:
                self.split_view.set_content(ServicePage())

        # Conectando la accion de mostrar el menu en base a la seleccion de la fila
        sidebar_listbox.connect("row-selected", on_row_selected)

        # Añadiendo el ListBox creado junto con cada uno de los menus
        sidebar_box.append(sidebar_listbox)

        # Añadiendo la cabecera del menu lateral y las filas del menu
        sidebar_toolbar = Adw.ToolbarView()
        sidebar_toolbar.add_top_bar(Adw.HeaderBar())
        sidebar_toolbar.set_content(sidebar_box)

        self.navigation_sidebar = Adw.NavigationPage()
        self.navigation_sidebar.set_title("Menú")
        self.navigation_sidebar.set_child(sidebar_toolbar)

        return self.navigation_sidebar
    
class MyApp(Adw.Application):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.connect('activate', self.on_activate)

    def on_activate(self, app):
        self.win = MainWindow(application=app)
        self.win.present()

def main():
    app = MyApp(application_id=app_id)
    app.run(None)

if __name__ == "__main__":
    main()
