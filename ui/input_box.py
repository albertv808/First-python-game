import pygame
from ui import theme
from ui.box import Box


class InputBox(Box):

    def __init__(self, x, y, w, h, text="", minimum=0, maximum=None):
        super().__init__(x, y, w, h)

        self.text = str(text)

        self.active = False
        self.select_all = False

        self.minimum = minimum
        self.maximum = maximum

        self.font = pygame.font.SysFont(theme.FONT_NAME, theme.FONT_MEDIUM)

    # ==========================================================
    # VALUE
    # ==========================================================

    def get_value(self):

        try:
            value = int(self.text)
        except (ValueError, TypeError):
            value = self.minimum

        value = max(self.minimum, value)

        if self.maximum is not None:
            value = min(self.maximum, value)

        return value

    def set_value(self, value):

        try:
            value = int(value)
        except (ValueError, TypeError):
            value = self.minimum

        value = max(self.minimum, value)

        if self.maximum is not None:
            value = min(self.maximum, value)

        self.text = str(value)

    # ==========================================================
    # EVENTS
    # ==========================================================

    def handle_event(self, event):

        changed = False

        # ------------------------------------------------------
        # MOUSE
        # ------------------------------------------------------

        if event.type == pygame.MOUSEBUTTONDOWN:

            if event.button == 1:

                if self.rect.collidepoint(event.pos):

                    self.active = True

                    # Quan entrem al camp, seleccionem tot
                    # el contingut.
                    self.select_all = True

                else:

                    if self.active:
                        self.set_value(self.get_value())

                    self.active = False
                    self.select_all = False

                return False

        # ------------------------------------------------------
        # KEYBOARD
        # ------------------------------------------------------

        if event.type == pygame.KEYDOWN and self.active:

            # --------------------------------------------------
            # BACKSPACE
            # --------------------------------------------------

            if event.key == pygame.K_BACKSPACE:

                if self.select_all:

                    self.text = ""
                    self.select_all = False

                elif self.text:

                    self.text = self.text[:-1]

                changed = True

            # --------------------------------------------------
            # DELETE
            # --------------------------------------------------

            elif event.key == pygame.K_DELETE:

                self.text = ""
                self.select_all = False

                changed = True

            # --------------------------------------------------
            # ENTER
            # --------------------------------------------------

            elif event.key == pygame.K_RETURN:

                self.set_value(self.get_value())

                self.active = False
                self.select_all = False

                changed = True

            # --------------------------------------------------
            # NUMBER
            # --------------------------------------------------

            elif event.unicode.isdigit():

                if self.select_all:

                    new_text = event.unicode
                    self.select_all = False

                else:

                    new_text = (self.text + event.unicode)

                # Evitar zeros inicials
                if len(new_text) > 1:

                    new_text = new_text.lstrip("0")

                    if new_text == "":
                        new_text = "0"

                try:
                    value = int(new_text)

                except ValueError:
                    return False

                # No permetre superar el màxim
                if self.maximum is not None and value > self.maximum:
                    return False

                self.text = new_text
                changed = True

        return changed

    # ==========================================================
    # DRAW
    # ==========================================================

    def draw(self, screen, color=None):

        color = (theme.INPUT_ACTIVE if self.active else theme.INPUT_BACKGROUND)

        super().draw(screen, color)

        txt = self.font.render(self.text, True, theme.INPUT_TEXT)

        text_rect = txt.get_rect(midleft=(self.rect.x + 10, self.rect.centery))

        screen.blit(txt, text_rect)

        if self.active:
            cursor_x = text_rect.right + 2

            pygame.draw.line(screen, theme.INPUT_CURSOR, (cursor_x, self.rect.y + 8), (cursor_x, self.rect.bottom - 8),
                             2)
