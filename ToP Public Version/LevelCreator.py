import pygame
import sys

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1200  # 30 * 40
SCREEN_HEIGHT = 640  # 16 * 40
CELL_SIZE = 40
GRID_WIDTH = 30
GRID_HEIGHT = 16

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# Initialize screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Grid Color Changer")

# Grid array to store cell colors
grid = [[' ' for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

# Current color selection
current_color = 'g'

def draw_grid():
    for row in range(GRID_HEIGHT):
        for col in range(GRID_WIDTH):
            rect = pygame.Rect(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            if grid[row][col] == 'g':
                pygame.draw.rect(screen, GREEN, rect)
            elif grid[row][col] == 'r':
                pygame.draw.rect(screen, RED, rect)
            else:
                pygame.draw.rect(screen, WHITE, rect)
            pygame.draw.rect(screen, BLACK, rect, 1)

def save_grid_to_file():
    with open("level11.txt", "w") as f:
        f.write("level11 = [\n")
        for row in grid:
            f.write(f'    "{"".join(row)}",\n')
        f.write("]\n")

# Main loop
running = True
mouse_down = False
draw_mode = None  # 'draw' or 'erase'
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            save_grid_to_file()
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                mouse_down = True
                x, y = event.pos
                col = x // CELL_SIZE
                row = y // CELL_SIZE
                if 0 <= col < GRID_WIDTH and 0 <= row < GRID_HEIGHT:
                    if grid[row][col] == current_color:
                        draw_mode = 'erase'
                    else:
                        draw_mode = 'draw'
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # Left click
                mouse_down = False
                draw_mode = None
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                current_color = 'g'
            elif event.key == pygame.K_2:
                current_color = 'r'

    if mouse_down and draw_mode:
        x, y = pygame.mouse.get_pos()
        col = x // CELL_SIZE
        row = y // CELL_SIZE
        if 0 <= col < GRID_WIDTH and 0 <= row < GRID_HEIGHT:
            if draw_mode == 'draw':
                grid[row][col] = current_color
            elif draw_mode == 'erase':
                grid[row][col] = ' '

    screen.fill(WHITE)
    draw_grid()
    pygame.display.flip()
