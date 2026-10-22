import pygame
from ui import theme


class Button:

    def __init__(
        self,
        x, y, w, h,
        text,
        callback,
        enabled=True,
        color=None,
        disabled_color=None,
        text_color=None,
        disabled_text_color=None,
        border_color=None,
        disabled_border_color=None,
        hover_color=None
    ):
        self.rect = pygame.Rect(x, y, w, h)

        self.text = text
        self.callback = callback
        self.enabled = enabled

        # Colors del tema per defecte
        self.color = (
            theme.BUTTON_NORMAL if color is None else color
        )
        self.hover_color = (
            theme.BUTTON_HOVER if hover_color is None else hover_color
        )
        self.disabled_color = (
            theme.BUTTON_DISABLED
            if disabled_color is None else disabled_color
        )

        self.text_color = (
            theme.TEXT if text_color is None else text_color
        )
        self.disabled_text_color = (
            theme.TEXT_DISABLED
            if disabled_text_color is None else disabled_text_color
        )

        self.border_color = (
            theme.BUTTON_BORDER
            if border_color is None else border_color
        )
        self.disabled_border_color = (
            theme.BUTTON_DISABLED_BORDER
            if disabled_border_color is None else disabled_border_color
        )

        self.font = pygame.font.SysFont(
            theme.FONT_NAME, theme.FONT_BUTTON
        )

    def draw(self, screen):

        if not self.enabled:
            color = self.disabled_color
            text_color = self.disabled_text_color
            border_color = self.disabled_border_color

        else:
            text_color = self.text_color
            border_color = self.border_color

            if self.rect.collidepoint(pygame.mouse.get_pos()):
                color = self.hover_color
            else:
                color = self.color

        pygame.draw.rect(
            screen,
            color,
            self.rect,
            border_radius=theme.BORDER_RADIUS
        )

        pygame.draw.rect(
            screen,
            border_color,
            self.rect,
            theme.BORDER_WIDTH,
            border_radius=theme.BORDER_RADIUS
        )

        txt = self.font.render(
            self.text,
            True,
            text_color
        )

        text_rect = txt.get_rect(center=self.rect.center)
        screen.blit(txt, text_rect)

    def handle_event(self, event):

        if not self.enabled:
            return False

        if event.type == pygame.MOUSEBUTTONDOWN:

            if event.button == 1 and self.rect.collidepoint(event.pos):
                self.callback()
                return True

        return False
