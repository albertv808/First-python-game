import pygame
from ui import theme


class Slider:

    def __init__(self, x, y, width, minimum=0, maximum=100, value=0, height=8):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        self.minimum = minimum
        self.maximum = maximum

        self.value = 0

        self.dragging = False

        self.background_color = theme.SLIDER_BACKGROUND
        self.fill_color = theme.SLIDER_FILL
        self.knob_color = theme.SLIDER_KNOB

        self.set_value(value)

    def set_value(self, value):

        try:
            value = int(value)
        except (ValueError, TypeError):
            value = self.minimum

        value = max(self.minimum, value)

        value = min(self.maximum, value)

        self.value = value

    def get_ratio(self):

        if self.maximum <= self.minimum:
            return 0.0

        return (self.value - self.minimum) / (self.maximum - self.minimum)

    def get_rect(self):

        return pygame.Rect(int(self.x), int(self.y), int(self.width), int(self.height))

    def get_knob_x(self):

        return int(self.x + self.width * self.get_ratio())

    def get_value_at_x(self, mouse_x):

        if self.width <= 0:
            return self.minimum

        ratio = (mouse_x - self.x) / self.width

        ratio = max(0.0, min(1.0, ratio))

        value = (self.minimum + (self.maximum - self.minimum) * ratio)

        return int(round(value))

    def handle_event(self, event):

        # ----------------------------------------------
        # CLICK
        # ----------------------------------------------

        if event.type == pygame.MOUSEBUTTONDOWN:

            if event.button == 1:

                hit_rect = (self.get_rect().inflate(0, 30))

                if hit_rect.collidepoint(event.pos):
                    self.dragging = True

                    self.set_value(self.get_value_at_x(event.pos[0]))

                    return True

        # ----------------------------------------------
        # DRAG
        # ----------------------------------------------

        elif event.type == pygame.MOUSEMOTION:

            if self.dragging:
                self.set_value(self.get_value_at_x(event.pos[0]))

                return True

        # ----------------------------------------------
        # RELEASE
        # ----------------------------------------------

        elif event.type == pygame.MOUSEBUTTONUP:

            if event.button == 1:
                self.dragging = False

        return False

    def draw(self, screen):

        rect = self.get_rect()

        pygame.draw.rect(screen, self.background_color, rect, border_radius=4)

        fill_width = int(rect.width * self.get_ratio())

        if fill_width > 0:
            fill_rect = pygame.Rect(rect.x, rect.y, fill_width, rect.height)

            pygame.draw.rect(screen, self.fill_color, fill_rect, border_radius=4)

        pygame.draw.circle(screen, self.knob_color, (self.get_knob_x(), rect.centery), 10)
