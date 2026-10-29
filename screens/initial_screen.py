import pygame

from core.player import Player
from core.game_state import GameState
from core.board import Board

from screens.base_screen import BaseScreen

from ui.input_box import InputBox
from ui.button import Button
from ui.layout import Layout
from ui import theme

class InitialScreen(BaseScreen):
    def __init__(self, screen_manager, screen, context=None):
        super().__init__(screen_manager, screen, context)

        # 📐 layout responsive
        self.layout = Layout(screen)

        # 🧾 UI
        self.build_ui()

        # ❌ error opcional
        self.error_message = None

    def build_ui(self):
        self.layout.update()

        self.money_input = InputBox(self.layout.x(0.3), self.layout.y(0.2), self.layout.width(0.4),
                                    self.layout.height(0.08), "20")

        self.width_input = InputBox(self.layout.x(0.3), self.layout.y(0.32), self.layout.width(0.4),
                                    self.layout.height(0.08), "10")

        self.height_input = InputBox(self.layout.x(0.3), self.layout.y(0.44), self.layout.width(0.4),
                                     self.layout.height(0.08), "10")

        self.start_button = Button(self.layout.x(0.35), self.layout.y(0.6), self.layout.width(0.3),
                                   self.layout.height(0.1), "START", self.start_game)

    def handle_event(self, event):
        self.money_input.handle_event(event)
        self.width_input.handle_event(event)
        self.height_input.handle_event(event)

        self.start_button.handle_event(event)

    def render(self, screen):
        # Fons global
        screen.fill(theme.BACKGROUND)

        # Camps d'entrada
        self.money_input.draw(screen)
        self.width_input.draw(screen)
        self.height_input.draw(screen)

        # Botó principal
        self.start_button.draw(screen)

        # Missatge d'error
        if self.error_message:
            font = pygame.font.SysFont(theme.FONT_NAME, theme.FONT_BUTTON)

            txt = font.render(self.error_message, True, theme.DANGER)

            screen.blit(txt, (self.layout.x(0.3), self.layout.y(0.1)))

    def on_resize(self, w, h):
        self.layout.update()
        self.build_ui()

    def validate(self):
        money = int(self.money_input.text)
        width = int(self.width_input.text)
        height = int(self.height_input.text)

        return (money > 0 and 10 <= width <= 30 and 10 <= height <= 30)

    def start_game(self):
        if not self.validate():
            self.error_message = "Configuració no vàlida"
            return

        money = int(self.money_input.text)
        width = int(self.width_input.text)
        height = int(self.height_input.text)

        player1 = Player(1, "Player 1", money)
        player2 = Player(2, "Player 2", money)

        board = Board(width, height)

        game_state = GameState(player1, player2, board)

        self.sm.change_screen("select", game_state)
