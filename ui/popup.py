import pygame
from ui import theme
from ui.scrollbar import Scrollbar


class Popup:
    """
    Popup visual genèric.

    Permet mostrar un missatge multilínia o contingut en dues
    columnes amb desplaçament vertical opcional.
    """

    PADDING_X = 20
    TITLE_HEIGHT = 70
    BOTTOM_PADDING = 20
    COLUMN_GAP = 24
    SCROLLBAR_SIZE = 12

    def __init__(self, screen, width=450, height=320, title=""):
        self.rect = None
        self.screen = screen

        self.width = width
        self.height = height
        self.title = title
        self.message = ""

        self.visible = False

        self.columns = None
        self.scrollbar = None
        self.content_height = 0
        self.scroll = 0

        self.background_color = theme.POPUP_BACKGROUND
        self.border_color = theme.POPUP_BORDER
        self.overlay_color = theme.OVERLAY

        self.font = pygame.font.SysFont(
            theme.FONT_NAME, theme.FONT_SMALL
        )
        self.title_font = pygame.font.SysFont(
            theme.FONT_NAME, theme.FONT_POPUP_TITLE
        )

        self.update_position()

    def update_position(self):
        screen_width, screen_height = self.screen.get_size()

        self.rect = pygame.Rect(
            (screen_width - self.width) // 2,
            (screen_height - self.height) // 2,
            self.width,
            self.height
        )

        self._update_scrollbar()

    def set_message(self, message):
        self.message = str(message)
        self.columns = None
        self.scroll = 0
        self._update_scrollbar()

    def open(self, title=None, message=None):
        """Mode genèric original, compatible amb els altres screens."""
        if title is not None:
            self.title = title

        if message is not None:
            self.set_message(message)

        self.columns = None
        self.scroll = 0
        self.update_position()
        self.visible = True

    def open_columns(self, title, left, right):
        """Obre el popup amb dues columnes independents."""
        self.title = title
        self.message = ""
        self.columns = (str(left), str(right))
        self.scroll = 0

        self.update_position()
        self._update_scrollbar()
        self.visible = True

    def close(self):
        self.visible = False

    def _content_rect(self):
        return pygame.Rect(
            self.rect.x + self.PADDING_X,
            self.rect.y + self.TITLE_HEIGHT,
            self.rect.width - self.PADDING_X * 2,
            self.rect.height - self.TITLE_HEIGHT - self.BOTTOM_PADDING
        )

    def _wrap_text(self, text, max_width):
        words = text.split()
        lines = []
        current_line = ""

        for word in words:
            candidate = f"{current_line} {word}".strip()

            if current_line and self.font.size(candidate)[0] > max_width:
                lines.append(current_line)
                current_line = word
            else:
                current_line = candidate

        if current_line:
            lines.append(current_line)

        return lines

    def _get_lines(self, text, max_width):
        """Conserva les línies en blanc i calcula el text embolicat."""
        lines = []

        for paragraph in text.splitlines():
            wrapped = self._wrap_text(paragraph, max_width)

            if wrapped:
                lines.extend(wrapped)
            else:
                lines.append("")

        return lines

    def _column_width(self):
        content = self._content_rect()
        return max(1, (content.width - self.COLUMN_GAP) // 2)

    def _measure_content_height(self):
        line_height = self.font.get_linesize() + 5

        if self.columns is None:
            lines = self._get_lines(
                self.message,
                self._content_rect().width
            )
            return len(lines) * line_height

        width = self._column_width()
        left_lines = self._get_lines(self.columns[0], width)
        right_lines = self._get_lines(self.columns[1], width)

        return max(len(left_lines), len(right_lines)) * line_height

    def _update_scrollbar(self):
        if self.rect is None:
            return

        content = self._content_rect()
        self.content_height = self._measure_content_height()

        bar_x = self.rect.right - self.PADDING_X - self.SCROLLBAR_SIZE
        bar_y = content.y
        bar_height = content.height

        # Només reservem espai per a la barra si hi ha contingut
        # que no cap a la zona visible.
        if self.content_height > content.height:
            content_width = self.rect.width - self.PADDING_X * 2
            view_width = content_width - self.SCROLLBAR_SIZE - 6

            self.scrollbar = Scrollbar(
                bar_x,
                bar_y,
                self.SCROLLBAR_SIZE,
                bar_height,
                content_height=self.content_height,
                view_height=content.height,
                orientation="vertical"
            )
            self.scrollbar.set_scroll(self.scroll)

            # Guardem l'amplada útil per al dibuix.
            self._visible_content_width = view_width
        else:
            self.scrollbar = None
            self.scroll = 0
            self._visible_content_width = content.width

    def handle_event(self, event):
        if not self.visible:
            return False

        # Si la barra existeix, permetem desplaçar el contingut
        # sense tancar el popup.
        if self.scrollbar is not None:
            if self.scrollbar.handle_event(event, self._content_rect()):
                self.scroll = self.scrollbar.scroll
                return True

            if event.type == pygame.MOUSEWHEEL:
                if self._content_rect().collidepoint(
                    pygame.mouse.get_pos()
                ):
                    self.scrollbar.set_scroll(
                        self.scrollbar.scroll - event.y * 40
                    )
                    self.scroll = self.scrollbar.scroll
                    return True

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.close()
            return True

        if event.type == pygame.MOUSEBUTTONDOWN and event.button in (1, 2, 3):
            # No tanquem si el clic és dins de la finestra del popup.
            # Això permet interactuar amb la barra de desplaçament.
            if self.rect.collidepoint(event.pos):
                return True

            self.close()
            return True

        return False

    def draw_background(self, screen):
        if not self.visible:
            return

        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill(self.overlay_color)
        screen.blit(overlay, (0, 0))

        pygame.draw.rect(
            screen, self.background_color, self.rect,
            border_radius=theme.POPUP_RADIUS
        )
        pygame.draw.rect(
            screen, self.border_color, self.rect,
            width=2, border_radius=theme.POPUP_RADIUS
        )

        title_surface = self.title_font.render(
            self.title, True, theme.TEXT
        )
        screen.blit(
            title_surface,
            (self.rect.x + self.PADDING_X, self.rect.y + 20)
        )

    def _draw_lines(self, screen, text, x, y, max_width, clip_rect):
        line_height = self.font.get_linesize() + 5
        lines = self._get_lines(text, max_width)

        old_clip = screen.get_clip()
        screen.set_clip(clip_rect)

        for line in lines:
            if line:
                surface = self.font.render(
                    line, True, theme.TEXT_SECONDARY
                )
                screen.blit(surface, (x, y - self.scroll))

            y += line_height

        screen.set_clip(old_clip)

    def draw_message(self, screen):
        if not self.visible or not self.message:
            return

        content = self._content_rect()
        width = getattr(self, "_visible_content_width", content.width)

        self._draw_lines(
            screen,
            self.message,
            content.x,
            content.y,
            width,
            content
        )

    def draw_columns(self, screen):
        if not self.visible or self.columns is None:
            return

        content = self._content_rect()
        width = self._column_width()
        gap = self.COLUMN_GAP

        if self.scrollbar is not None:
            width = max(
                1,
                (self._visible_content_width - gap) // 2
            )

        left_rect = pygame.Rect(
            content.x, content.y, width, content.height
        )
        right_rect = pygame.Rect(
            content.x + width + gap,
            content.y,
            width,
            content.height
        )

        self._draw_lines(
            screen, self.columns[0],
            left_rect.x, left_rect.y, left_rect.width, left_rect
        )
        self._draw_lines(
            screen, self.columns[1],
            right_rect.x, right_rect.y, right_rect.width, right_rect
        )

    def draw(self, screen):
        if not self.visible:
            return

        self.draw_background(screen)

        if self.columns is None:
            self.draw_message(screen)
        else:
            self.draw_columns(screen)

        if self.scrollbar is not None:
            self.scrollbar.draw(screen)