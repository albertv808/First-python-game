import pygame
from ui.scrollbar import Scrollbar


class Grid:
    """
    Graella amb mida mínima de casella i desplaçament horitzontal/vertical.
    width i height són el nombre de columnes i files.
    """

    SCROLLBAR_SIZE = 12

    def __init__(
        self, x, y, width, height, cell_size,
        background_color=(60, 60, 65),
        line_color=(20, 20, 20),
        viewport=None
    ):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.cell_size = cell_size

        self.background_color = background_color
        self.line_color = line_color
        self.highlighted_cells = {}

        self.viewport_rect = pygame.Rect(
            int(x), int(y),
            int(width * cell_size),
            int(height * cell_size)
        ) if viewport is None else pygame.Rect(viewport)

        self.horizontal_scrollbar = None
        self.vertical_scrollbar = None
        self.content_rect = self.viewport_rect.copy()

        self._update_scrollbars()

    @property
    def content_width(self):
        return self.width * self.cell_size

    @property
    def content_height(self):
        return self.height * self.cell_size

    @property
    def scroll_x(self):
        if self.horizontal_scrollbar is None:
            return 0
        return self.horizontal_scrollbar.scroll

    @property
    def scroll_y(self):
        if self.vertical_scrollbar is None:
            return 0
        return self.vertical_scrollbar.scroll

    def set_viewport(self, viewport):
        self.viewport_rect = pygame.Rect(viewport)
        self.x = self.viewport_rect.x
        self.y = self.viewport_rect.y
        self._update_scrollbars()

    def set_geometry(self, x, y, width, height, cell_size):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.cell_size = cell_size

        self.viewport_rect.topleft = (int(x), int(y))
        self._update_scrollbars()

    def _update_scrollbars(self):
        bar = self.SCROLLBAR_SIZE
        vw = self.viewport_rect.width
        vh = self.viewport_rect.height

        # Comprovem si cal reservar espai per a cada barra.
        need_h = self.content_width > vw
        need_v = self.content_height > vh

        for _ in range(2):
            view_w = max(0, vw - (bar if need_v else 0))
            view_h = max(0, vh - (bar if need_h else 0))

            need_h = self.content_width > view_w
            need_v = self.content_height > view_h

        view_w = max(0, vw - (bar if need_v else 0))
        view_h = max(0, vh - (bar if need_h else 0))

        self.content_rect = pygame.Rect(
            self.viewport_rect.x,
            self.viewport_rect.y,
            view_w,
            view_h
        )

        if need_h:
            self.horizontal_scrollbar = Scrollbar(
                self.viewport_rect.x,
                self.viewport_rect.bottom - bar,
                view_w,
                bar,
                content_height=self.content_width,
                view_height=view_w,
                orientation="horizontal"
            )
        else:
            self.horizontal_scrollbar = None

        if need_v:
            self.vertical_scrollbar = Scrollbar(
                self.viewport_rect.right - bar,
                self.viewport_rect.y,
                bar,
                view_h,
                content_height=self.content_height,
                view_height=view_h,
                orientation="vertical"
            )
        else:
            self.vertical_scrollbar = None

    def get_rect(self):
        return self.content_rect.copy()

    def get_cell_rect(self, x, y):
        return pygame.Rect(
            round(self.content_rect.x + x * self.cell_size - self.scroll_x),
            round(self.content_rect.y + y * self.cell_size - self.scroll_y),
            round(self.cell_size),
            round(self.cell_size)
        )

    def get_cell_at(self, mouse_pos):
        if not self.content_rect.collidepoint(mouse_pos):
            return None

        mx, my = mouse_pos

        x = int((mx - self.content_rect.x + self.scroll_x) / self.cell_size)
        y = int((my - self.content_rect.y + self.scroll_y) / self.cell_size)

        if 0 <= x < self.width and 0 <= y < self.height:
            return x, y

        return None

    def handle_event(self, event):
        handled = False

        # La roda del ratolí desplaça el tauler verticalment.
        if event.type == pygame.MOUSEWHEEL:
            mouse_pos = pygame.mouse.get_pos()

            if self.content_rect.collidepoint(mouse_pos):
                if self.vertical_scrollbar is not None:
                    old = self.vertical_scrollbar.scroll
                    self.vertical_scrollbar.set_scroll(
                        old - event.y * 40
                    )
                    handled = old != self.vertical_scrollbar.scroll

                return handled

        for scrollbar in (
            self.horizontal_scrollbar,
            self.vertical_scrollbar
        ):
            if scrollbar is not None:
                if scrollbar.handle_event(event, self.viewport_rect):
                    handled = True

        return handled

    def set_cell_color(self, x, y, color):
        self.highlighted_cells[(x, y)] = color

    def clear_cell_colors(self):
        self.highlighted_cells.clear()

    def draw(self, screen):
        old_clip = screen.get_clip()
        screen.set_clip(self.content_rect)

        screen.fill(self.background_color, self.content_rect)

        for y in range(self.height):
            for x in range(self.width):
                rect = self.get_cell_rect(x, y)

                if not self.content_rect.colliderect(rect):
                    continue

                color = self.highlighted_cells.get(
                    (x, y), self.background_color
                )

                pygame.draw.rect(screen, color, rect)
                pygame.draw.rect(screen, self.line_color, rect, 1)

        screen.set_clip(old_clip)
        self.draw_scrollbars(screen)

    def draw_scrollbars(self, screen):
        if self.horizontal_scrollbar is not None:
            self.horizontal_scrollbar.draw(screen)

        if self.vertical_scrollbar is not None:
            self.vertical_scrollbar.draw(screen)