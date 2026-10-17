import pygame, math, random

pygame.init()
W, H = 820, 520
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Tiki-Taka Football")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 24, bold=True)
big = pygame.font.SysFont("Arial", 56, bold=True)

GOAL_H = 170
GOAL_TOP, GOAL_BOT = H/2 - GOAL_H/2, H/2 + GOAL_H/2
WIN = 5
PR, IR, BR = 18, 16, 9

FORMATION = [(90, H/2), (250, 130), (250, H-130), (480, H/2)]

def dist(ax, ay, bx, by):
    return math.hypot(ax - bx, ay - by)

def disc(col, x, y, r, ring=3):
    pygame.draw.circle(screen, col, (int(x), int(y)), r)
    pygame.draw.circle(screen, (0,0,0), (int(x), int(y)), r, ring)

def new_interceptors():
    return [[random.randint(560, 700), random.randint(120, H-120)] for _ in range(3)]

def reset():
    """Reset position for a new possession (keeps the score)"""
    global team, inter, keeper, holder, bx, by, tx, ty, moving, mode, target
    team = [list(p) for p in FORMATION]
    inter = new_interceptors()
    keeper = [W - 42, H/2]
    holder, target = 0, -1
    bx, by = team[0]
    tx, ty = bx, by
    moving, mode = False, "idle"

score = wait = 0
msg, state = "", "play"
GOAL_MSG = ["GOOAL!", "Tiki-taka magic!", "finish!", "Back of the net!"]
LOSE_MSG = ["Intercepted!", "Turnover!", "Lost it!", "Robbed!"]
reset()

def turnover(text):
    global state, wait, msg
    msg, state, wait = random.choice(LOSE_MSG) if text == "lose" else random.choice(GOAL_MSG), "wait", 55

run = True
while run:
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            run = False
        if e.type == pygame.KEYDOWN and e.key == pygame.K_r and state == "over":
            score = 0; state = "play"; reset()
        if e.type == pygame.MOUSEBUTTONDOWN and state == "play" and not moving:
            mx, my = e.pos
            if mx > W - 140 and GOAL_TOP < my < GOAL_BOT + 40:
                mode, target = "shot", -1
                tx, ty, = W - 4, max(GOAL_TOP + 12, min(GOAL_BOT - 12, my))
                moving = True; holder = -1
            else:
                best, bd = -1, 999
                for i, (px, py) in enumerate(team):
                    if i != holder and dist(mx, my, px, py) < 45 and dist(mx, my, px, py) < bd:
                        best, bd = i, dist(mx, my, px, py)
                if best >= 0:
                    mode, target = "pass", best
                    tx, ty = team[best]; moving = True; holder = -1

    if state == "play":
        k = pygame.key.get_pressed()
        if holder >= 0 and not moving:
            team[holder][0] = min(max(team[holder][0] + ((k[pygame.K_RIGHT] or k[pygame.K_d]) - (k[pygame.K_LEFT] or k[pygame.K_a])) * 4, PR), W-PR)
            team[holder][1] = min(max(team[holder][1] + ((k[pygame.K_DOWN] or k[pygame.K_s]) - (k[pygame.K_UP] or k[pygame.K_w]))*4, PR), H-PR)

        if moving:
            dx, dy = tx - bx, ty - by
            d = math.hypot(dx, dy) or 1
            if d < 11:
                bx, by, moving = tx, ty, False
                if mode != "shot": holder = target
                elif GOAL_TOP < by < GOAL_BOT:
                    score += 1
                    if score >= WIN: state, msg = "over", "YOU WIN!"
                    else: turnover("goal")
                else: turnover("lose")
            else:
                bx += dx/d*11; by += dy/d*11
        elif holder >= 0:
            bx, by = team[holder]

        aimx, aimy = (0.3*bx + 0.7*tx, 0.3*by + 0.7*ty) if moving else (bx, by)
        for it in inter + [keeper]:
            spd = 2.5 if it == keeper else 4.5
            ax, ay = (keeper[0], by) if it is keeper else (aimx, aimy)
            dx, dy = ax - it[0], ay - it[1]
            d = math.hypot(dx, dy) or 1
            it[0] += dx/d*spd; it[1] += dy/d*spd
            if dist(bx, by, it[0], it[1]) < IR + BR: turnover("lose"); break
        keeper[1] = max(GOAL_TOP + IR, min(GOAL_BOT - IR, keeper[1]))

    elif state == "wait":
        wait -= 1
        if wait <= 0: state = "play"; reset()

    screen.fill((52, 168, 83))
    pygame.draw.rect(screen, (255,255,255), (8, 8, W-16, H-16), 4)
    pygame.draw.line(screen, (255,255,255), (W//2, 8), (W//2, H-8), 4)
    pygame.draw.circle(screen, (255,255,255), (W//2, H//2), 70, 4)
    pygame.draw.rect(screen, (255,245,0), (W-12, GOAL_TOP, 12, GOAL_H))
    for i, (px, py) in enumerate(team):
        disc((40,120,240), px, py, PR)
        if i != holder: pygame.draw.circle(screen, (255,255,255), (int(px), int(py)), PR+6, 2)
    if holder >= 0:
        pygame.draw.circle(screen, (255,255,0), (int(team[holder][0]), int(team[holder][1])), PR+7, 3)
    for it in inter: disc((230,60,60), it[0], it[1], IR)
    disc((180,30,30), keeper[0], keeper[1], IR+2)
    disc((255,255,255), bx, by, BR, 2)

    screen.blit(font.render(f"Goals: {score}/{WIN}", True, (255,255,0)), (20, 14))
    tip = font.render("Move = arrows/WASD  -  Click teammate = pass  -  Click goal = shoot", True, (255,255,255))
    screen.blit(tip, (W/2 - tip.get_width()/2, H-32))
    if state == "wait":
        t = big.render(msg, True, (255,255,0)); screen.blit(t, (W/2 - t.get_width()/2, H/2 - 40))
    if state == "over":
        t = big.render(msg, True, (255,255,255)); screen.blit(t, (W/2 - t.get_width()/2, H/2 - 60))
        t2 = font.render("Press R to play again", True, (255,255,0))
        screen.blit(t2, (W/2 - t2.get_width()/2, H/2 + 20))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()

