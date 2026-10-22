import pygame

from ui import theme


class PieceRenderer:
    """Renderització compartida de les peces del tauler."""

    @staticmethod
    def draw(screen, rect, piece, cell_size, darkened=False):
        # Colors segons el jugador
        if piece.player.id == 1:
            color = theme.PLAYER_1
            border_color = theme.PLAYER_1_BORDER
        else:
            color = theme.PLAYER_2
            border_color = theme.PLAYER_2_BORDER

        # Enfosquir les peces que ja han actuat
        if darkened:
            color = tuple(int(c * 0.38) for c in color)
            border_color = tuple(int(c * 0.45) for c in border_color)

        # Cos de la peça
        piece_rect = rect.inflate(-8, -8)

        pygame.draw.rect(
            screen, color, piece_rect, border_radius=6
        )

        pygame.draw.rect(
            screen, border_color, piece_rect,
            width=2, border_radius=6
        )

        # Símbol centrat
        symbol_color = (
            (155, 155, 165) if darkened else theme.TEXT
        )

        symbol_font = pygame.font.SysFont(
            theme.FONT_NAME,
            max(16, int(cell_size * 0.32)),
            bold=True
        )

        symbol = symbol_font.render(
            piece.troop.symbol, True, symbol_color
        )

        screen.blit(
            symbol,
            symbol.get_rect(center=piece_rect.center)
        )

        # Quantitat a la part superior dreta
        count_color = (
            theme.TEXT_DISABLED if darkened else theme.TEXT
        )

        count_font = pygame.font.SysFont(
            theme.FONT_NAME,
            max(14, int(cell_size * 0.25)),
            bold=True
        )

        count = count_font.render(
            str(piece.count), True, count_color
        )

        count_rect = count.get_rect(
            top=piece_rect.top + 4,
            right=piece_rect.right - 5
        )

        # Fons fosc arrodonit del nombre
        count_bg = count_rect.inflate(6, 4)

        pygame.draw.rect(
            screen,
            theme.BACKGROUND,
            count_bg,
            border_radius=4
        )

        screen.blit(count, count_rect)