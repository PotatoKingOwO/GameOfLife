
import pygame
import random

pygame.init()

width = 800
height = 600

cell_size = 5
min_cell_size = 2
max_cell_size = 40

cols = width // cell_size
rows = height // cell_size

camera_x = 0
camera_y = 0

# Posouvání mapy
panning = False
pan_start_mouse = (0, 0)
pan_start_camera = (0, 0)

background_color = (12, 15, 20)
grid_color = (30, 38, 45)

grid = []
running_simulation = False
last_update_time = 0
generation_interval = 250
generation = 0

# Knihovna vzorů
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
        (0, 1),
        (2, 2), (3, 2),
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

screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Game of Life")

font = pygame.font.SysFont(None, 28)
small_font = pygame.font.SysFont(None, 20)
clock = pygame.time.Clock()


def count_neighbors(grid, row, col):
    count = 0

    for i in range(-1, 2):
        for j in range(-1, 2):
            if i == 0 and j == 0:
                continue

            r = (row + i) % rows
            c = (col + j) % cols
            count += grid[r][c]

    return count


def next_generation(grid):
    new_grid = []

    for row in range(rows):
        new_row = []

        for col in range(cols):
            neighbours = count_neighbors(grid, row, col)
            alive = grid[row][col] == 1

            if alive and neighbours in (2, 3):
                new_row.append(1)
            elif not alive and neighbours == 3:
                new_row.append(1)
            else:
                new_row.append(0)

        new_grid.append(new_row)

    return new_grid


def randomize_grid(grid):
    for row in range(rows):
        for col in range(cols):
            grid[row][col] = 1 if random.random() < 0.3 else 0


def clear_grid(grid):
    for row in range(rows):
        for col in range(cols):
            grid[row][col] = 0


def screen_to_cell(pos):
    mouse_x, mouse_y = pos

    col = (mouse_x + camera_x) // cell_size
    row = (mouse_y + camera_y) // cell_size

    if 0 <= row < rows and 0 <= col < cols:
        return row, col

    return None


def place_pattern(pattern_name, anchor_row, anchor_col):
    for dx, dy in PATTERNS[pattern_name]:
        col = anchor_col + dx
        row = anchor_row + dy

        if 0 <= row < rows and 0 <= col < cols:
            grid[row][col] = 1


for row in range(rows):
    grid.append([0] * cols)

randomize_grid(grid)

running = True
selected_pattern = None
show_pattern_menu = False
pattern_names = list(PATTERNS.keys())

while running:
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                selected_pattern = None
                show_pattern_menu = False

            elif event.key == pygame.K_SPACE:
                running_simulation = not running_simulation

            elif event.key == pygame.K_r:
                randomize_grid(grid)
                running_simulation = False
                generation = 0

            elif event.key == pygame.K_c:
                clear_grid(grid)
                running_simulation = False
                generation = 0

            elif event.key == pygame.K_w:
                generation_interval = max(
                    50, generation_interval - 200
                )

            elif event.key == pygame.K_s:
                generation_interval = min(
                    450, generation_interval + 200
                )

            elif event.key == pygame.K_p:
                show_pattern_menu = not show_pattern_menu
                selected_pattern = None

            # Rychlý výběr vzorů klávesami 1–6
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

        # Zoom kolečkem myši
        if event.type == pygame.MOUSEWHEEL:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            old_size = cell_size

            if event.y > 0:
                cell_size = min(max_cell_size, cell_size + 1)
            elif event.y < 0:
                cell_size = max(min_cell_size, cell_size - 1)

            if cell_size != old_size:
                camera_x = int(
                    (mouse_x + camera_x) * cell_size
                    / old_size - mouse_x
                )
                camera_y = int(
                    (mouse_y + camera_y) * cell_size
                    / old_size - mouse_y
                )

                camera_x = max(
                    0, min(camera_x, cols * cell_size - width)
                )
                camera_y = max(
                    0, min(camera_y, rows * cell_size - height)
                )

        if event.type == pygame.MOUSEBUTTONDOWN:

            # Prostřední tlačítko: začni posouvat mapu
            if event.button == 2:
                panning = True
                pan_start_mouse = event.pos
                pan_start_camera = (camera_x, camera_y)

            elif event.button == 1:

                # Kliknutí na položku v nabídce vzorů
                if show_pattern_menu:
                    menu_x, menu_y = 20, 70
                    item_height = 30

                    for index, name in enumerate(pattern_names):
                        rect = pygame.Rect(
                            menu_x,
                            menu_y + index * item_height,
                            260,
                            item_height
                        )

                        if rect.collidepoint(event.pos):
                            selected_pattern = name
                            show_pattern_menu = False
                            break

                else:
                    cell = screen_to_cell(event.pos)

                    if cell is not None:
                        row, col = cell

                        if selected_pattern:
                            place_pattern(
                                selected_pattern, row, col
                            )
                            selected_pattern = None
                        else:
                            grid[row][col] = 1

            # Pravé tlačítko: smazání buňky
            elif event.button == 3:
                if not selected_pattern and not show_pattern_menu:
                    cell = screen_to_cell(event.pos)

                    if cell is not None:
                        row, col = cell
                        grid[row][col] = 0

        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 2:
                panning = False

        if event.type == pygame.MOUSEMOTION:

            if panning:
                dx = pan_start_mouse[0] - event.pos[0]
                dy = pan_start_mouse[1] - event.pos[1]

                camera_x = max(
                    0,
                    min(
                        pan_start_camera[0] + dx,
                        cols * cell_size - width
                    )
                )
                camera_y = max(
                    0,
                    min(
                        pan_start_camera[1] + dy,
                        rows * cell_size - height
                    )
                )

            elif not show_pattern_menu and not selected_pattern:
                buttons = pygame.mouse.get_pressed()

                if buttons[0] or buttons[2]:
                    cell = screen_to_cell(event.pos)

                    if cell is not None:
                        row, col = cell

                        if buttons[0]:
                            grid[row][col] = 1
                        elif buttons[2]:
                            grid[row][col] = 0

    screen.fill(background_color)

    # Vykreslení živých buněk
    for row in range(rows):
        for col in range(cols):
            if grid[row][col] == 1:
                x = col / max(1, cols - 1)
                y = row / max(1, rows - 1)

                red = int(30 + 100 * x)
                green = int(220 - 100 * y)
                blue = int(100 + 155 * (1 - x) * y)

                screen_x = col * cell_size - camera_x
                screen_y = row * cell_size - camera_y

                if (
                    -cell_size < screen_x < width
                    and -cell_size < screen_y < height
                ):
                    pygame.draw.rect(
                        screen,
                        (red, green, blue),
                        (
                            screen_x,
                            screen_y,
                            cell_size,
                            cell_size
                        )
                    )

    # Mřížka
    start_x = (
        int(camera_x // cell_size) * cell_size - camera_x
    )
    start_y = (
        int(camera_y // cell_size) * cell_size - camera_y
    )

    for x in range(int(start_x), width, cell_size):
        pygame.draw.line(
            screen, grid_color, (x, 0), (x, height)
        )

    for y in range(int(start_y), height, cell_size):
        pygame.draw.line(
            screen, grid_color, (0, y), (width, y)
        )

    alive_cells = sum(sum(row) for row in grid)

    status = "RUNNING" if running_simulation else "PAUSED"

    generation_text = font.render(
        f"Generation: {generation}  "
        f"Alive Cells: {alive_cells}  {status}",
        True,
        (255, 255, 255)
    )
    screen.blit(generation_text, (10, 10))

    help_text = small_font.render(
        "SPACE: Play/Pause | R: Random | C: Clear | "
        "W/S: Speed | P: Patterns | Middle mouse: Pan",
        True,
        (190, 200, 210)
    )
    screen.blit(help_text, (10, height - 24))

    # Nápověda při umisťování vzoru
    if selected_pattern:
        hint = small_font.render(
            f"Click to place: {selected_pattern} | ESC: Cancel",
            True,
            (255, 220, 100)
        )
        screen.blit(hint, (10, 38))

        # Náhled vzoru pod kurzorem
        cell = screen_to_cell(pygame.mouse.get_pos())

        if cell is not None:
            anchor_row, anchor_col = cell

            for dx, dy in PATTERNS[selected_pattern]:
                col = anchor_col + dx
                row = anchor_row + dy

                if 0 <= row < rows and 0 <= col < cols:
                    screen_x = col * cell_size - camera_x
                    screen_y = row * cell_size - camera_y

                    pygame.draw.rect(
                        screen,
                        (255, 220, 100),
                        (
                            screen_x,
                            screen_y,
                            cell_size,
                            cell_size
                        ),
                        1
                    )

    # Nabídka vzorů
    if show_pattern_menu:
        menu_x, menu_y = 20, 70
        item_height = 30

        menu_rect = pygame.Rect(
            menu_x,
            menu_y,
            260,
            len(pattern_names) * item_height
        )

        pygame.draw.rect(
            screen, (22, 28, 36), menu_rect
        )
        pygame.draw.rect(
            screen, (80, 100, 115), menu_rect, 1
        )

        for index, name in enumerate(pattern_names):
            rect = pygame.Rect(
                menu_x,
                menu_y + index * item_height,
                260,
                item_height
            )

            pygame.draw.rect(
                screen, (45, 60, 70), rect, 1
            )

            label = small_font.render(
                f"{index + 1}. {name}",
                True,
                (230, 240, 245)
            )
            screen.blit(label, (rect.x + 8, rect.y + 7))

    pygame.display.flip()

    if running_simulation:
        current_time = pygame.time.get_ticks()

        if (
            current_time - last_update_time
            >= generation_interval
        ):
            grid = next_generation(grid)
            generation += 1
            last_update_time = current_time

    clock.tick(60)

pygame.quit()