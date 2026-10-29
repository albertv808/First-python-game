import pygame

from core.combat import format_combat_columns
from core.battle_manager import BattleManager
from screens.base_screen import BaseScreen
from ui.layout import Layout
from ui.grid import Grid
from ui.button import Button
from ui.piece_renderer import PieceRenderer
from ui.popup import Popup
from ui import theme


class BattleScreen(BaseScreen):
    MIN_CELL_SIZE = 50
    MAX_CELL_SIZE = 80

    def __init__(self, screen_manager, screen, context=None):
        super().__init__(screen_manager, screen, context)

        self.layout = Layout(screen)
        self.manager = BattleManager(self.game_state)

        self.grid = None
        self.finish_button = None

        self.combat_popup = Popup(screen, width=560, height=440, title="Resultat del combat")

        self.hovered_piece = None
        self.hovered_cell = None

        self.build_ui()
        self.refresh_highlights()

    # ======================================================
    # UI
    # ======================================================

    def build_ui(self):
        self.layout.update()

        board = self.game_state.board

        available_width = self.layout.width(0.74)
        available_height = self.layout.height(0.76)

        cell_size = max(self.MIN_CELL_SIZE,
            min(self.MAX_CELL_SIZE, available_width / board.width, available_height / board.height))

        viewport = pygame.Rect(int(self.layout.x(0.02)), int(self.layout.y(0.16)), int(available_width),
            int(available_height))

        self.grid = Grid(viewport.x, viewport.y, board.width, board.height, cell_size, background_color=(55, 55, 65),
            line_color=theme.GRID_BORDER, viewport=viewport)

        panel_x = self.layout.x(0.79)
        panel_width = self.layout.width(0.19)

        self.finish_button = Button(panel_x, self.layout.y(0.82), panel_width, self.layout.height(0.075), "FINALITZAR",
            self.finish_activation, enabled=False)

    def on_resize(self, w, h):
        self.layout.update()
        self.build_ui()
        self.combat_popup.update_position()
        self.refresh_highlights()

    def show_combat_popup(self):
        """Mostra el resultat i els càlculs de l'últim atac."""
        details = self.manager.last_combat_log

        if not details or not details.get("valid", False):
            print("ERROR: no hi ha un registre de combat vàlid.")
            return

        left, right = format_combat_columns(details)

        self.combat_popup.open_columns(title="Resultat del combat", left=left, right=right)
    # ======================================================
    # SELECCIÓ I ACCIONS
    # ======================================================

    def select_piece(self, piece):
        if self.manager.select_piece(piece):
            self.refresh_highlights()
            return True

        return False

    def handle_board_click(self, visual_cell):
        if visual_cell is None:
            return

        x, y = visual_cell
        piece = self.game_state.board.get_piece(x, y)
        selected = self.manager.selected_piece

        # 1. Intentar moure la peça seleccionada.
        if selected is not None:
            if (x, y) in self.manager.get_valid_moves():
                if self.manager.move_selected_piece(x, y):
                    self.refresh_highlights()
                return

            # 2. Intentar atacar una peça enemiga.
            if (x, y) in self.manager.get_valid_attacks():
                success = self.manager.attack_selected_piece(x, y)

                if success:
                    self.refresh_highlights()

                    # IMPORTANT: mostrar el resultat del combat.
                    self.show_combat_popup()

                return

        # 3. Seleccionar una altra peça pròpia.
        if (piece is not None and piece.player == self.manager.current_player and not piece.has_acted):
            self.select_piece(piece)

    def finish_activation(self):
        if self.manager.selected_piece is None:
            return

        self.manager.finish_piece_action()
        self.refresh_highlights()

    # ======================================================
    # COLORS I INDICADORS
    # ======================================================

    def refresh_highlights(self):
        if self.grid is None:
            return

        board = self.game_state.board
        self.grid.clear_cell_colors()

        # Colors base de les zones de cada jugador.
        for y in range(board.height):
            for x in range(board.width):
                if x < 2:
                    color = theme.DEPLOY_PLAYER_1
                elif x >= board.width - 2:
                    color = theme.DEPLOY_PLAYER_2
                else:
                    color = (55, 55, 65)

                self.grid.set_cell_color(x, y, color)

        selected = self.manager.selected_piece

        if selected is not None:
            # Caselles de moviment en blau.
            for x, y in self.manager.get_valid_moves():
                self.grid.set_cell_color(
                    x, y, (55, 105, 175)
                )

        self.finish_button.enabled = selected is not None

    # ======================================================
    # ESDEVENIMENTS
    # ======================================================

    def handle_event(self, event):
        if event.type == pygame.VIDEORESIZE:
            self.on_resize(event.w, event.h)
            return

        # El popup té prioritat sobre el tauler i els botons.
        if self.combat_popup.visible:
            self.combat_popup.handle_event(event)
            return

        if self.grid.handle_event(event):
            return

        if self.finish_button.handle_event(event):
            return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            cell = self.grid.get_cell_at(event.pos)
            self.handle_board_click(cell)

    def update_hover(self):
        """Actualitza la tropa situada sota el ratolí."""
        mouse_pos = pygame.mouse.get_pos()
        cell = self.grid.get_cell_at(mouse_pos)

        self.hovered_cell = cell
        self.hovered_piece = None

        if cell is not None:
            x, y = cell
            piece = self.game_state.board.get_piece(x, y)

            if piece is not None and piece.is_alive:
                self.hovered_piece = piece

    # ======================================================
    # DIBUIX
    # ======================================================

    def render(self, screen):
        screen.fill(theme.BACKGROUND)

        self.draw_header(screen)
        self.grid.draw(screen)
        self.draw_pieces(screen)
        self.draw_attack_outlines(screen)
        self.draw_selected_outline(screen)
        self.draw_panel(screen)

        self.finish_button.draw(screen)
        self.grid.draw_scrollbars(screen)

        # El popup sempre es dibuixa per sobre de la interfície.
        self.combat_popup.draw(screen)

    def draw_header(self, screen):
        font = pygame.font.SysFont(theme.FONT_NAME, theme.FONT_TITLE)
        small_font = pygame.font.SysFont(theme.FONT_NAME, theme.FONT_SMALL)

        player = self.manager.current_player

        # Títol a l'esquerra
        title = font.render(f"BATALLA - {player.name}", True, theme.TEXT)
        screen.blit(title, (self.layout.x(0.02), self.layout.y(0.035)))

        # Instruccions al centre
        instructions_x = self.layout.x(0.34)
        instructions_y = self.layout.y(0.025)

        lines = ["INSTRUCCIONS", "Blau: moviment", "Vermell: atac", "Groc: tropa seleccionada",
            "Enfosquida: activació completada", ]

        for i, line in enumerate(lines):
            color = theme.TEXT if i == 0 else theme.TEXT_SECONDARY
            text = small_font.render(line, True, color)

            screen.blit(text, (instructions_x, instructions_y + i * self.layout.height(0.027)))

        # Torn a la dreta
        turn_text = small_font.render(f"Torn {self.game_state.turn}", True, theme.TEXT_SECONDARY)

        screen.blit(turn_text, (self.layout.x(0.90) - turn_text.get_width(), self.layout.y(0.06)))

    def draw_pieces(self, screen):
        board = self.game_state.board

        old_clip = screen.get_clip()
        screen.set_clip(self.grid.content_rect)

        for y in range(board.height):
            for x in range(board.width):
                piece = board.get_piece(x, y)

                if piece is None or not piece.is_alive:
                    continue

                rect = self.grid.get_cell_rect(x, y)

                if not self.grid.content_rect.colliderect(rect):
                    continue

                PieceRenderer.draw(screen, rect, piece, self.grid.cell_size, darkened=piece.has_acted)

        screen.set_clip(old_clip)

    def draw_attack_outlines(self, screen):
        selected = self.manager.selected_piece

        if selected is None:
            return

        old_clip = screen.get_clip()
        screen.set_clip(self.grid.content_rect)

        for x, y in self.manager.get_valid_attacks():
            rect = self.grid.get_cell_rect(x, y).inflate(-4, -4)

            pygame.draw.rect(screen, theme.DANGER, rect, width=3, border_radius=4)

        screen.set_clip(old_clip)

    def draw_selected_outline(self, screen):
        selected = self.manager.selected_piece

        if selected is None:
            return

        old_clip = screen.get_clip()
        screen.set_clip(self.grid.content_rect)

        rect = self.grid.get_cell_rect(selected.x, selected.y).inflate(-2, -2)

        pygame.draw.rect(screen, theme.WARNING, rect, width=3, border_radius=5)

        screen.set_clip(old_clip)

    def draw_panel(self, screen):
        x = self.layout.x(0.79)
        y = self.layout.y(0.15)
        width = self.layout.width(0.19)

        selected = self.manager.selected_piece
        hovered = self.hovered_piece

        # Estadístiques de la tropa seleccionada
        self.draw_troop_stats(screen, selected, "Tropa seleccionada", x, y, width)

        # Separació entre les dues seccions
        y += self.layout.height(0.30)

        pygame.draw.line(screen, theme.GRID_BORDER, (int(x), int(y)), (int(x + width), int(y)), 2)

        y += self.layout.height(0.025)

        # Estadístiques de la tropa sota el ratolí
        self.draw_troop_stats(screen, hovered, "Sota el ratolí", x, y, width)

    def draw_troop_stats(self, screen, piece, title, x, y, width):
        font = pygame.font.SysFont(theme.FONT_NAME, theme.FONT_MEDIUM)
        small_font = pygame.font.SysFont(theme.FONT_NAME, theme.FONT_SMALL)

        title_surface = font.render(title, True, theme.TEXT)
        screen.blit(title_surface, (x, y))
        y += self.layout.height(0.045)

        if piece is None:
            text = small_font.render("Cap tropa", True, theme.TEXT_MUTED)
            screen.blit(text, (x, y))
            return

        details = [f"Nom: {piece.troop.name}", f"Unitats: {piece.count}", f"Vida: {piece.hp}/{piece.troop.life}",
            f"Moviment: {piece.troop.movement}", f"Rang d'atac: {piece.troop.attack_range}", ]

        for detail in details:
            text = small_font.render(detail, True, theme.TEXT_SECONDARY)
            screen.blit(text, (x, y))
            y += self.layout.height(0.035)

        if piece.has_acted:
            status = "Activació completada"
        else:
            status = "Activació disponible"

        screen.blit(small_font.render(status, True, theme.PRIMARY_HOVER), (x, y))

    # ======================================================
    # ACTUALITZACIÓ
    # ======================================================

    def update(self):
        # No canviar de pantalla mentre el jugador llegeix el combat.
        if self.combat_popup.visible:
            return

        self.update_hover()

        if self.manager.winner is not None:
            self.game_state.winner = self.manager.winner
            self.game_state.phase = "final"

            self.sm.change_screen("final", self.game_state)