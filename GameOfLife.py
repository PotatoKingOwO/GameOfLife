import pygame

pygame.init()

width = 800
height = 600

cell_size = 20

screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Game of Life")

clock = pygame.time.Clock()

running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((20, 20, 20))

    # Update the game state here
    for x in range(0, width, cell_size):
        pygame.draw.line(screen, (50, 50, 50), (x, 0), (x, height))
    for y in range(0, height, cell_size):
        pygame.draw.line(screen, (50, 50, 50), (0, y), (width, y))

    pygame.display.flip()
    clock.tick(60)



pygame.quit()