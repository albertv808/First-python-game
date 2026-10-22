import pygame

from core.troop import Troop
from data.troops_data import TROOPS
from ui.layout import Layout
from ui.button import Button
from ui import theme



class SelectScreen:
    def __init__(self, screen_manager, screen, context=None):
        self.sm = screen_manager
        self.screen = screen
        self.game_state = context

        self.layout = Layout(screen)

        self.current_player_index = 0
        self.players = [self.game_state.player1, self.game_state.player2]

        self.current_player = self.players[self.current_player_index]

        # selecció temporal
        self.selection = {key: 0 for key in TROOPS.keys()}

        self.build_ui()

    def build_ui(self):
        self.layout.update()

        self.buttons = []

        y_start = 0.2
        spacing = 0.1

        for i, key in enumerate(TROOPS.keys()):
            troop = Troop(key)

            btn = Button(self.layout.x(0.2), self.layout.y(y_start + i * spacing), self.layout.width(0.4),
                self.layout.height(0.08), f"{troop.name} (${troop.cost})", lambda k=key: self.add_troop(k))

            self.buttons.append(btn)

        self.confirm_button = Button(self.layout.x(0.65), self.layout.y(0.8), self.layout.width(0.25),
            self.layout.height(0.1), "CONFIRM", self.confirm_selection)

    def add_troop(self, troop_key):
        troop = Troop(troop_key)

        if self.current_player.money >= troop.cost:
            self.current_player.money -= troop.cost
            self.selection[troop_key] += 1

    def confirm_selection(self):
        self.current_player.troops_selected = (self.selection.copy())

        self.current_player.army_selection = (self.selection.copy())

        self.current_player_index += 1

        if self.current_player_index < len(self.players):

            self.current_player = (self.players[self.current_player_index])

            self.selection = {key: 0 for key in TROOPS.keys()}

        else:

            self.sm.change_screen("deploy", self.game_state)

    def handle_event(self, event):
        for btn in self.buttons:
            btn.handle_event(event)

        self.confirm_button.handle_event(event)

    def render(self, screen):
        # Fons global
        screen.fill(theme.BACKGROUND)

        # Informació del jugador actual
        font = pygame.font.SysFont(theme.FONT_NAME, theme.FONT_TITLE)

        txt = font.render(f"{self.current_player.name} - Money: {self.current_player.money}", True, theme.TEXT)

        screen.blit(txt, (self.layout.x(0.03), self.layout.y(0.04)))

        # Tropes seleccionades
        small_font = pygame.font.SysFont(theme.FONT_NAME, theme.FONT_MEDIUM)

        y = self.layout.y(0.15)

        for key, count in self.selection.items():
            if count > 0:
                txt = small_font.render(f"{TROOPS[key]['name']}: {count}", True, theme.TEXT_SECONDARY)

                screen.blit(txt, (self.layout.x(0.55), y))

                y += self.layout.height(0.05)

        # Botons
        for btn in self.buttons:
            btn.draw(screen)

        self.confirm_button.draw(screen)

    def on_resize(self, w, h):
        self.build_ui()
