class BaseScreen:
    """
    Classe base de totes les pantalles del joc.

    Defineix els mètodes que ScreenManager pot cridar.
    Les subclasses els poden sobreescriure.
    """

    def __init__(self, screen_manager, screen, context=None):
        self.sm = screen_manager
        self.screen = screen
        self.game_state = context

    def handle_event(self, event):
        """Processa els esdeveniments de Pygame."""
        pass

    def render(self, screen):
        """Dibuixa la pantalla."""
        pass

    def update(self):
        """Actualitza la lògica de la pantalla."""
        pass

    def on_resize(self, width, height):
        """Actualitza la interfície quan canvia la mida."""
        pass

    def exit_screen(self):
        """Allibera recursos quan se surt de la pantalla."""
        pass