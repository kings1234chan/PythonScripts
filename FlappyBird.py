import pygame
import random

pygame.init()
WIDTH, HEIGHT = 400, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird")
clock = pygame.time.Clock()
FPS = 60

# Colors and game variables
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
bird_x, bird_y = 50, HEIGHT // 2
bird_vel = 1
gravity = 0.5
jump = -10
pipe_width = 50
pipe_gap = 200
pipe_freq = 3000
pipes = []
score = 0
font = pygame.font.Font(None,36)
game_over = False

def draw_bird(x, y):
    pygame.draw.circle(screen, WHITE, (int(x), int(y)), 5)

def draw_pipe(x, gap_y):
    pygame.draw.rect(screen, GREEN, (x, 0, pipe_width, gap_y))
    pygame.draw.rect(screen, GREEN, (x, gap_y + pipe_gap, pipe_width, HEIGHT))

running = True
last_pipe = pygame.time.get_ticks()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            if game_over:
                bird_y = HEIGHT // 2
                bird_vel = 0
                pipes = []
                scorer = 0
                game_over = False
            else:
                bird_vel = jump

    if not game_over:
        # Update bird
        bird_vel += gravity
        bird_y += bird_vel

        # Generate pipes
        current_time = pygame.time.get_ticks()
        if current_time - last_pipe > pipe_freq:
            gap_y = random.randint(150, HEIGHT - 150)
            pipes.append([WIDTH, gap_y])
            last_pipe = current_time

        # Update pipes
        for pipe in pipes[:]:
            pipe[0] -= 1
            if pipe[0] < -pipe_width:
                pipes.remove(pipe)
                score += 1

            # Collision detection
            bird_rect = pygame.Rect(bird_x - 5, bird_y - 5, 40, 40)
            pipe_top = pygame.Rect(pipe[0], 0, pipe_width, pipe[1])
            pipe_bottom = pygame.Rect(pipe[0], pipe[1] + pipe_gap, pipe_width, HEIGHT)
            if bird_rect.colliderect(pipe_top) or bird_rect.colliderect(pipe_bottom) or bird_y > HEIGHT or bird_y < 0:
                game_over = True

    # Draw everything
    screen.fill(BLACK)
    for pipe in pipes:
        draw_pipe(pipe[0], pipe[1])
    draw_bird(bird_x, bird_y)
    score_text = font.render(str(score), True, WHITE)
    screen.blit(score_text, ( WIDTH // 2 - 100, HEIGHT // 2))
    if game_over:
        game_over_text = font.render("Game Over! Press SPACE", True, WHITE)
        screen.blit(game_over_text, (WIDTH // 2 - 100, HEIGHT // 2))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()

        