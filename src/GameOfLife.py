import random
from collections import deque

import pygame

pygame.init()

WIDTH = 800
HEIGHT = 600
CELL_SIZE = 5
MIN_CELL_SIZE = 2
MAX_CELL_SIZE = 40

camera_x = 0
camera_y = 0
panning = False
pan_start_mouse = (0, 0)
pan_start_camera = (0, 0)

BACKGROUND_COLOR = (12, 15, 20)
GRID_COLOR = (30, 38, 45)
ALIVE_COLOR = (80, 220, 160)
PREVIEW_COLOR = (255, 220, 100)

alive_cells = set()

running_simulation = False
generation_interval = 150
last_update_time = 0
generation = 0

population_history = deque([0], maxlen=400)

PATTERNS = {
    "Glider": [
        (1, 0), (2, 1), (0, 2), (1, 2), (2, 2)
    ],
    "Blinker": [
        (0, 0), (1, 0), (2, 0)
    ],
    "Toad": [
        (1, 0), (2, 0), (3, 0),
        (0, 1), (1, 1), (2, 1)
    ],
    "Beacon": [
        (0, 0), (1, 0),
        (0, 1), (3, 2),
        (2, 3), (3, 3)
    ],
    "Pulsar": [
        *[(x, y) for x in (2, 3, 4, 8, 9, 10)
          for y in (0, 5, 7, 12)],
        *[(x, y) for y in (2, 3, 4, 8, 9, 10)
          for x in (0, 5, 7, 12)]
    ],
    "Gosper Glider Gun": [
        (24, 0),
        (22, 1), (24, 1),
        (12, 2), (13, 2), (20, 2), (21, 2),
        (34, 2), (35, 2),
        (11, 3), (15, 3), (20, 3), (21, 3),
        (34, 3), (35, 3),
        (0, 4), (1, 4), (10, 4), (16, 4),
        (20, 4), (21, 4),
        (0, 5), (1, 5), (10, 5), (14, 5),
        (16, 5), (17, 5), (22, 5), (24, 5),
        (10, 6), (16, 6), (24, 6),
        (11, 7), (15, 7),
        (12, 8), (13, 8)
    ]
}

screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Game of Life — Infinite World")
font = pygame.font.SysFont(None, 28)
small_font = pygame.font.SysFont(None, 20)
clock = pygame.time.Clock()
pattern_names = list(PATTERNS.keys())
selected_pattern = None
show_pattern_menu = False


def count_neighbors(cells, x, y):
    count = 0
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            if (x + dx, y + dy) in cells:
                count += 1
    return count


def next_generation(cells):
    candidates = set()

    for x, y in cells:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                candidates.add((x + dx, y + dy))

    new_cells = set()
    for x, y in candidates:
        neighbors = count_neighbors(cells, x, y)
        is_alive = (x, y) in cells

        if neighbors == 3 or (is_alive and neighbors == 2):
            new_cells.add((x, y))

    return new_cells


def reset_history():
    population_history.clear()
    population_history.append(len(alive_cells))


def clear_world():
    alive_cells.clear()
    reset_history()


def randomize_visible_area():
    alive_cells.clear()
    left = camera_x // CELL_SIZE
    top = camera_y // CELL_SIZE
    right = (camera_x + WIDTH) // CELL_SIZE + 1
    bottom = (camera_y + HEIGHT) // CELL_SIZE + 1

    max_random_cells = 18000000
    if (right - left) * (bottom - top) > max_random_cells:
        center_x = (left + right) // 2
        center_y = (top + bottom) // 2
        half_w = 60
        half_h = 45
        left, right = center_x - half_w, center_x + half_w
        top, bottom = center_y - half_h, center_y + half_h

    for y in range(top, bottom):
        for x in range(left, right):
            if random.random() < 0.22:
                alive_cells.add((x, y))

    reset_history()


def screen_to_cell(pos):
    mouse_x, mouse_y = pos
    world_x = (mouse_x + camera_x) // CELL_SIZE
    world_y = (mouse_y + camera_y) // CELL_SIZE
    return world_x, world_y


def place_pattern(pattern_name, anchor_x, anchor_y):
    for dx, dy in PATTERNS[pattern_name]:
        alive_cells.add((anchor_x + dx, anchor_y + dy))


def draw_cell(x, y, color, outline=0):
    screen_x = x * CELL_SIZE - camera_x
    screen_y = y * CELL_SIZE - camera_y
    if -CELL_SIZE < screen_x < WIDTH and -CELL_SIZE < screen_y < HEIGHT:
        pygame.draw.rect(
            screen,
            color,
            (int(screen_x), int(screen_y), CELL_SIZE, CELL_SIZE),
            outline
        )


def draw_population_graph():
    w = min(260, WIDTH - 20)
    h = min(120, HEIGHT // 3)
    if w < 80 or h < 50:
        return
    x = WIDTH - w - 10
    y = HEIGHT - h - 34

    panel = pygame.Surface((w, h), pygame.SRCALPHA)
    panel.fill((22, 28, 36, 215))
    screen.blit(panel, (x, y))
    pygame.draw.rect(screen, (80, 100, 115), (x, y, w, h), 1)

    data = list(population_history)
    max_v = max(max(data), 1)

    title = small_font.render("Population", True, (190, 200, 210))
    screen.blit(title, (x + 6, y + 4))
    max_label = small_font.render(f"max {max_v}", True, (140, 155, 165))
    screen.blit(max_label, (x + w - max_label.get_width() - 6, y + 4))
    now_label = small_font.render(f"now {data[-1]}", True, ALIVE_COLOR)
    screen.blit(now_label, (x + 6, y + h - now_label.get_height() - 4))

    plot = pygame.Rect(x + 6, y + 24, w - 12, h - 24 - 22)
    pygame.draw.line(screen, GRID_COLOR, (plot.left, plot.bottom), (plot.right, plot.bottom))

    if len(data) >= 2:
        n = len(data)
        points = [
            (
                plot.left + i * (plot.width - 1) / (n - 1),
                plot.bottom - v / max_v * plot.height,
            )
            for i, v in enumerate(data)
        ]
        pygame.draw.lines(screen, ALIVE_COLOR, False, points, 2)


running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.VIDEORESIZE:
            if pygame.version.vernum[0] < 2:
                screen = pygame.display.set_mode(
                    (event.w, event.h), pygame.RESIZABLE
                )
            else:
                screen = pygame.display.get_surface()
            WIDTH, HEIGHT = screen.get_size()

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                selected_pattern = None
                show_pattern_menu = False

            elif event.key == pygame.K_SPACE:
                running_simulation = not running_simulation
                last_update_time = pygame.time.get_ticks()

            elif event.key == pygame.K_r:
                randomize_visible_area()
                running_simulation = False
                generation = 0

            elif event.key == pygame.K_c:
                clear_world()
                running_simulation = False
                generation = 0

            elif event.key == pygame.K_w:
                generation_interval = max(30, generation_interval - 25)

            elif event.key == pygame.K_s:
                generation_interval = min(1000, generation_interval + 25)

            elif event.key == pygame.K_p:
                show_pattern_menu = not show_pattern_menu
                selected_pattern = None

            elif event.key == pygame.K_1:
                selected_pattern = "Glider"
                show_pattern_menu = False
            elif event.key == pygame.K_2:
                selected_pattern = "Blinker"
                show_pattern_menu = False
            elif event.key == pygame.K_3:
                selected_pattern = "Toad"
                show_pattern_menu = False
            elif event.key == pygame.K_4:
                selected_pattern = "Beacon"
                show_pattern_menu = False
            elif event.key == pygame.K_5:
                selected_pattern = "Pulsar"
                show_pattern_menu = False
            elif event.key == pygame.K_6:
                selected_pattern = "Gosper Glider Gun"
                show_pattern_menu = False

        elif event.type == pygame.MOUSEWHEEL:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            old_size = CELL_SIZE

            if event.y > 0:
                CELL_SIZE = min(MAX_CELL_SIZE, CELL_SIZE + 1)
            elif event.y < 0:
                CELL_SIZE = max(MIN_CELL_SIZE, CELL_SIZE - 1)

            if CELL_SIZE != old_size:
                camera_x = int((mouse_x + camera_x) * CELL_SIZE / old_size - mouse_x)
                camera_y = int((mouse_y + camera_y) * CELL_SIZE / old_size - mouse_y)

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 2:  
                panning = True
                pan_start_mouse = event.pos
                pan_start_camera = (camera_x, camera_y)

            elif event.button == 1:  
                if show_pattern_menu:
                    menu_x, menu_y = 20, 70
                    item_height = 30
                    for index, name in enumerate(pattern_names):
                        rect = pygame.Rect(
                            menu_x, menu_y + index * item_height, 260, item_height
                        )
                        if rect.collidepoint(event.pos):
                            selected_pattern = name
                            show_pattern_menu = False
                            break
                else:
                    x, y = screen_to_cell(event.pos)
                    if selected_pattern:
                        place_pattern(selected_pattern, x, y)
                        selected_pattern = None
                    else:
                        alive_cells.add((x, y))

            elif event.button == 3:  # pravé tlačítko = smazání buňky
                if not selected_pattern and not show_pattern_menu:
                    alive_cells.discard(screen_to_cell(event.pos))

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 2:
                panning = False

        elif event.type == pygame.MOUSEMOTION:
            if panning:
                dx = pan_start_mouse[0] - event.pos[0]
                dy = pan_start_mouse[1] - event.pos[1]
                camera_x = pan_start_camera[0] + dx
                camera_y = pan_start_camera[1] + dy
            elif not show_pattern_menu and not selected_pattern:
                buttons = pygame.mouse.get_pressed()
                x, y = screen_to_cell(event.pos)
                if buttons[0]:
                    alive_cells.add((x, y))
                elif buttons[2]:
                    alive_cells.discard((x, y))

    if not running_simulation:
        population_history[-1] = len(alive_cells)

    screen.fill(BACKGROUND_COLOR)

    for x, y in alive_cells:
        screen_x = x * CELL_SIZE - camera_x
        screen_y = y * CELL_SIZE - camera_y
        if -CELL_SIZE < screen_x < WIDTH and -CELL_SIZE < screen_y < HEIGHT:
            gx = max(0.0, min(1.0, screen_x / max(1, WIDTH)))
            gy = max(0.0, min(1.0, screen_y / max(1, HEIGHT)))
            red = int(35 + 65 * gx)
            green = int(190 + 40 * (1 - gy))
            blue = int(130 + 100 * gy)
            pygame.draw.rect(
                screen, (red, green, blue),
                (int(screen_x), int(screen_y), CELL_SIZE, CELL_SIZE)
            )

    start_x = -(camera_x % CELL_SIZE)
    start_y = -(camera_y % CELL_SIZE)
    for x in range(int(start_x), WIDTH, CELL_SIZE):
        pygame.draw.line(screen, GRID_COLOR, (x, 0), (x, HEIGHT))
    for y in range(int(start_y), HEIGHT, CELL_SIZE):
        pygame.draw.line(screen, GRID_COLOR, (0, y), (WIDTH, y))

    draw_population_graph()

    status = "RUNNING" if running_simulation else "PAUSED"
    generation_text = font.render(
        f"Generation: {generation}  Alive Cells: {len(alive_cells)}  {status}",
        True, (255, 255, 255)
    )
    screen.blit(generation_text, (10, 10))

    help_text = small_font.render(
        "SPACE: Play/Pause | R: Random | C: Clear | W/S: Speed | P: Patterns | 1-6 Quick Patterns | Middle mouse: Pan",
        True, (190, 200, 210)
    )
    screen.blit(help_text, (10, HEIGHT - 24))

    if selected_pattern:
        hint = small_font.render(
            f"Click to place: {selected_pattern} | ESC: Cancel",
            True, PREVIEW_COLOR
        )
        screen.blit(hint, (10, 38))
        anchor_x, anchor_y = screen_to_cell(pygame.mouse.get_pos())
        for dx, dy in PATTERNS[selected_pattern]:
            draw_cell(anchor_x + dx, anchor_y + dy, PREVIEW_COLOR, 1)

    if show_pattern_menu:
        menu_x, menu_y = 20, 70
        item_height = 30
        menu_rect = pygame.Rect(
            menu_x, menu_y, 260, len(pattern_names) * item_height
        )
        pygame.draw.rect(screen, (22, 28, 36), menu_rect)
        pygame.draw.rect(screen, (80, 100, 115), menu_rect, 1)

        for index, name in enumerate(pattern_names):
            rect = pygame.Rect(
                menu_x, menu_y + index * item_height, 260, item_height
            )
            pygame.draw.rect(screen, (45, 60, 70), rect, 1)
            label = small_font.render(
                f"{index + 1}. {name}", True, (230, 240, 245)
            )
            screen.blit(label, (rect.x + 8, rect.y + 7))

    pygame.display.flip()

    if running_simulation:
        current_time = pygame.time.get_ticks()
        if current_time - last_update_time >= generation_interval:
            alive_cells = next_generation(alive_cells)
            generation += 1
            population_history.append(len(alive_cells))
            last_update_time = current_time

    clock.tick(60)

pygame.quit()