import pygame
from ui import theme


class Scrollbar:
    def __init__(
        self, x, y, width, height,
        content_height=0, view_height=None,
        orientation="vertical"
    ):
        self.rect = pygame.Rect(int(x), int(y), int(width), int(height))
        self.orientation = orientation

        self.content_height = max(0, int(content_height))
        self.view_height = max(
            0, int(height if view_height is None else view_height)
        )

        self.scroll = 0
        self.dragging = False
        self.drag_offset = 0

        self.track_color = theme.SURFACE
        self.thumb_color = theme.SECONDARY
        self.thumb_hover_color = theme.SECONDARY_HOVER

        self.min_thumb_size = min(
            28,
            self.rect.width if orientation == "horizontal"
            else self.rect.height
        )

    @property
    def max_scroll(self):
        return max(0, self.content_height - self.view_height)

    def set_metrics(self, content_height, view_height=None):
        self.content_height = max(0, int(content_height))

        if view_height is not None:
            self.view_height = max(0, int(view_height))

        self.scroll = min(self.scroll, self.max_scroll)

    def set_scroll(self, value):
        self.scroll = max(0, min(int(value), self.max_scroll))

    def get_thumb_rect(self):
        horizontal = self.orientation == "horizontal"
        track_size = self.rect.width if horizontal else self.rect.height

        if self.max_scroll <= 0 or track_size <= 0:
            return self.rect.copy()

        ratio = min(1.0, self.view_height / max(1, self.content_height))
        thumb_size = max(self.min_thumb_size, int(track_size * ratio))
        thumb_size = min(track_size, thumb_size)

        travel = track_size - thumb_size
        offset = round(travel * self.scroll / self.max_scroll)

        if horizontal:
            return pygame.Rect(
                self.rect.x + offset, self.rect.y,
                thumb_size, self.rect.height
            )

        return pygame.Rect(
            self.rect.x, self.rect.y + offset,
            self.rect.width, thumb_size
        )

    def handle_event(self, event, viewport=None):
        horizontal = self.orientation == "horizontal"

        if event.type == pygame.MOUSEWHEEL:
            if viewport is not None and not viewport.collidepoint(
                pygame.mouse.get_pos()
            ):
                return False

            if self.max_scroll <= 0:
                return False

            old_scroll = self.scroll
            self.set_scroll(self.scroll - event.y * 40)
            return old_scroll != self.scroll

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if not self.rect.collidepoint(event.pos):
                return False

            if self.max_scroll <= 0:
                return True

            thumb = self.get_thumb_rect()
            mouse_axis = event.pos[0] if horizontal else event.pos[1]
            thumb_start = thumb.x if horizontal else thumb.y
            thumb_end = thumb.right if horizontal else thumb.bottom

            if thumb.collidepoint(event.pos):
                self.dragging = True
                self.drag_offset = mouse_axis - thumb_start
            else:
                direction = -1 if mouse_axis < thumb_start else 1
                self.set_scroll(self.scroll + direction * self.view_height)

                thumb = self.get_thumb_rect()
                if thumb.collidepoint(event.pos):
                    self.dragging = True
                    self.drag_offset = mouse_axis - (
                        thumb.x if horizontal else thumb.y
                    )

            return True

        if event.type == pygame.MOUSEMOTION and self.dragging:
            thumb = self.get_thumb_rect()

            if horizontal:
                travel = self.rect.width - thumb.width
                new_pos = event.pos[0] - self.drag_offset - self.rect.x
            else:
                travel = self.rect.height - thumb.height
                new_pos = event.pos[1] - self.drag_offset - self.rect.y

            if travel > 0:
                self.set_scroll(round(new_pos / travel * self.max_scroll))

            return True

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            was_dragging = self.dragging
            self.dragging = False
            return was_dragging

        return False

    def draw(self, screen):
        if self.max_scroll <= 0:
            return

        pygame.draw.rect(
            screen, self.track_color, self.rect, border_radius=4
        )

        thumb = self.get_thumb_rect()
        color = (
            self.thumb_hover_color
            if thumb.collidepoint(pygame.mouse.get_pos()) or self.dragging
            else self.thumb_color
        )

        pygame.draw.rect(screen, color, thumb, border_radius=4)