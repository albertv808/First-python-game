import pygame

from core.board import Board
from core.game_state import GameState
from core.player import Player

from screens.base_screen import BaseScreen

from ui import theme
from ui.button import Button
from ui.input_box import InputBox
from ui.layout import Layout
from ui.slider import Slider
from ui.scrollbar import Scrollbar


class InitialScreen(BaseScreen):

    def __init__(self, screen_manager, screen, context=None):
        super().__init__(screen_manager, screen, context)

        self.layout = Layout(screen)
        self.error_message = None

        self.initial_money = "20"
        self.initial_width = "10"
        self.initial_height = "10"

        self.scroll = 0
        self.build_ui()

    def build_ui(self):

        self.layout.update()

        w = self.layout.w
        h = self.layout.h

        # Conservar els valors actuals.
        money = getattr(self, "money_input", None)
        board_width = getattr(self, "width_input", None)
        board_height = getattr(self, "height_input", None)

        money_value = money.text if money else str(self.initial_money)
        width_value = board_width.text if board_width else str(self.initial_width)
        height_value = board_height.text if board_height else str(self.initial_height)

        # Fonts.
        self.title_font = pygame.font.SysFont(
            theme.FONT_NAME, max(36, min(60, int(h * 0.085))), bold=True
        )
        self.subtitle_font = pygame.font.SysFont(theme.FONT_NAME, theme.FONT_SMALL)
        self.label_font = pygame.font.SysFont(
            theme.FONT_NAME, theme.FONT_MEDIUM, bold=True
        )
        self.help_font = pygame.font.SysFont(
            theme.FONT_NAME, max(14, theme.FONT_SMALL - 4)
        )
        self.summary_font = pygame.font.SysFont(
            theme.FONT_NAME, theme.FONT_MEDIUM, bold=True
        )
        self.error_font = pygame.font.SysFont(theme.FONT_NAME, theme.FONT_SMALL)

        # Capçalera fixa.
        self.header_height = min(max(145, int(h * 0.25)), 185)
        self.viewport_top = self.header_height
        self.bottom_margin = max(12, int(h * 0.025))

        # Amplada del formulari.
        self.content_width = max(
            1, min(int(w * 0.72), 680, w - 48)
        )
        self.center_x = w // 2
        self.content_left = self.center_x - self.content_width // 2

        # Mides i posicions locals del formulari.
        compact = h < 600
        self.input_height = 38 if compact else 46

        self.money_label_y = 22
        self.money_input_y = 42
        self.money_help_y = self.money_input_y + self.input_height + 15

        # Separació entre el pressupost i les dimensions.
        self.dimensions_title_y = 145
        self.fields_label_y = 184
        self.fields_y = 202

        self.slider_y = self.fields_y + self.input_height + 20
        self.limits_y = self.slider_y + 20

        self.summary_y = 324
        self.summary_height = 50
        self.error_y = 392

        self.button_height = 44 if compact else 56
        self.button_y = 420

        self.content_height = self.button_y + self.button_height + 24

        self.content_surface = pygame.Surface(
            (w, self.content_height)
        )

        # Pressupost.
        money_width = min(self.content_width, int(w * 0.42))
        money_x = self.center_x - money_width // 2

        self.money_input = InputBox(
            money_x, self.money_input_y,
            money_width, self.input_height,
            money_value, minimum=1
        )

        # Columnes.
        gap = max(20, int(self.content_width * 0.06))
        self.column_width = (self.content_width - gap) // 2

        self.width_x = self.content_left
        self.height_x = self.content_left + self.column_width + gap

        self.width_input = InputBox(
            self.width_x, self.fields_y,
            self.column_width, self.input_height,
            width_value, minimum=10, maximum=30
        )

        self.height_input = InputBox(
            self.height_x, self.fields_y,
            self.column_width, self.input_height,
            height_value, minimum=10, maximum=30
        )

        # Sliders.
        self.width_slider = Slider(
            self.width_x, self.slider_y, self.column_width,
            minimum=10, maximum=30,
            value=self.width_input.get_value(), height=8
        )

        self.height_slider = Slider(
            self.height_x, self.slider_y, self.column_width,
            minimum=10, maximum=30,
            value=self.height_input.get_value(), height=8
        )

        # Resum.
        summary_width = min(self.content_width, 620)
        self.summary_rect = pygame.Rect(
            self.center_x - summary_width // 2,
            self.summary_y,
            summary_width,
            self.summary_height
        )

        # Botó START.
        button_width = min(int(self.content_width * 0.65), 300)

        self.start_button = Button(
            self.center_x - button_width // 2,
            self.button_y,
            button_width,
            self.button_height,
            "START",
            self.start_game
        )

        # Àrea visible i scrollbar.
        self.viewport = pygame.Rect(
            0, self.viewport_top,
            w, max(1, h - self.viewport_top - self.bottom_margin)
        )

        self.scrollbar = Scrollbar(
            w - 13, self.viewport.y,
            8, self.viewport.height,
            content_height=self.content_height,
            view_height=self.viewport.height,
            orientation="vertical"
        )

        self.scrollbar.set_metrics(
            self.content_height, self.viewport.height
        )
        self.scrollbar.set_scroll(self.scroll)
        self.scroll = self.scrollbar.scroll

        # Alinear a baix si tot el contingut hi cap.
        if self.content_height <= self.viewport.height:
            self.content_origin_y = (
                self.viewport.height - self.content_height
            )
        else:
            self.content_origin_y = 0

    # ==========================================================
    # ESDEVENIMENTS
    # ==========================================================

    def _translate_event(self, event):

        if not hasattr(event, "pos"):
            return event

        x, y = event.pos

        if self.viewport.collidepoint((x, y)):
            local_y = (
                y - self.viewport.y
                - self.content_origin_y + self.scroll
            )
        else:
            local_y = -100000

        attributes = dict(event.dict)
        attributes["pos"] = (x, local_y)

        return pygame.event.Event(event.type, attributes)

    def handle_event(self, event):

        # Primer, gestionar la barra de desplaçament.
        self.scrollbar.handle_event(event, viewport=self.viewport)
        self.scroll = self.scrollbar.scroll

        if (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and self.scrollbar.rect.collidepoint(event.pos)
        ):
            return

        if self.scrollbar.dragging:
            return

        translated = self._translate_event(event)

        money_changed = self.money_input.handle_event(translated)
        width_changed = self.width_input.handle_event(translated)
        height_changed = self.height_input.handle_event(translated)

        # Sincronització input -> slider.
        if width_changed:
            self.width_slider.set_value(self.width_input.get_value())

        if height_changed:
            self.height_slider.set_value(self.height_input.get_value())

        # Sincronització slider -> input.
        if self.width_slider.handle_event(translated):
            self.width_input.set_value(self.width_slider.value)

        if self.height_slider.handle_event(translated):
            self.height_input.set_value(self.height_slider.value)

        self.start_button.handle_event(translated)

        if money_changed or width_changed or height_changed:
            self.error_message = None

    # ==========================================================
    # RENDERITZACIÓ
    # ==========================================================

    def render(self, screen):

        screen.fill(theme.BACKGROUND)

        w = self.layout.w
        h = self.layout.h
        cx = self.center_x

        # Capçalera fixa.
        title = self.title_font.render("FANTASY ARMY BATTLE", True, theme.TEXT)
        screen.blit(
            title,
            title.get_rect(center=(cx, int(self.header_height * 0.32)))
        )

        subtitle = self.subtitle_font.render(
            "Configura la teva partida", True, theme.TEXT_SECONDARY
        )
        screen.blit(
            subtitle,
            subtitle.get_rect(center=(cx, int(self.header_height * 0.62)))
        )

        pygame.draw.line(
            screen, theme.PRIMARY,
            (cx - 80, int(self.header_height * 0.82)),
            (cx + 80, int(self.header_height * 0.82)), 3
        )

        # Dibuixar el formulari a la superfície virtual.
        surface = self.content_surface
        surface.fill(theme.BACKGROUND)

        self._draw_label(
            surface, "Pressupost inicial",
            cx, self.money_label_y, centered=True
        )
        self.money_input.draw(surface)

        money_help = self.help_font.render(
            "Diners disponibles per a cada jugador",
            True, theme.TEXT_MUTED
        )
        surface.blit(
            money_help,
            money_help.get_rect(center=(cx, self.money_help_y))
        )

        self._draw_label(
            surface, "Dimensions del tauler",
            cx, self.dimensions_title_y, centered=True
        )

        # Etiquetes centrades respecte dels camps.
        self._draw_label(
            surface, "Amplada",
            self.width_x + self.column_width // 2,
            self.fields_label_y, centered=True
        )
        self._draw_label(
            surface, "Longitud",
            self.height_x + self.column_width // 2,
            self.fields_label_y, centered=True
        )

        self.width_input.draw(surface)
        self.height_input.draw(surface)

        self.width_slider.draw(surface)
        self.height_slider.draw(surface)

        self._draw_slider_limits(
            surface, self.width_x, self.limits_y, self.column_width
        )
        self._draw_slider_limits(
            surface, self.height_x, self.limits_y, self.column_width
        )

        # Resum de dimensions.
        width = self.width_input.get_value()
        height = self.height_input.get_value()

        pygame.draw.rect(
            surface, theme.SURFACE, self.summary_rect,
            border_radius=theme.BORDER_RADIUS
        )
        pygame.draw.rect(
            surface, theme.BORDER, self.summary_rect,
            theme.BORDER_WIDTH,
            border_radius=theme.BORDER_RADIUS
        )

        summary = self.summary_font.render(
            f"{width} x {height} = {width * height} caselles",
            True, theme.TEXT
        )
        surface.blit(
            summary,
            summary.get_rect(center=self.summary_rect.center)
        )

        if self.error_message:
            error = self.error_font.render(
                self.error_message, True, theme.DANGER
            )
            surface.blit(
                error,
                error.get_rect(center=(cx, self.error_y))
            )

        self.start_button.draw(surface)

        # Mostrar només la zona visible.
        if self.content_height <= self.viewport.height:
            source_y = 0
            destination_y = self.viewport.y + self.content_origin_y
        else:
            source_y = self.scroll
            destination_y = self.viewport.y

        source_height = min(
            self.viewport.height,
            self.content_height - source_y
        )

        if source_height > 0:
            screen.set_clip(self.viewport)

            screen.blit(
                surface,
                (0, destination_y),
                pygame.Rect(0, source_y, w, source_height)
            )

            screen.set_clip(None)

        self.scrollbar.draw(screen)

    # ==========================================================
    # AUXILIARS
    # ==========================================================

    def _draw_label(self, screen, text, x, y, centered=False):

        label = self.label_font.render(text, True, theme.TEXT)

        if centered:
            rect = label.get_rect(center=(x, y))
        else:
            rect = label.get_rect(midleft=(x, y))

        screen.blit(label, rect)

    def _draw_slider_limits(self, screen, x, y, width):

        minimum = self.help_font.render("10", True, theme.TEXT_MUTED)
        maximum = self.help_font.render("30", True, theme.TEXT_MUTED)

        screen.blit(minimum, (x, y))
        screen.blit(maximum, maximum.get_rect(topright=(x + width, y)))

    # ==========================================================
    # REDIMENSIONAMENT
    # ==========================================================

    def on_resize(self, w, h):

        self.initial_money = self.money_input.text
        self.initial_width = self.width_input.text
        self.initial_height = self.height_input.text

        self.layout.update()
        self.build_ui()

    # ==========================================================
    # VALIDACIÓ
    # ==========================================================

    def validate(self):

        try:
            money = int(self.money_input.text)
            width = int(self.width_input.text)
            height = int(self.height_input.text)
        except (ValueError, TypeError):
            return False

        return (
            money > 0
            and 10 <= width <= 30
            and 10 <= height <= 30
        )

    # ==========================================================
    # INICI DE LA PARTIDA
    # ==========================================================

    def start_game(self):

        if not self.validate():
            self.error_message = (
                "Introdueix valors vàlids per a tots els camps"
            )
            return

        money = int(self.money_input.text)
        width = int(self.width_input.text)
        height = int(self.height_input.text)

        player1 = Player(1, "Player 1", money)
        player2 = Player(2, "Player 2", money)

        board = Board(width, height)
        game_state = GameState(player1, player2, board)

        self.sm.change_screen("select", game_state)