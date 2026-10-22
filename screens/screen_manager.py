import pygame


class ScreenManager:
    def __init__(self, screen):
        self.screen = screen
        self.width, self.height = self.screen.get_size()

        self.current_screen = None
        self.current_screen_name = None

        self.SCREEN_REGISTRY = {}

    def register(self, name, screen_class):
        self.SCREEN_REGISTRY[name] = screen_class

    def change_screen(self, name, context=None):

        if name not in self.SCREEN_REGISTRY:
            raise ValueError(f"Screen '{name}' no existeix")

        # exit screen actual
        if self.current_screen and hasattr(self.current_screen, "exit_screen"):
            self.current_screen.exit_screen()

        self.current_screen_name = name

        cls = self.SCREEN_REGISTRY[name]
        self.current_screen = cls(self, self.screen, context or {})

    def update(self, events):
        for event in events:

            if event.type == pygame.VIDEORESIZE:
                self.handle_resize(event.w, event.h)

            if self.current_screen and hasattr(self.current_screen, "handle_event"):
                self.current_screen.handle_event(event)

        if self.current_screen and hasattr(self.current_screen, "update"):
            self.current_screen.update()

    def draw(self):
        if self.current_screen:
            self.current_screen.render(self.screen)

    def handle_resize(self, w, h):
        self.width = w
        self.height = h

        self.screen = pygame.display.set_mode((w, h), self.screen.get_flags())

        if self.current_screen and hasattr(self.current_screen, "on_resize"):
            self.current_screen.on_resize(w, h)
