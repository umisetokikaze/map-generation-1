import math
import random
import pygame
import tile
from tile_manager import TILESET, GENERATION_PARAMS

from player_manager import PlayerManager

pygame.init()

# ウィンドウの設定
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Hack and Slash Game")

# タイルの設定
TILE_SIZE = 6
MAP_WIDTH = SCREEN_WIDTH // TILE_SIZE
MAP_HEIGHT = SCREEN_HEIGHT // TILE_SIZE


def apply_cellular_automata(
    map, iterations=GENERATION_PARAMS["cellular_automata"]["iterations"]
):
    for _ in range(iterations):
        new_map = [row[:] for row in map]
        for y in range(MAP_HEIGHT):
            for x in range(MAP_WIDTH):
                neighbors = count_neighbors(map, x, y)
                current_tile = map[y][x]

                if current_tile.find_attribute("terrain_type").value == "liquid":
                    if (
                        neighbors["ground"]
                        > GENERATION_PARAMS["cellular_automata"][
                            "water_to_floor_threshold"
                        ]
                    ):
                        new_map[y][x] = next(
                            tile
                            for tile in TILESET.values()
                            if tile.find_attribute("terrain_type").value == "ground"
                        )
                elif current_tile.find_attribute("terrain_type").value == "ground":
                    if (
                        neighbors["liquid"]
                        > GENERATION_PARAMS["cellular_automata"][
                            "floor_to_water_threshold"
                        ]
                    ):
                        new_map[y][x] = next(
                            tile
                            for tile in TILESET.values()
                            if tile.find_attribute("terrain_type").value == "liquid"
                        )
                    elif (
                        neighbors["solid"]
                        > GENERATION_PARAMS["cellular_automata"][
                            "floor_to_wall_threshold"
                        ]
                    ):
                        new_map[y][x] = next(
                            tile
                            for tile in TILESET.values()
                            if tile.find_attribute("terrain_type").value == "solid"
                        )
                elif current_tile.find_attribute("terrain_type").value == "solid":
                    if (
                        neighbors["ground"]
                        > GENERATION_PARAMS["cellular_automata"][
                            "wall_to_floor_threshold"
                        ]
                    ):
                        new_map[y][x] = next(
                            tile
                            for tile in TILESET.values()
                            if tile.find_attribute("terrain_type").value == "ground"
                        )
        map = new_map
    return map


def count_neighbors(map, x, y):
    neighbors = {"liquid": 0, "ground": 0, "solid": 0}
    for dy in [-1, 0, 1]:
        for dx in [-1, 0, 1]:
            if dx == 0 and dy == 0:
                continue
            nx, ny = x + dx, y + dy
            if 0 <= nx < MAP_WIDTH and 0 <= ny < MAP_HEIGHT:
                terrain_type = map[ny][nx].find_attribute("terrain_type").value
                neighbors[terrain_type] += 1
    return neighbors


def diamond_square(size, roughness=GENERATION_PARAMS["diamond_square"]["roughness"]):
    # マップを初期化
    map = [[0 for _ in range(size)] for _ in range(size)]

    # 四隅に初期値を設定
    map[0][0] = random.random()
    map[0][size - 1] = random.random()
    map[size - 1][0] = random.random()
    map[size - 1][size - 1] = random.random()

    step = size - 1
    while step > 1:
        half = step // 2

        # Diamond step
        for y in range(half, size, step):
            for x in range(half, size, step):
                square_avg = (
                    map[y - half][x - half]
                    + map[y - half][x + half]
                    + map[y + half][x - half]
                    + map[y + half][x + half]
                ) / 4
                map[y][x] = square_avg + random.uniform(-1, 1) * roughness

        # Square step
        for y in range(0, size, half):
            for x in range((y + half) % step, size, step):
                diamond_avg = (
                    map[(y - half) % size][x]
                    + map[(y + half) % size][x]
                    + map[y][(x - half) % size]
                    + map[y][(x + half) % size]
                ) / 4
                map[y][x] = diamond_avg + random.uniform(-1, 1) * roughness

        roughness /= 2
        step //= 2

    return map


def generate_map():
    size = 2 ** math.ceil(math.log2(max(MAP_WIDTH, MAP_HEIGHT))) + 1
    height_map = diamond_square(size, GENERATION_PARAMS["diamond_square"]["roughness"])

    scale_x = MAP_WIDTH / size
    scale_y = MAP_HEIGHT / size

    new_map = [[None for _ in range(MAP_WIDTH)] for _ in range(MAP_HEIGHT)]

    for y in range(MAP_HEIGHT):
        for x in range(MAP_WIDTH):
            height = height_map[int(y / scale_y)][int(x / scale_x)]
            if height < GENERATION_PARAMS["generate_map"]["water_threshold"]:
                terrain_type = "liquid"
            elif height < GENERATION_PARAMS["generate_map"]["floor_threshold"]:
                terrain_type = "ground"
            else:
                terrain_type = "solid"

            possible_tiles = [
                tile
                for tile in TILESET.values()
                if tile.has_attribute("terrain_type")
                and tile.find_attribute("terrain_type").value == terrain_type
            ]
            new_map[y][x] = random.choice(possible_tiles)

    new_map = apply_cellular_automata(new_map)
    return new_map


# マップを生成
game_map = generate_map()
# プレイヤースポーン
player_manager = PlayerManager(game_map, TILE_SIZE)
spawn_x, spawn_y = player_manager.spawn_player()
if spawn_x and spawn_y:
    player = pygame.Rect(spawn_x, spawn_y, TILE_SIZE, TILE_SIZE)
else:
    print("適切なスポーン地点が見つかりませんでした。")
player_speed = 0.6


# プレイヤーの移動関数を追加
def move_player(dx, dy):
    global player
    new_x = player.x + dx
    new_y = player.y + dy

    # マップの境界チェック
    if new_x < 0:
        new_x = 0
    elif new_x > SCREEN_WIDTH - player.width:
        new_x = SCREEN_WIDTH - player.width

    if new_y < 0:
        new_y = 0
    elif new_y > SCREEN_HEIGHT - player.height:
        new_y = SCREEN_HEIGHT - player.height
    tile_x = int(new_x // TILE_SIZE)
    tile_y = int(new_y // TILE_SIZE)
    current_tile = game_map[tile_y][tile_x]
    if (
        current_tile.has_attribute("passable")
        and current_tile.find_attribute("passable").value
    ):
        # タイルを通過できる処理
        player.x = new_x
        player.y = new_y


# マップ描画関数
def draw_map():
    for row in range(MAP_HEIGHT):
        for col in range(MAP_WIDTH):
            tile = game_map[row][col]
            pygame.draw.rect(
                screen,
                tile.color,
                (col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE),
            )


# ゲームループ
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # プレイヤーの移動

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        move_player(-player_speed, 0)
    if keys[pygame.K_RIGHT]:
        move_player(player_speed, 0)
    if keys[pygame.K_UP]:
        move_player(0, -player_speed)
    if keys[pygame.K_DOWN]:
        move_player(0, player_speed)

    # 画面の描画
    screen.fill((0, 0, 0))  # 背景を黒で塗りつぶす
    draw_map()  # マップを描画
    pygame.draw.rect(screen, (255, 0, 0), player)  # プレイヤーを赤い四角で描画

    pygame.display.flip()

pygame.quit()
