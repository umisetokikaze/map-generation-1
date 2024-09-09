from tile_manager import TILESET


class PlayerManager:
    def __init__(self, game_map, TILE_SIZE):
        self.game_map = game_map
        self.spawn_point = self.find_spawn_point()
        self.tile_size = TILE_SIZE

    def find_spawn_point(self):
        best_spot = None
        max_floor_count = 0

        for y in range(len(self.game_map)):
            for x in range(len(self.game_map[0])):
                if self.game_map[y][x] == TILESET["floor"]:
                    floor_count = self.count_surrounding_floors(x, y)
                    if floor_count > max_floor_count:
                        max_floor_count = floor_count
                        best_spot = (x, y)

        return best_spot

    def count_surrounding_floors(self, x, y):
        count = 0
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < len(self.game_map[0]) and 0 <= ny < len(self.game_map):
                    if self.game_map[ny][nx] == TILESET["floor"]:
                        count += 1
        return count

    def spawn_player(self):
        if self.spawn_point:
            return self.spawn_point[0] * self.tile_size, self.spawn_point[
                1
            ] * self.tile_size
        return None
