import pygame


class Grid:
    """
    Graella visual genèrica.

    No coneix res de tropes, jugadors ni GameState.
    Només gestiona la representació i la conversió
    entre píxels i coordenades de cel·la.
    """

    def __init__(self, x, y, width, height, cell_size, background_color=(60, 60, 65), line_color=(20, 20, 20)):
        self.x = x
        self.y = y

        self.width = width
        self.height = height

        self.cell_size = cell_size

        self.background_color = background_color
        self.line_color = line_color

        self.highlighted_cells = {}

    def set_geometry(self, x, y, width, height, cell_size):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.cell_size = cell_size

    def get_rect(self):
        return pygame.Rect(int(self.x), int(self.y), int(self.width * self.cell_size),
            int(self.height * self.cell_size))

    def get_cell_rect(self, x, y):
        return pygame.Rect(int(self.x + x * self.cell_size), int(self.y + y * self.cell_size), int(self.cell_size),
            int(self.cell_size))

    def get_cell_at(self, mouse_pos):
        """
        Converteix una posició de ratolí en (x, y).

        Retorna None si està fora de la graella.
        """

        mx, my = mouse_pos

        if not self.get_rect().collidepoint(mx, my):
            return None

        x = int((mx - self.x) / self.cell_size)

        y = int((my - self.y) / self.cell_size)

        if not (0 <= x < self.width and 0 <= y < self.height):
            return None

        return x, y

    def set_cell_color(self, x, y, color):
        self.highlighted_cells[(x, y)] = color

    def clear_cell_colors(self):
        self.highlighted_cells.clear()

    def draw(self, screen):
        for y in range(self.height):
            for x in range(self.width):
                rect = self.get_cell_rect(x, y)

                color = self.highlighted_cells.get((x, y), self.background_color)

                pygame.draw.rect(screen, color, rect)

                pygame.draw.rect(screen, self.line_color, rect, 1)
