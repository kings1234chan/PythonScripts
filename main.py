import pygame
import math
import random

# 初始化Pygame
pygame.init()

# 設置窗口
width, height = 400, 400
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("迷你高爾夫遊戲（中級版）")

# 顏色定義
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)

# 球同洞設置
ball_pos = [width // 2, height - 50]
ball_size = 10
ball_velocity = [0, 0]
friction = 0.98
holes = [[width // 2, 50, 20]]  # [x, y, size]
current_hole = 0
dragging = False
start_pos = [0, 0]
# 計分同計時
shots = 0
score = 0
font = pygame.font.SysFont(None, 36)
start_time = pygame.time.get_ticks()
time_limit = 60

# 遊戲主循環
running = True
clock = pygame.time.Clock()

while running:
    # 事件處理
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN and not dragging:
            start_pos = event.pos
            dragging = True
        if event.type == pygame.MOUSEBUTTONUP and dragging:
            end_pos = event.pos
            dx = start_pos[0] - end_pos[0]
            dy = start_pos[1] - end_pos[1]
            ball_velocity = [dx * 0.1, dy * 0.1]
            shots += 1
            dragging = False

    # 更新球位置
    ball_pos[0] += ball_velocity[0]
    ball_pos[1] += ball_velocity[1]
    ball_velocity[0] *= friction
    ball_velocity[1] *= friction
    
    # 邊界檢查
    if ball_pos[0] < ball_size // 2:
        ball_pos[0] = ball_size // 2
        ball_velocity[0] = -ball_velocity[0] * 0.8
    if ball_pos[0] > width - ball_size // 2:
        ball_pos[0] = width - ball_size // 2
        ball_velocity[0] = -ball_velocity[0] * 0.8
    if ball_pos[1] < ball_size // 2:
        ball_pos[1] = ball_size // 2
        ball_velocity[1] = -ball_velocity[1] * 0.8
    if ball_pos[1] > height - ball_size // 2:
        ball_pos[1] = height - ball_size // 2
        ball_velocity[1] = -ball_velocity[1] * 0.8

    # 碰撞判斷
    if current_hole < len(holes):
        hole = holes[current_hole]
        dx = ball_pos[0] - hole[0]
        dy = ball_pos[1] - hole[1]
        distance = math.sqrt(dx ** 2 + dy ** 2)
        if distance < (ball_size + hole[2]) / 2:
            score += max(100 - shots * 10, 10)  # 擊球越少分數越高
            shots = 0
            ball_pos = [width // 2, height - 50]  # 重置球位置
            ball_velocity = [0, 0]
            current_hole += 1
            # 生成新洞
            if current_hole >= len(holes):
                new_x = random.randint(50, width - 50)
                new_y = random.randint(50, height // 2)
                holes.append([new_x, new_y, 20])

    # 檢查遊戲結束
    elapsed_time = (pygame.time.get_ticks() - start_time) // 1000
    if elapsed_time >= time_limit:
        print(f"遊戲結束！最終分數：{score}")
        running = False

    # 繪製
    screen.fill(BLACK)
    pygame.draw.circle(screen, WHITE, (int(ball_pos[0]), int(ball_pos[1])), ball_size // 2)
    if current_hole < len(holes):
        pygame.draw.circle(screen, GREEN, (int(holes[current_hole][0]), int(holes[current_hole][1])), holes[current_hole][2] // 2)
    if dragging:
        pygame.draw.line(screen, WHITE, start_pos, pygame.mouse.get_pos(), 2)
    
    # 顯示分數同擊球次數
    score_text = font.render(f"Score: {score}", True, WHITE)
    shots_text = font.render(f"Shots: {shots}", True, WHITE)
    time_text = font.render(f"Time: {time_limit - elapsed_time}", True, WHITE)
    screen.blit(score_text, (10, 10))
    screen.blit(shots_text, (10, 40))
    screen.blit(time_text, (10, 70))
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()