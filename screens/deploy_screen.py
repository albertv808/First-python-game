import pygame

from core.troop import Troop

from ui.layout import Layout
from ui.grid import Grid
from ui.popup import Popup
from ui.slider import Slider
from ui.input_box import InputBox
from ui.button import Button
from ui.piece_renderer import PieceRenderer
from ui import theme


class DeployScreen:
    DEPLOY_WIDTH = 2

    def __init__(self, screen_manager, screen, context=None):
        self.finish_button = None
        self.troop_buttons = None
        self.sm = screen_manager
        self.screen = screen
        self.game_state = context

        self.layout = Layout(screen)

        self.players = [self.game_state.player1, self.game_state.player2]

        self.current_player_index = 0
        self.current_player = self.players[0]

        self.selected_troop_key = None

        # UI
        self.grid = None
        self.popup = None
        self.slider = None
        self.amount_input = None

        self.confirm_popup_button = None
        self.cancel_popup_button = None

        self.build_ui()

    # ==========================================================
    # UI
    # ==========================================================

    def build_ui(self):
        self.layout.update()

        self.build_grid()
        self.build_troop_buttons()
        self.build_finish_button()

    def build_grid(self):

        board = self.game_state.board

        available_width = self.layout.width(0.65)
        available_height = self.layout.height(0.75)

        cell_size = min(available_width / self.DEPLOY_WIDTH, available_height / board.height)

        grid_width = self.DEPLOY_WIDTH
        grid_height = board.height

        grid_x = self.layout.x(0.30)
        grid_y = self.layout.y(0.15)

        self.grid = Grid(grid_x, grid_y, grid_width, grid_height, cell_size)

    def build_troop_buttons(self):

        self.troop_buttons = []

        selected = getattr(self.current_player, "troops_selected", {})

        y = self.layout.y(0.20)

        for troop_key, total in selected.items():

            if total <= 0:
                continue

            troop = Troop(troop_key)

            button = Button(self.layout.x(0.03), y, self.layout.width(0.22), self.layout.height(0.07), troop.name,
                            lambda key=troop_key: self.select_troop(key))

            self.troop_buttons.append((troop_key, button))

            y += self.layout.height(0.09)

    def build_finish_button(self):

        width = self.layout.width(0.30)
        height = self.layout.height(0.07)

        x, y = self.layout.bottom_right(width, height, margin_x=0.03, margin_y=0.03)

        self.finish_button = Button(x, y, width, height, self.get_finish_button_text(), self.finish_deployment,
                                    enabled=self.all_units_deployed())

    def get_finish_button_text(self):

        if not self.all_units_deployed():
            return "FALTA DESPLEGAR"

        if self.current_player_index == 0:
            return "PASSAR AL JUGADOR 2"

        return "COMENÇAR BATALLA"

    # ==========================================================
    # TROOPES
    # ==========================================================

    def select_troop(self, troop_key):

        if self.get_available_units(troop_key) <= 0:
            return

        self.selected_troop_key = troop_key

    def get_total_selected(self, troop_key):
        selected = getattr(self.current_player, "troops_selected", {})

        return selected.get(troop_key, 0)

    def get_deployed_units(self, troop_key):

        total = 0

        for piece in self.current_player.pieces:

            if piece.troop.key == troop_key:
                total += piece.count

        return total

    def get_available_units(self, troop_key):

        if troop_key is None:
            return 0

        selected = getattr(self.current_player, "troops_selected", {}).get(troop_key, 0)

        deployed = 0

        for piece in self.current_player.pieces:

            if piece.troop.key == troop_key:
                deployed += piece.count

        return max(0, selected - deployed)

    def all_units_deployed(self):

        selected = getattr(self.current_player, "troops_selected", {})

        for troop_key, amount in selected.items():

            if self.get_available_units(troop_key) > 0:
                return False

        return True

    # ==========================================================
    # COORDENADES
    # ==========================================================

    def visual_to_board(self, visual_x, visual_y):

        board = self.game_state.board

        if self.current_player.id == 1:

            board_x = visual_x

        else:

            board_x = (board.width - 1 - visual_x)

        return board_x, visual_y

    # ==========================================================
    # POPUP
    # ==========================================================

    def open_deploy_popup(self, visual_cell):

        if self.selected_troop_key is None:
            return

        visual_x, visual_y = visual_cell

        board_x, board_y = self.visual_to_board(visual_x, visual_y)

        board = self.game_state.board

        # Validació zona
        if self.current_player.id == 1:

            if board_x >= self.DEPLOY_WIDTH:
                return

        else:

            if board_x < (board.width - self.DEPLOY_WIDTH):
                return

        # Casella ocupada
        if board.get_piece(board_x, board_y) is not None:
            return

        available = self.get_available_units(self.selected_troop_key)

        if available <= 0:
            return

        troop = Troop(self.selected_troop_key)

        # Popup
        self.popup = Popup(self.screen, title=f"Desplegar {troop.name}")

        self.popup.open()

        popup_rect = self.popup.rect

        # Slider
        self.slider = Slider(popup_rect.x + 40, popup_rect.y + 125, popup_rect.width - 80, minimum=0, maximum=available,
                             value=1)

        # Input
        self.amount_input = InputBox(popup_rect.x + 130, popup_rect.y + 165, 190, 45, text="1", minimum=0,
                                     maximum=available)

        # Botons
        self.confirm_popup_button = Button(popup_rect.x + 35, popup_rect.bottom - 55, 150, 40, "CONFIRMAR",
                                           lambda: self.confirm_deployment(board_x, board_y))

        self.cancel_popup_button = Button(popup_rect.x + 215, popup_rect.bottom - 55, 150, 40, "CANCEL·LAR",
                                          self.close_popup)

    def close_popup(self):

        self.popup = None
        self.slider = None
        self.amount_input = None

        self.confirm_popup_button = None
        self.cancel_popup_button = None

    def confirm_deployment(self, x, y):

        if self.slider is None:
            return

        if self.amount_input is None:
            return

        amount = self.amount_input.get_value()

        if amount <= 0:
            return

        available = self.get_available_units(self.selected_troop_key)

        if amount > available:
            amount = available

        if amount <= 0:
            return

        troop = Troop(self.selected_troop_key)

        player = self.current_player

        piece = player.deploy_piece(troop, amount, x, y)

        success = self.game_state.board.place_piece(piece, x, y)

        if not success:

            if piece in player.pieces:
                player.pieces.remove(piece)

            return

        # ----------------------------------------------
        # TANCAR POPUP
        # ----------------------------------------------

        self.close_popup()

        # ----------------------------------------------
        # SI NO QUEDEN UNITATS, DESELECCIONAR TROPA
        # ----------------------------------------------

        if self.get_available_units(self.selected_troop_key) <= 0:
            self.selected_troop_key = None

        # ----------------------------------------------
        # ACTUALITZAR BOTÓ
        # ----------------------------------------------

        self.update_finish_button()

    # ==========================================================
    # CANVI DE JUGADOR
    # ==========================================================

    def finish_deployment(self):

        # No permetre avançar si encara falten tropes
        if not self.all_units_deployed():
            return

        # ==================================================
        # PLAYER 1 → PLAYER 2
        # ==================================================

        if self.current_player_index == 0:
            self.current_player_index = 1

            self.current_player = self.players[1]

            self.selected_troop_key = None

            self.close_popup()

            self.build_ui()

            return

        # ==================================================
        # PLAYER 2 → BATTLE
        # ==================================================

        self.game_state.deployed_pieces = {1: self.game_state.player1.pieces, 2: self.game_state.player2.pieces}

        self.game_state.phase = "battle"

        self.sm.change_screen("battle", self.game_state)

    # ==========================================================
    # EVENTS
    # ==========================================================

    def handle_event(self, event):

        if event.type == pygame.VIDEORESIZE:
            self.on_resize(event.w, event.h)
            return

        # --------------------------------------------------
        # Popup
        # --------------------------------------------------

        if self.popup is not None:
            self.handle_popup_event(event)

            return

        # --------------------------------------------------
        # Tropes
        # --------------------------------------------------

        for _, button in self.troop_buttons:
            button.handle_event(event)

        self.finish_button.handle_event(event)

        # --------------------------------------------------
        # Grid
        # --------------------------------------------------

        if event.type == pygame.MOUSEBUTTONDOWN:

            if event.button == 1:

                cell = self.grid.get_cell_at(event.pos)

                if cell is not None:
                    self.open_deploy_popup(cell)

    def handle_popup_event(self, event):

        if self.popup is None:
            return

        # ==================================================
        # SLIDER
        # ==================================================

        if self.slider is not None:

            if self.slider.handle_event(event):
                self.amount_input.set_value(self.slider.value)

                return

        # ==================================================
        # INPUT
        # ==================================================

        if self.amount_input is not None:

            if self.amount_input.handle_event(event):
                self.slider.set_value(self.amount_input.get_value())

                return

        # ==================================================
        # CONFIRMAR
        # ==================================================

        if self.confirm_popup_button is not None:

            if self.confirm_popup_button.handle_event(event):
                return

        # ==================================================
        # CANCEL·LAR
        # ==================================================

        if self.cancel_popup_button is not None:

            if self.cancel_popup_button.handle_event(event):
                return

    # ==========================================================
    # DRAW
    # ==========================================================

    def render(self, screen):

        screen.fill(theme.BACKGROUND)

        self.draw_header(screen)
        self.draw_troop_panel(screen)
        self.draw_grid(screen)
        self.finish_button.draw(screen)

        if self.popup is not None:
            self.draw_popup(screen)

    def draw_header(self, screen):
        font = pygame.font.SysFont(theme.FONT_NAME, theme.FONT_TITLE)

        title = font.render(f"DESPLEGAMENT - {self.current_player.name}", True, theme.TEXT)

        screen.blit(title, (self.layout.x(0.03), self.layout.y(0.04)))

        direction = ("→ DIRECCIÓ ENEMIGA" if self.current_player.id == 1 else "← DIRECCIÓ ENEMIGA")

        direction_text = font.render(direction, True, theme.PRIMARY_HOVER)

        screen.blit(direction_text, (self.layout.x(0.60), self.layout.y(0.04)))

    def draw_troop_panel(self, screen):

        font = pygame.font.SysFont(theme.FONT_NAME, theme.FONT_MEDIUM)

        for troop_key, button in self.troop_buttons:

            # Highlight
            if troop_key == self.selected_troop_key:
                pygame.draw.rect(screen, theme.PRIMARY, button.rect.inflate(6, 6), border_radius=theme.BORDER_RADIUS)

            button.draw(screen)

            available = self.get_available_units(troop_key)

            text = font.render(f"{available} disponibles", True, theme.TEXT_SECONDARY)

            screen.blit(text, (button.rect.x, button.rect.bottom + 3))

    def draw_grid(self, screen):

        board = self.game_state.board

        # Pintar zona de desplegament
        for y in range(board.height):

            for visual_x in range(self.DEPLOY_WIDTH):

                rect = self.grid.get_cell_rect(visual_x, y)

                zone_color = (theme.DEPLOY_PLAYER_1 if self.current_player.id == 1 else theme.DEPLOY_PLAYER_2)

                pygame.draw.rect(screen, zone_color, rect)

                pygame.draw.rect(screen, theme.GRID_BORDER, rect, 1)

                board_x, board_y = (self.visual_to_board(visual_x, y))

                piece = board.get_piece(board_x, board_y)

                if piece is not None:
                    PieceRenderer.draw(screen, rect, piece, self.grid.cell_size)

    def draw_popup(self, screen):

        self.popup.draw(screen)

        # --------------------------------------------------
        # Informació
        # --------------------------------------------------

        font = pygame.font.SysFont(theme.FONT_NAME, theme.FONT_MEDIUM)

        available_text = font.render(f"Disponibles: {self.slider.maximum}", True, theme.TEXT_SECONDARY)

        screen.blit(available_text, (self.popup.rect.x + 40, self.popup.rect.y + 75))

        value_text = font.render(f"Quantitat: {self.slider.value}", True, theme.PRIMARY_HOVER)

        screen.blit(value_text, (self.popup.rect.x + 40, self.popup.rect.y + 100))

        # --------------------------------------------------
        # Slider
        # --------------------------------------------------

        self.slider.draw(screen)

        # --------------------------------------------------
        # Input
        # --------------------------------------------------

        self.amount_input.draw(screen)

        # --------------------------------------------------
        # Botons
        # --------------------------------------------------

        self.confirm_popup_button.draw(screen)

        self.cancel_popup_button.draw(screen)

    def update_finish_button(self):

        if self.finish_button is None:
            return

        # Actualitzar text
        self.finish_button.text = (self.get_finish_button_text())

        # Activar/desactivar
        self.finish_button.enabled = (self.all_units_deployed())

    # ==========================================================
    # UPDATE / RESIZE
    # ==========================================================

    def update(self):
        pass

    def on_resize(self, w, h):

        self.layout.update()

        self.build_ui()
