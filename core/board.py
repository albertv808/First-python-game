from collections import deque


class Board:
    def __init__(self, width=10, height=10):
        self.width = width
        self.height = height
        self.grid = [[None for _ in range(width)] for _ in range(height)]

    def in_bounds(self, x, y):
        return 0 <= x < self.width and 0 <= y < self.height

    def get_piece(self, x, y):
        if not self.in_bounds(x, y):
            return None
        return self.grid[y][x]

    def place_piece(self, piece, x, y):
        if not self.in_bounds(x, y):
            return False
        if self.grid[y][x] is not None:
            return False

        self.grid[y][x] = piece
        piece.x, piece.y = x, y
        return True

    def move_piece(self, piece, x, y):
        if not self.in_bounds(x, y):
            return False
        if self.grid[y][x] is not None:
            return False

        self.grid[piece.y][piece.x] = None
        self.grid[y][x] = piece

        piece.x, piece.y = x, y
        return True

    def attack(self, attacker, target):
        damage = max(0, attacker.get_damage() - target.get_defence())

        target.take_damage(damage, self)

    def get_valid_moves(self, piece):
        if piece is None or not piece.is_alive:
            return []

        max_steps = piece.troop.movement

        if max_steps <= 0:
            return []

        # Moviment ortogonal: dreta, esquerra, avall i amunt.
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]

        # BFS: coordenades i distància recorreguda.
        queue = deque([(piece.x, piece.y, 0)])
        visited = {(piece.x, piece.y)}
        moves = []

        while queue:
            x, y, steps = queue.popleft()

            if steps >= max_steps:
                continue

            for dx, dy in directions:
                nx = x + dx
                ny = y + dy

                if not self.in_bounds(nx, ny):
                    continue

                if (nx, ny) in visited:
                    continue

                # Cap peça pot ser travessada ni ocupada.
                if self.get_piece(nx, ny) is not None:
                    continue

                visited.add((nx, ny))
                moves.append((nx, ny))

                queue.append((nx, ny, steps + 1))

        return moves

    def get_valid_attacks(self, piece, enemy_player):
        attacks = []

        for y in range(self.height):
            for x in range(self.width):
                target = self.get_piece(x, y)

                if target and target.player == enemy_player:
                    dist = abs(piece.x - x) + abs(piece.y - y)
                    if dist <= piece.troop.attack_range:
                        attacks.append((x, y))

        return attacks
