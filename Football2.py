import pygame, random, math

pygame.init()
W, H = 820, 520
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Football Game")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 28, bold=True)
big = pygame.font.SysFont("Arial", 60, bold=True)

GOAL_H, GOAL_W = 14, 160
GOAL_TOP, GOAL_BOT = H/2 - GOAL_H/2, H/2 + GOAL_H/2
WIN_SCORE = 5

class Circle:
    """One class for players AND the ball: a circle with velocity."""
    def __init__(self, x, y, r, color):
        self.x, self.y, self.r, self.color = x, y, r, color
        self.vx = self.vy = 0
    def clamp(self):
        self.x = min(max(self.x, self.r), W - self.r)
        self.y = min(max(self.y, self.r), H - self.r)
    def draw(self):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.r)
        pygame.draw.circle(screen, (0, 0, 0), (int(self.x), int(self.y)), self.r, 3)

you = Circle(W*0.25, H/2, 18, (40, 129, 240))
cpu = Circle(W*0.75, H/2, 18, (230, 60, 60))
ball = Circle(W/2, H/2, 12, (245, 245, 245))
you_score = cpu_score = 0
msg, msg_timer, state = "", 0, "play"

def reset():
    for c, x in ((ball, W/2), (you, W*0.25), (cpu, W*0.75)):
        c.x, c.y, c.vx, c.vy = x, H/2, 0, 0

def step_ball():
    ball.x += ball.vx; ball.y += ball.vy
    ball.vx *= 0.97; ball.vy *= 0.97
    if ball.y < ball.r: ball.y, ball.vy = ball.r, -ball.vy
    if ball.y > H-ball.r: ball.y, ball.vy = H-ball.r, -ball.vy
    if not GOAL_TOP < ball.y < GOAL_BOT:
        if ball.x < ball.r: ball.x, ball.vx = ball.r, -ball.vx
        if ball.x > W-ball.r: ball.x, ball.vx = W-ball.r, -ball.vx

def kick(m):
    """If player m touches the ball, shove it away from m."""
    dx, dy = ball.x - m.x, ball.y - m.y
    d = math.hypot(dx, dy) or 1
    if d < m.r + ball.r:
        ball.vx = dx/d*9 + m.vx*0.5
        ball.vy = dy/d*9 + m.vy*0.5

def text(s, f, y):
    img = f.render(s, True, (255, 255, 0))
    screen.blit(img, (W/2 - img.get_width()/2, y))

GOAL_LINES = ["GOAL!", "What a strike!", "Top shooter!", "Net buster!"]
SAD_LINES = ["AI scored!", "Oof, conceded", "Keeper napped!", "They punished you"]

reset()
run = True
while run:
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            run = False
        if e.type == pygame.KEYDOWN and e.key == pygame.K_r and state == "over":
            you_score = cpu_score = 0; state = "play"; reset()

    if state == "play":
        # --- your opponent ---
        k = pygame.key.get_pressed()
        you.vx = ((k[pygame.K_RIGHT] or k[pygame.K_d]) - (k[pygame.K_LEFT] or k[pygame.K_a])) * 5
        you.vy = ((k[pygame.K_DOWN] or k[pygame.K_s]) - (k[pygame.K_UP] or k[pygame.K_w])) * 5
        you.x += you.vx; you.y += you.vy; you.clamp()

        # --- AI: stand BEHIND the ball relative to AI goal, so pushes aim at the net ---
        # For the right-side AI goal at x = W, compute vector from goal to ball
        dx, dy = ball.x - W, ball.y - H/2
        d = math.hypot(dx, dy) or 1
        ax, ay = ball.x + dx/d*26 - cpu.x, ball.y + dy/d*26 - cpu.y
        ad = math.hypot(ax, ay) or 1
        cpu.vx, cpu.vy = ax/ad*4, ay/ad*4
        cpu.x += cpu.vx; cpu.y += cpu.vy; cpu.clamp()

        step_ball()
        kick(you); kick(cpu)

        if GOAL_TOP < ball.y < GOAL_BOT and ball.x > W-GOAL_W:
            you_score += 1; msg, msg_timer = random.choice(GOAL_LINES), 90; reset()
        elif GOAL_TOP < ball.y < GOAL_BOT and ball.x < GOAL_W:
            cpu_score += 1; msg, msg_timer = random.choice(SAD_LINES), 90; reset()
        if max(you_score, cpu_score) >= WIN_SCORE: state = "over"

    # --- draw everything ---
    screen.fill((52, 168, 83))
    pygame.draw.rect(screen, (255,255,255), (8, 8, W-16, H-16), 4)
    pygame.draw.line(screen, (255,255,255), (W//2, 8), (W//2, H-8), 4)
    pygame.draw.circle(screen, (255,255,255), (W//2, H//2), 70, 4)
    pygame.draw.rect(screen, (255,235,0), (0, GOAL_TOP, GOAL_W, GOAL_H))
    pygame.draw.rect(screen, (255,255,0), (W-GOAL_W, GOAL_TOP, GOAL_W, GOAL_H))
    for c in (ball, you, cpu): c.draw()
    screen.blit(font.render(f"YOU {you_score}", True, (255,255,0)), (20, 14))
    ai = font.render(f"AI {cpu_score}", True, (255,255,0))
    screen.blit(ai, (W - 20 - ai.get_width(), 14))
    if msg_timer > 0:
        msg_timer -= 1
        text(msg, font, 60)
    if state == "over":
        text("YOU WIN!" if you_score > cpu_score else "AI WINS!", big, H/2-60)
        text("Press R to play again", font, H/2+20)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
