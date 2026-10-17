import pygame, random, math

pygame.init()
W, H = 700, 500
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("🍺 Drunk Aim")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 24, bold=True)
big_font = pygame.font.SysFont("Arial", 40, bold=True)

# Game state
target = [W // 2, H // 2]
target_dir = [random.choice([-2, 2]), random.choice([-2, 2])]
score = 0
shots = 0
messages = []  # floating text : [x, y, text, life, color]
t = 0  # time couner for wobble

def drunk_offset(time_tick):
    """Calculate the drunk wobble offset using sin waves + randomness."""
    wobble_x = math.sin(time_tick * 0.05) * 30 + random.randint(-15, 15)
    wobble_y = math.cos(time_tick * 0.07) * 30 + random.randint(-15, 15)
    return int(wobble_x), int(wobble_y)

def add_msg(x, y, text, color):
    messages.append([x, y, text, 60, color])

running = True
while running:
    t += 1
    mx, my = pygame.mouse.get_pos()
    ox, oy = drunk_offset(t)
    aim_x, aim_y = mx + ox, my + oy  # where the shot will ACTUALLY land

    # Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            shots += 1
            dist = math.hypot(aim_x - target[0], aim_y - target[1])
            if dist < 15:
                score += 10
                add_msg(aim_x, aim_y, "BULLSEYE! + 10", (255, 215, 0))
            elif dist < 30:
                score += 5
                add_msg(aim_x, aim_y, "Hit! +5", (100, 255, 100))
            elif dist < 50:
                score += 1
                add_msg(aim_x, aim_y, "+1", (200, 200, 200))
            else:
                add_msg(aim_x, aim_y, random.choice(["MISS!", "BRUH", "HOW?!", "choke*"]),
                        (255, 80, 80))
                
    # Move target (bouncing)
    target[0] += target_dir[0]
    target[1] += target_dir[1]
    if target[0] < 50 or target[0] > W - 50: target_dir[0] *= -1
    if target[1] < 50 or target[1] > H - 50: target_dir[1] *= -1

    # Draw
    screen.fill((30, 20, 50))

    # Target (bullseye rings)
    pygame.draw.circle(screen, (255, 255, 255), target, 50)
    pygame.draw.circle(screen, (200, 0, 0), target, 40)
    pygame.draw.circle(screen, (255, 255, 255), target, 30)
    pygame.draw.circle(screen, (200, 0, 0), target, 20)
    pygame.draw.circle(screen, (255, 215, 0), target, 10)

    # Wobbly line from mouse to drunk crosshair (shows the offset)
    pygame.draw.line(screen, (100, 100, 100), (mx, my), (aim_x, aim_y), 2)

    # Real mouse position (small dot)
    pygame.draw.circle(screen, (150, 150, 150), (mx, my), 3)

    # Drunk crosshair (where shot actually lands)
    pygame.draw.circle(screen, (255, 50, 50), (aim_x, aim_y), 12, 2)
    pygame.draw.line(screen, (255, 50, 50), (aim_x - 15, aim_y), (aim_x + 15, aim_y), 2)
    pygame.draw.line(screen, (255, 50, 50), (aim_x, aim_y - 15), (aim_x, aim_y + 15), 2)

    # Floating messages
    for m in messages[:]:
        m[1] -= 1
        m[3] -= 1
        text = font.render(m[2], True, m[4])
        screen.blit(text, (m[0] - text.get_width() // 2, m[1]))
        if m[3] <= 0:
            messages.remove(m)

    # HUD
    accuracy = int(score / max(shots, 1) * 10) if shots else 0
    screen.blit(big_font.render(f"Score: {score}", True, (255, 215, 0)), (15, 10))
    screen.blit(font.render(f"Shots: {shots}  |  Accuracy: {accuracy}%",
                            True, (200, 200, 200)), (15, 55))
    screen.blit(font.render("🍺 You're drunk. Click to shoot anyway.",
                            True, (180, 180, 220)), (15, H - 30))
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
