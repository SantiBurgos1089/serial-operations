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

# Configuracion de la seccion central donde iran todas las subsecciones
class InstructionsPage(Adw.NavigationPage):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.ip_headerbar = Adw.HeaderBar()
        self.ip_wintitle = Adw.WindowTitle()
        self.ip_wintitle.set_title("Instrucciones")
        self.ip_wintitle.set_subtitle("Lea detenidamente antes de usar el programa")
        self.ip_headerbar.set_title_widget(self.ip_wintitle)

        # Seccion central donde ira cada subseccion
        self.ip_central_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self.ip_central_box.set_hexpand(True)
        self.ip_central_box.set_vexpand(True)

        # Seccion de contenido donde ira cada subseccion
        self.ip_content_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        self.ip_content_box.set_hexpand(True)
        self.ip_content_box.set_vexpand(True)

        # Subseccion izquierda con sus controles
        self.ip_leftbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self.ip_leftbox.set_hexpand(True)
        self.ip_leftbox.set_vexpand(True)

        # StatusPage para mostrar instrucciones (izquierda)
        self.left_status_page = Adw.StatusPage()
        self.left_status_page.set_title("Seccion Monitor RS232")
        self.left_status_page.set_description("Esta seccion permite realizar pruebas generales con el puerto serial RS232. \n" \
        "Puede configurar los parametros de lectura de su dispositivo serial segun el manual de su fabricante. \n" \
        "Una vez colocado los parametros, hacer clic en el boton de \"Iniciar lectura\" para comenzar a verificar datos")
        self.left_status_page.set_icon_name("xsi-network-symbolic")

        self.ip_leftbox.append(self.left_status_page)

        # Subseccion derecha con sus controles
        self.ip_rightbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self.ip_rightbox.set_hexpand(True)
        self.ip_rightbox.set_vexpand(True)

        # StatusPage para mostrar instrucciones (derecha)
        self.right_status_page = Adw.StatusPage()
        self.right_status_page.set_title("Seccion Websocket RS232")
        self.right_status_page.set_description("Esta seccion permite leer informacion de un puerto serial RS232 y enviarlo a un sitio web. \n" \
        "Puede configurar los parametros de lectura de su dispositivo serial segun el manual de su fabricante, \n" \
        "adicionalmente, debe configurar en su sitio web la direccion IP y el puerto ocupado segun su documentacion o manejo de dicho sitio \n" \
        "Una vez colocado los parametros, hacer clic en el boton de \"Iniciar WebSocket\" para comenzar a leer y enviar los datos respectivos")
        self.right_status_page.set_icon_name("xsi-network-symbolic")

        self.ip_rightbox.append(self.right_status_page)

        # Añadiendo cada subseccion a la seccion de contenido
        self.ip_content_box.append(self.ip_leftbox)
        self.ip_content_box.append(self.ip_rightbox)

        # Añadiendo la seccion de contenido completa
        self.ip_central_box.append(self.ip_content_box)

        # Añadiendo la cabecera y contenido
        self.ip_toolbar = Adw.ToolbarView()
        self.ip_toolbar.add_top_bar(self.ip_headerbar)
        self.ip_toolbar.set_content(self.ip_central_box)

        self.set_title("Instrucciones")
        self.set_child(self.ip_toolbar)
