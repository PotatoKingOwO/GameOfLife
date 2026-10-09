
import pygame

pygame.init()

width = 800
height = 600

cell_size = 20

cols = width // cell_size
rows = height // cell_size

grid = []

screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Game of Life")

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

            if alive and neighbours < 2:
                new_row.append(0)
            elif alive and neighbours in [2, 3]:
                new_row.append(1)
            elif alive and neighbours > 3:
                new_row.append(0)
            elif not alive and neighbours == 3:
                new_row.append(1)
            else:
                new_row.append(0)
        new_grid.append(new_row)
    return new_grid
for row in range(rows):
    line = []
    for col in range(cols):
        line.append(0)
    grid.append(line)

running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                grid = next_generation(grid)

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos

            col = mouse_x // cell_size
            row = mouse_y // cell_size

            grid[row][col] = 1 - grid[row][col]

    screen.fill((20, 20, 20))

    for row in range(rows):
        for col in range(cols):
            if grid[row][col] == 1:
                pygame.draw.rect(
                    screen,
                    (100, 220, 120),
                    (
                        col * cell_size,
                        row * cell_size,
                        cell_size,
                        cell_size
                    )
                )

    for x in range(0, width, cell_size):
        pygame.draw.line(
            screen, (50, 50, 50), (x, 0), (x, height)
        )

    for y in range(0, height, cell_size):
        pygame.draw.line(
            screen, (50, 50, 50), (0, y), (width, y)
        )

    pygame.display.flip()
    clock.tick(60)



pygame.quit()