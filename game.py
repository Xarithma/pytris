import random
import subprocess
import sys


def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])


try:
    import pygame
except:
    install("pygame")
    import pygame


pygame.font.init()

s_width = 800
s_height = 700
play_width = 300  # this / 10 = width
play_height = 600  # this / 20 = height
block_size = 30

top_left_x = (s_width - play_width) // 2
top_left_y = s_height - play_height


# Shapes (pasted)

S = [['.....',
      '......',
      '..00..',
      '.00...',
      '.....'],
     ['.....',
      '..0..',
      '..00.',
      '...0.',
      '.....']]

Z = [['.....',
      '.....',
      '.00..',
      '..00.',
      '.....'],
     ['.....',
      '..0..',
      '.00..',
      '.0...',
      '.....']]

I = [['..0..',
      '..0..',
      '..0..',
      '..0..',
      '.....'],
     ['.....',
      '0000.',
      '.....',
      '.....',
      '.....']]

O = [['.....',
      '.....',
      '.00..',
      '.00..',
      '.....']]

J = [['.....',
      '.0...',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..00.',
      '..0..',
      '..0..',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '...0.',
      '.....'],
     ['.....',
      '..0..',
      '..0..',
      '.00..',
      '.....']]

L = [['.....',
      '...0.',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..0..',
      '..0..',
      '..00.',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '.0...',
      '.....'],
     ['.....',
      '.00..',
      '..0..',
      '..0..',
      '.....']]

T = [['.....',
      '..0..',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..0..',
      '..00.',
      '..0..',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '..0..',
      '.....'],
     ['.....',
      '..0..',
      '.00..',
      '..0..',
      '.....']]

shapes = [S, Z, I, O, J, L, T]

# Colors representing their shapes.
shape_colors = [(0, 255, 0),
                (255, 0, 0),
                (0, 255, 255),
                (255, 255, 0),
                (255, 165, 0),
                (0, 0, 255),
                (128, 0, 128)]


class Piece(object):
    """Main data structure/class."""

    def __init__(self, x, y, shape):
        self.x = x
        self.y = y
        self.shape = shape
        self.color = shape_colors[shapes.index(shape)]
        self.rotation = 0


def update_score(nscore):
    """Updates the score from the scores.txt file."""
    score = max_score()

    with open('scores.txt', 'w') as f:
        if int(score) > nscore:
            f.write(str(score))
        else:
            f.write(str(nscore))


def max_score():
    with open('scores.txt', 'r') as f:
        lines = f.readlines()

    return lines[0].strip()


def create_grid(locked_positions={}):
    """Creates the playfield's gridfield."""
    grid = [[(0, 0, 0) for _ in range(10)] for _ in range(20)]

    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if (j, i) in locked_positions:
                c = locked_positions[(j, i)]
                grid[i][j] = c

    return grid


def convert_shape_format(shape):
    """Converts the shape arrays from dots and 0's to numbers/grid-positions."""
    positions = []

    format = shape.shape[shape.rotation % len(shape.shape)]

    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                positions.append((shape.x + j, shape.y + i))

    for i, pos in enumerate(positions):
        positions[i] = (pos[0] - 2, pos[1] - 4)

    return positions


def valid_space(shape, grid):
    """Validates the shape by it's position."""
    accepted_pos = [[(j, i) for j in range(10)
                     if grid[i][j] == (0, 0, 0)] for i in range(20)]

    accepted_pos = [j for sub in accepted_pos for j in sub]

    for pos in convert_shape_format(shape):
        if pos not in accepted_pos and pos[1] > -1:
            return False

    return True


def check_lost(positions):
    """Checks if any blocks are above the screen."""
    for pos in positions:
        x, y = pos

        if y < 1:
            return True

    return False


def get_shape():
    """Gets a random shape from the `shapes` array."""
    return Piece(5, 0, random.choice(shapes))


def draw_text_middle(text, size, color, surface):
    font = pygame.font.SysFont("Noto Sans", size, bold=True)
    label = font.render(text, 1, color)

    surface.blit(label, (top_left_x + play_width / 2 -
                         (label.get_width() / 2), top_left_y + play_height / 2 - label.get_height() / 2))


def draw_grid(surface, grid):
    """Draws the grid lines through the Pygame renderer."""
    sx = top_left_x
    sy = top_left_y

    # This draws 20 vertical and 10 horizontal lines.
    for i in range(len(grid)):
        pygame.draw.line(surface,
                         (128, 128, 128),  # Color
                         (sx, sy + i*block_size),  # Width
                         (sx + play_width, sy + i*block_size))  # Height

        for j in range(len(grid[i])):
            pygame.draw.line(surface,
                             (128, 128, 128),  # Color
                             (sx + j*block_size, sy),  # Width
                             (sx + j*block_size, sy + play_height))  # Height


def clear_rows(grid, locked):
    """Deletes the row, if that row is filled."""
    increment = 0

    for i in range(len(grid) - 1, -1, -1):
        row = grid[i]

        if (0, 0, 0) not in row:
            increment += 1
            index = i

            for j in range(len(row)):
                try:
                    del locked[(j, i)]
                except:
                    continue

    if increment > 0:
        for key in sorted(list(locked), key=lambda x: x[1])[::-1]:
            x, y = key

            if y < index:
                newKey = (x, y + increment)
                locked[newKey] = locked.pop(key)

    return increment * 1.5


def draw_next_shape(shape, surface):
    """Draws the next shape falling down on the side of the screen."""
    font = pygame.font.SysFont('Noto Sans', 30)
    label = font.render('Next Shape', 1, (255, 255, 255))

    sx = top_left_x + play_width + 50
    sy = top_left_y + play_height / 2 - 100

    format = shape.shape[shape.rotation % len(shape.shape)]

    for i, line in enumerate(format):
        row = list(line)

        for j, column in enumerate(row):
            if column == '0':
                pygame.draw.rect(surface, shape.color,
                                 (sx + j*block_size,
                                  sy + i*block_size,
                                  block_size,
                                  block_size), 0)

    surface.blit(label, (sx - 5, sy - 35))


def draw_window(surface, grid, score=0, last_score=0):
    """Draws the display window on screen. (Called every frame/event)"""
    # TODO: Check if removing the double parenties would be a problem.
    surface.fill((64, 64, 64))

    # --- Top title text START ---
    pygame.font.init()
    font = pygame.font.SysFont('Noto Sans', 48)
    label = font.render('Totros', 1, (255, 255, 255))

    surface.blit(label, (top_left_x + play_width / 2 -
                         (label.get_width() / 2), 15))
    # --- Top title text END ---
    # --------------------------------------------------------------

    # --- Current score text START ---
    font = pygame.font.SysFont('Noto Sans', 30)
    label = font.render(f'Score: {score}', 1, (255, 255, 255))

    sx = top_left_x + play_width + 50
    sy = top_left_y + play_height / 2 - 100

    surface.blit(label, (sx, sy + 250))
    # --- Current score text END ---
    # --------------------------------------------------------------

    # --- High score text START ---
    label = font.render('High Score:', 1, (255, 255, 255))

    sx = top_left_x - 210
    sy = top_left_y + 100

    surface.blit(label, (sx, sy))

    label = font.render(str(last_score), 1, (255, 255, 255))

    sx = top_left_x - 175
    sy = top_left_y + 150

    surface.blit(label, (sx, sy))
    # --- High score text END ---
    # --------------------------------------------------------------
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            pygame.draw.rect(surface, grid[i][j],
                             (top_left_x + j*block_size,
                              top_left_y + i*block_size,
                              block_size, block_size), 0)

    pygame.draw.rect(surface, (255, 0, 0), (top_left_x,
                                            top_left_y,
                                            play_width,
                                            play_height), 4)

    draw_grid(surface, grid)


def main(win):
    """The main function, which takes care of the game's logic."""
    locked_positions = {}
    grid = create_grid(locked_positions)

    change_piece = False

    run = True

    current_piece = get_shape()
    next_piece = get_shape()

    clock = pygame.time.Clock()

    fall_time = 0
    fall_speed = 0.3

    time_passed = 0

    update_time = 0

    score = 0

    while run:
        grid = create_grid(locked_positions)

        time_passed += clock.get_rawtime()
        fall_time += clock.get_rawtime()
        update_time += clock.get_rawtime()
        clock.tick()

        # Side direction insta-lose fix
        if current_piece.y <= 1:
            current_piece.y += 1

        # TODO: Change this, so that the fall rate increases by clearing rows.
        if time_passed / 1000 > 5:
            time_passed = 0

            if fall_speed > 0.1:
                fall_speed -= 0.0075

        if fall_time / 1000 > fall_speed:
            fall_time = 0
            current_piece.y += 1

            if not (valid_space(current_piece, grid)) and current_piece.y > 0:
                current_piece.y -= 1
                change_piece = True

        if update_time / 1000 > 0.05:
            update_time = 0

            keys = pygame.key.get_pressed()

            if keys[pygame.K_DOWN]:
                current_piece.y += 1
                if not(valid_space(current_piece, grid)):
                    current_piece.y -= 1

            if keys[pygame.K_LEFT]:
                current_piece.x -= 1
                if not(valid_space(current_piece, grid)):
                    current_piece.x += 1

            if keys[pygame.K_RIGHT]:
                current_piece.x += 1
                if not(valid_space(current_piece, grid)):
                    current_piece.x -= 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.display.quit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    current_piece.rotation += 1

                    if not(valid_space(current_piece, grid)):
                        current_piece.rotation -= 1

        shape_pos = convert_shape_format(current_piece)

        for i in range(len(shape_pos)):
            x, y = shape_pos[i]

            if y > -1:
                grid[y][x] = current_piece.color

        if change_piece:
            for pos in shape_pos:
                p = (pos[0], pos[1])
                locked_positions[p] = current_piece.color

            current_piece = next_piece
            next_piece = get_shape()
            change_piece = False
            score += clear_rows(grid, locked_positions) * 1000

        last_score = max_score()

        draw_window(win, grid, score, last_score)
        draw_next_shape(next_piece, win)
        pygame.display.update()

        if check_lost(locked_positions):
            draw_text_middle("You Lost!", 80, (255, 255, 255), win)
            pygame.display.update()
            pygame.time.delay(1500)
            run = False
            update_score(score)


def main_menu():
    """Opens the game's main menu. 
    This function is the startup for the game."""

    run = True

    while run:
        win.fill((0, 0, 0))
        draw_text_middle('Press Anything To Play!', 60, (255, 255, 255), win)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                main(win)

    pygame.display.quit()


# TODO: Remove the double parenties.
# Window for the game startup.
win = pygame.display.set_mode((s_width, s_height))
pygame.display.set_caption('Totros')

# Game startup
main_menu()
