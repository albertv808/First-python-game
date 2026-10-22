import pygame

from core.battle_manager import BattleManager
from ui.layout import Layout
from ui.grid import Grid
from ui.button import Button
from ui.piece_renderer import PieceRenderer
from ui import theme


class BattleScreen:
    def __init__(self, screen_manager, screen, context=None):
        self.sm = screen_manager
        self.screen = screen
        self.game_state = context

        self.layout = Layout(screen)
        self.manager = BattleManager(self.game_state)

        self.grid = None
        self.finish_button = None

        self.build_ui()
        self.refresh_highlights()

    # ======================================================
    # UI
    # ======================================================

    def build_ui(self):
        self.layout.update()

        board = self.game_state.board

        # Reservem espai per al tauler i per al panell lateral.
        available_width = self.layout.width(0.74)
        available_height = self.layout.height(0.76)

        cell_size = min(
            available_width / board.width,
            available_height / board.height
        )

        grid_width = board.width * cell_size
        grid_height = board.height * cell_size

        grid_x = (
            self.layout.x(0.02)
            + (available_width - grid_width) / 2
        )

        grid_y = (
            self.layout.y(0.16)
            + (available_height - grid_height) / 2
        )

        self.grid = Grid(
            grid_x,
            grid_y,
            board.width,
            board.height,
            cell_size,
            background_color=(55, 55, 65),
            line_color=theme.GRID_BORDER
        )

        panel_x = self.layout.x(0.79)
        panel_width = self.layout.width(0.19)

        self.finish_button = Button(
            panel_x,
            self.layout.y(0.82),
            panel_width,
            self.layout.height(0.075),
            "FINALITZAR",
            self.finish_activation,
            enabled=False
        )

    def on_resize(self, w, h):
        self.layout.update()
        self.build_ui()
        self.refresh_highlights()

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
                if self.manager.attack_selected_piece(x, y):
                    self.refresh_highlights()
                return

        # 3. Seleccionar una altra peça pròpia.
        if (
            piece is not None
            and piece.player == self.manager.current_player
            and not piece.has_acted
        ):
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

        if self.finish_button.handle_event(event):
            return

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                cell = self.grid.get_cell_at(event.pos)
                self.handle_board_click(cell)

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

    def draw_header(self, screen):
        font = pygame.font.SysFont(
            theme.FONT_NAME, theme.FONT_TITLE
        )

        player = self.manager.current_player

        title = font.render(
            f"BATALLA - {player.name}",
            True,
            theme.TEXT
        )

        screen.blit(
            title,
            (self.layout.x(0.02), self.layout.y(0.035))
        )

        small_font = pygame.font.SysFont(
            theme.FONT_NAME, theme.FONT_SMALL
        )

        turn_text = small_font.render(
            f"Torn {self.game_state.turn}",
            True,
            theme.TEXT_SECONDARY
        )

        screen.blit(
            turn_text,
            (self.layout.x(0.80), self.layout.y(0.06))
        )

    def draw_pieces(self, screen):
        board = self.game_state.board

        for y in range(board.height):
            for x in range(board.width):
                piece = board.get_piece(x, y)

                if piece is None or not piece.is_alive:
                    continue

                rect = self.grid.get_cell_rect(x, y)

                PieceRenderer.draw(screen, rect, piece, self.grid.cell_size, darkened=piece.has_acted)

    def draw_attack_outlines(self, screen):
        selected = self.manager.selected_piece

        if selected is None:
            return

        for x, y in self.manager.get_valid_attacks():
            rect = self.grid.get_cell_rect(x, y).inflate(-4, -4)

            pygame.draw.rect(
                screen,
                theme.DANGER,
                rect,
                width=3,
                border_radius=4
            )

    def draw_selected_outline(self, screen):
        selected = self.manager.selected_piece

        if selected is None:
            return

        rect = self.grid.get_cell_rect(
            selected.x, selected.y
        ).inflate(-2, -2)

        pygame.draw.rect(
            screen,
            theme.WARNING,
            rect,
            width=3,
            border_radius=5
        )

    def draw_panel(self, screen):
        x = self.layout.x(0.79)
        y = self.layout.y(0.15)

        font = pygame.font.SysFont(
            theme.FONT_NAME, theme.FONT_MEDIUM
        )

        small_font = pygame.font.SysFont(
            theme.FONT_NAME, theme.FONT_SMALL
        )

        player = self.manager.current_player

        title = font.render("El teu exèrcit", True, theme.TEXT)
        screen.blit(title, (x, y))

        y += self.layout.height(0.07)

        remaining = self.manager.get_player_pieces(player)

        text = small_font.render(
            f"Tropes vives: {len(remaining)}",
            True,
            theme.TEXT_SECONDARY
        )

        screen.blit(text, (x, y))

        y += self.layout.height(0.07)

        selected = self.manager.selected_piece

        if selected is not None:
            screen.blit(
                font.render("Tropa seleccionada", True, theme.TEXT),
                (x, y)
            )

            y += self.layout.height(0.05)

            details = [
                selected.troop.name,
                f"Unitats: {selected.count}",
                f"Vida: {selected.hp}/{selected.troop.life}",
                f"Moviment: {selected.troop.movement}",
                f"Rang atac: {selected.troop.attack_range}",
            ]

            for detail in details:
                text = small_font.render(
                    detail, True, theme.TEXT_SECONDARY
                )
                screen.blit(text, (x, y))
                y += self.layout.height(0.045)

            y += self.layout.height(0.025)

            if selected in self.manager.moved_pieces:
                status = "Ja s'ha mogut"
            else:
                status = "Moviment disponible"

            screen.blit(
                small_font.render(status, True, theme.PRIMARY_HOVER),
                (x, y)
            )

            y += self.layout.height(0.04)

            if selected in self.manager.attacked_pieces:
                attack_status = "Ja ha atacat"
            else:
                attack_status = "Atac disponible"

            screen.blit(
                small_font.render(
                    attack_status,
                    True,
                    theme.DANGER
                    if selected not in self.manager.attacked_pieces
                    else theme.TEXT_MUTED
                ),
                (x, y)
            )

        else:
            instructions = [
                "Selecciona una tropa",
                "pròpia per començar.",
                "",
                "Blau: moviment",
                "Vermell: objectiu",
                "Groc: tropa seleccionada",
                "",
                "Enfosquida:",
                "activació completada",
            ]

            for line in instructions:
                screen.blit(
                    small_font.render(
                        line, True, theme.TEXT_SECONDARY
                    ),
                    (x, y)
                )
                y += self.layout.height(0.04)

    # ======================================================
    # ACTUALITZACIÓ
    # ======================================================

    def update(self):
        if self.manager.winner is not None:
            self.game_state.winner = self.manager.winner
            self.game_state.phase = "final"

            self.sm.change_screen("final", self.game_state)