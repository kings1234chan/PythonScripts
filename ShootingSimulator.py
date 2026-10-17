from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import random

app = Ursina()
player = FirstPersonController()
player.gravity = 0
ground = Entity(model='cube', color=color.green, scale=(20, 1, 20))

targets = []
score = 0
score_text = Text(f'Score: {score}', position=(-0.8, 0.45), scale=2, color=color.white)

DirectionalLight(parent=scene, y=2, z=3, shadows=True)
AmbientLight(color=color.rgba(100, 100, 100, 0.1))

Sky()

def spawn_human():
    x = random.uniform(-15, 15)
    z = random.uniform(-15, 15)
    y = 1.5  # Fixed height on ground

    head = Entity(model='cube', color=color.orange, scale=0.7, position=(x, y + 0.9, z))
    body = Entity(model='cube', color=color.red, scale=(0.8, 1.2, 0.5), position=(x, y, z))

    arm_left = Entity(model='cube', color=color.red, scale=(0.3, 0.8, 0.3), position=(x - 0.6, y + 0.1, z))
    arm_right = Entity(model='cube', color=color.red, scale=(0.3, 0.8, 0.3), position=(x + 0.6, y + 0.1, z))

    leg_left = Entity(model='cube', color=color.dark_gray, scale=(0.3, 1.0, 0.3), position=(x - 0.25, y - 1.1, z))
    leg_right = Entity(model='cube', color=color.dark_gray, scale=(0.3, 1.0, 0.3), position=(x + 0.25, y - 1.1, z))

    humanoid_parts = [head, body, arm_left, arm_right, leg_left, leg_right]

    target = body
    target.humanoid_parts = humanoid_parts
    target.target_type = 'human'

    targets.append(target)
    invoke(destroy_target, target, delay=10)

def destroy_target(target):
    if target in targets:
        targets.remove(target)
        if hasattr(target, 'humanoid_parts'):
            for part in target.humanoid_parts:
                destroy(part)
        else:
            destroy(target)

# Bullet list for tracking
bullets = []

def shoot():
    # Position bullet slightly in front of camera to avoid clipping
    bullet_start = camera.world_position + camera.forward * 2
    bullet = Entity(
        model='sphere',
        color=color.yellow,
        scale=0.3,
        position=bullet_start,
    )

    # Fixed: Assign velocity to the individual bullet instance
    bullet.velocity = camera.forward * 25
    bullets.append(bullet)

    invoke(lambda: [destroy(bullet), bullets.remove(bullet)] if bullet in bullets else None, delay=3)

# Flying controls and updates
def update():
    global score

    if held_keys['space']:
        player.y += 5 * time.dt
    if held_keys['shift']:
        player.y -= 5 * time.dt

    for bullet in bullets[:]:
        try:
            bullet.position += bullet.velocity * time.dt

            for target in targets[:]:
                hit = False

                if hasattr(target, 'humanoid_parts'):
                    for part in target.humanoid_parts:
                        if distance(bullet.position, part.position) < 1.5:
                            hit = True
                            break
                else:
                    if distance(bullet.position, target.position) < 2.5:
                        hit = True

                if hit:
                    score += 10
                    score_text.text = f'Score: {score}'

                    if hasattr(target, 'humanoid_parts'):
                        for part in target.humanoid_parts:
                            destroy(part)
                    else:
                        destroy(target)

                    if target in targets:
                        targets.remove(target)
                    destroy(bullet)
                    if bullet in bullets:
                        bullets.remove(bullet)
                    break
        except Exception as e:
            if bullet in bullets:
                bullets.remove(bullet)

def input(key):
    if key == 'r':
        application.quit()
    if key == 'left mouse down':
        shoot()

def spawn_loop():
    spawn_human()
    invoke(spawn_loop, delay=3)

invoke(spawn_loop, delay=3)

app.run()