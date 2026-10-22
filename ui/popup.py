import pygame
from ui import theme


class Popup:
    """
    Popup visual genèric.

    No sap res sobre tropes ni GameState.
    """

    def __init__(self, screen, width=450, height=320, title=""):
        self.rect = None
        self.screen = screen

        self.width = width
        self.height = height

        self.title = title

        self.visible = False

        self.background_color = theme.POPUP_BACKGROUND
        self.border_color = theme.POPUP_BORDER
        self.overlay_color = theme.OVERLAY
        self.font = pygame.font.SysFont(theme.FONT_NAME, theme.FONT_BUTTON)
        self.title_font = pygame.font.SysFont(theme.FONT_NAME, theme.FONT_POPUP_TITLE)

        self.update_position()

    def update_position(self):
        screen_width, screen_height = (self.screen.get_size())

        self.rect = pygame.Rect(int((screen_width - self.width) / 2), int((screen_height - self.height) / 2),
                                int(self.width), int(self.height))

    def open(self, title=None):
        if title is not None:
            self.title = title

        self.update_position()
        self.visible = True

    def close(self):
        self.visible = False

    def handle_event(self, event):

        if not self.visible:
            return False

        if event.type == pygame.MOUSEBUTTONDOWN:

            if event.button == 1:

                if not self.rect.collidepoint(event.pos):
                    return False

        return True

    def draw_background(self, screen):
        if not self.visible:
            return

        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)

        overlay.fill(self.overlay_color)

        screen.blit(overlay, (0, 0))

        pygame.draw.rect(screen, self.background_color, self.rect, border_radius=theme.POPUP_RADIUS)

        pygame.draw.rect(screen, self.border_color, self.rect, width=2, border_radius=theme.POPUP_RADIUS)

        title = self.title_font.render(self.title, True, theme.TEXT)

        screen.blit(title, (self.rect.x + 20, self.rect.y + 20))

    def draw(self, screen):
        self.draw_background(screen)
