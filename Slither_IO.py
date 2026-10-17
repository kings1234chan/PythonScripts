import pygame
import random
import sys

# Initalize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Set up the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Snake Game")

# Clock for controlling frame rat
clock = pygame.time.Clock()

# Snake properties
snake_block = 20
snake_speed = 15
snake = [(100, 50)] # Initial position of the snake (list of segments)
snake_direction = 'RIGHT'

# Food properties
food_x = random.randrange(0, (SCREEN_WIDTH - snake_block) // snake_block)
food_y = random.randrange(0, (SCREEN_HEIGHT - snake_block) // snake_block)

# Score
score = 0
font = pygame.font.Font(None, 36)

# Game loop variables
game_over = False

# Main game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Handling key presses for snake direction
    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP] and snake_direction != "DOWN":
        snake_direction = "UP"
    if keys[pygame.K_DOWN] and snake_direction != "UP":
        snake_direction = "DOWN"
    if keys[pygame.K_LEFT] and snake_direction != "RIGHT":
        snake_direction = "LEFT"
    if keys[pygame.K_RIGHT] and snake_direction != "LEFT":
        snake_direction = "RIGHT"

    # Move the Snake
    head_x, head_y = snake[0]
    if snake_direction == "UP":
        head_y -= snake_block
    if snake_direction == "DOWN":
        head_y += snake_block
    if snake_direction == "LEFT":
        head_x -= snake_block
    if snake_direction == "RIGHT":
        head_x += snake_block

    # Insert new head at the front of the snake
    new_head = (head_x, head_y)
    snake.insert(0, new_head)

    # Create Rect objects for the snake's head and the food
    snake_head_rect = pygame.Rect(head_x, head_y, snake_block, snake_block)
    food_rect = pygame.Rect(food_x, food_y, snake_block, snake_block)

    # Check if the snake eats food using colliderect
    if snake_head_rect.colliderect(food_rect):
        score += 1
        food_x = random.randrange(0, SCREEN_WIDTH - snake_block, snake_block)
        food_y = random.randrange(0, SCREEN_HEIGHT - snake_block, snake_block)
    else:
        # Remove the tail segment if no food is eaten
        snake.pop()

    # Check for collisions (walls or itself)
    if (
        head_x < 0
        or head_x >= SCREEN_WIDTH
        or head_y < 0
        or head_y >= SCREEN_HEIGHT
        or new_head in snake[1:]
    ):
        game_over = True

    # Drawing everything
    screen.fill(BLACK)

    # Draw food
    pygame.draw.rect(screen, RED, food_rect)

    # Draw snake
    for segment in snake:
        pygame.draw.rect(screen, GREEN, (segment[0], segment[1], snake_block, snake_block))

    # Draw score
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))

    # Check for game over
    if game_over:
        game_over_text = font.render("Game Over! Press R to Restart", True, WHITE)
        screen.blit(game_over_text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2))
        pygame.display.flip()
        
        # Wait for restart
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    # Reset the game state variables
                    snake = [(100, 50)]
                    snake_direction = 'RIGHT'
                    food_x = random.randrange(0, SCREEN_WIDTH - snake_block, snake_block)
                    food_y = random.randrange(0, SCREEN_HEIGHT - snake_block, snake_block)
                    score = 0
                    game_over = False
                    waiting = False

    pygame.display.flip()
    clock.tick(snake_speed)