import pygame

from ui import theme


class Box:

    def __init__(self, x, y, w, h):
        self.rect = pygame.Rect(x, y, w, h)

    def draw(self, screen, color=None):

        if color is None:
            color = theme.SURFACE

        pygame.draw.rect(
            screen,
            color,
            self.rect,
            border_radius=theme.BORDER_RADIUS
        )

        pygame.draw.rect(
            screen,
            theme.BORDER,
            self.rect,
            theme.BORDER_WIDTH,
            border_radius=theme.BORDER_RADIUS
        )
