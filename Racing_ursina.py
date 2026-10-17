from ursina import *
import random

app = Ursina()
camera.position, camera.rotation_x = (0, 5, -10), 15

Entity(model='cube', color=color.dark_gray, scale=(50, 0.1, 100), position=(0, -1, 0))
Entity(model='cube', color=color.red, scale=(1, 2, 100), position=(-15, 0, 0))
Entity(model='cube', color=color.red, scale=(1, 2, 100), position=(15, 0, 0))
Entity(model='cube', color=color.yellow, scale=(30, 0.2, 1), position=(0, 0, 45))
Text('FINISH LINE', position=(0, 2, 45), scale=5, color=color.yellow, billboard=True)

player = Entity(model='cube', color=color.blue, scale=(1, 0.5, 2), position=(0, 0, -40))
player.speed, player.ax_speed, player.acceleration, player.friction = 0, 20, 0.5, 0.95

ai_cars = []
for i in range(8):
    ai_car = Entity(model='cube', color=color.random_color(), scale=(1, 0.5, 2))
    ai_car.position = (random.uniform(-10, 10), 0, random.uniform(10, 30))
    ai_car.speed = random.uniform(8, 12)
    ai_cars.append(ai_car)

game_over, finish_line, score, win_text = False, 45, 0, None
race_started, start_time, race_time, final_time = False, 0, 0, 0

speed_text = Text('Speed: 0', position=(-0.8, 0.4), scale=2)
score_text = Text('Distance: 0', position=(-0.8, 0.35), scale=2)
timer_text = Text('Time: 0.0s', position=(-0.8, 0.3), scale=2)
Text('WASD to move, Space to brake', position=(-0.5, -0.4), scale=1.5)
Text('Race Game - Drive to the Finish line!', position=(-0.4, 0.45), scale=2, color=color.yellow)

def input(key):
    global game_over, score, win_text, race_started, start_time, race_time, final_time
    if key == 'r' and game_over:
        player.position, player.speed, score = (0, 0, -40), 0, 0
        race_started, start_time, race_time, final_time = False, 0, 0, 0
        camera.position = (0, 5, -50)
        for ai_car in ai_cars:
            ai_car.position = (random.uniform(-10, 10), 0, random.uniform(10, 30))
            ai_car.speed = random.uniform(8, 12)
        if win_text:
            destroy(win_text)
            win_text = None
        game_over = False
def update():
    global game_over, score, win_text, race_started, start_time, race_time, final_time
    if race_started:
        race_time = time.time() - start_time

    if game_over:
         return
     
    if not race_started and (held_keys['w'] or held_keys['s'] or held_keys['a'] or held_keys['d']):
        race_started = True
        start_time = time.time()

    if held_keys['w']: player.speed = min(player.speed + player.acceleration, player.max_speed)
    if held_keys['s']: player.speed = max(player.speed - player.acceleration, -player.max_speed)
    if held_keys['a'] and player.x > -14: player.x -= 15 * time.dt
    if held_keys['d'] and player.x < 14: player.x += 15 * time.dt
    if held_keys['space']: player.speed *= 0.9
    player.max_speed = 10

    player.speed *= player.friction
    player.z += player.speed * time.dt
    camera.position = (player.x, 5, player.z - 10)

    for ai_car in ai_cars:
        ai_car.z -= ai_car.speed * time.dt
        if ai_car.z < player.z - 50:
            ai_car.z = player.z + random.uniform(30, 50)
            ai_car.x = random.uniform(-10, 10)
            ai_car.speed = random.uniform(8, 12)

    for ai_car in ai_cars:
        if distance(player, ai_car) < 2:
            player.speed *= -0.5
            ai_car.color = color.orange
            invoke(setattr, ai_car, 'color', color.random_color(), delay=0.2)

    if abs(player.x) > 14: player.speed *= 0.8

    score = int(player.z + 40)
    speed_text.text = f'Speed: {int(abs(player.speed))}'
    score_text.text = f'Distance: {score}'
    timer_text.text = f'Time: {race_time:.1f}s' if race_started else 'Time: 0.0s'
    
    if player.z > finish_line and not game_over:
        game_over, final_time = True, race_time
        win_text = Text(f'YOU WIN!\nTime: {final_time:.2f}s\nPress R to restart', position=(-0.3, 0), scale=3, color=color.green)
    
app.run()