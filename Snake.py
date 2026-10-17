from ursina import *
import time
import random

# Initialize the Ursina game engine
app = Ursina()

# Game settings
GRID_SIZE = 20
MOVE_SPEED = 0.15
TARGET_SCORE = 200

# Sound effects - NEW!
class GameSounds:
    """Manage all game sound effects"""
    def __init__(self):
        # Check if sounds folder exists
        import os
        self.sounds_available = os.path.exists('sounds')

        if self.sounds_available:
            print("🔊 Sound system initialized - sounds folder found!")
            # Try to load sound files
            try:
                # Pre-load sounds for better performance (optional)
                self.eat_sound = Audio('sounds/eat.wav', autoplay=False, auto_destroy=False)
                self.death_sound = Audio('sounds/death.wav', autoplay=False, auto_destroy=False)
                self.win_sound = Audio('sounds/win.wav', autoplay=False, auto_destroy=False)
                self.explosion_sound = Audio('sounds/explosion.wav', autoplay=False, auto_destroy=False)
                self.start_sound = Audio('sounds/start.wav', autoplay=False, auto_destroy=False)
                print("✅ All sound files loaded successfully.")
                self.preloaded = True
            except Exception as e:
                print(f"⚠️ Could not load all sounds: {e}")
                print("ℹ️ Game will run without audio")
                self.preloaded = False
        else:
            print("ℹ️ Sound system initialized (silent mode)")
            print("ℹ️ To enable sounds: Create 'sounds' folder with .wav files")
            print("ℹ️ See SOUND_FILE_GUIDE.md for download links")
            self.preloaded = False

    def play_eat(self):
        """Play eating sound"""
        try:
            if self.preloaded:
                self.eat_sound.play()
            elif self.sounds_available:
                Audio('sounds/eat.wav', auto_destroy=True)
        except:
            pass

    def play_death(self):
        """Play death sound"""
        try:
            if self.preloaded:
                self.death_sound.play()
            elif self.sounds_available:
                Audio('sounds/death.wav', auto_destroy=True)
        except:
            pass

    def play_win(self):
        """Play victory sound"""
        try:
            if self.preloaded:
                self.win_sound.play()
            elif self.sounds_available:
                Audio('sounds/win.wav', auto_destroy=True)
        except:
            pass

    def play_enemy_hit(self):
        """Play sound when enemy is destroyed"""
        try:
            if self.preloaded:
                self.explosion_sound.play()
            elif self.sounds_available:
                Audio('sounds/explosion.wav', auto_destroy=True)
        except:
            pass

    def play_start(self):
        """Play sound when game starts"""
        try:
            if self.preloaded:
                self.start_sound.play()
            elif self.sounds_available:
                Audio('sounds/start.wav', auto_destroy=True)
        except:
            pass

# Initialize sound system
sounds = GameSounds()

class Snake:
    def __init__(self, is_enemy=False, start_pos=Vec3(0, 0, 0), name=""):
        self.body = []
        self.eyes = []
        self.is_enemy = is_enemy
        self.name = name
        self.direction = Vec3(1, 0, 0)
        self.next_direction = Vec3(1, 0, 0)
        self.alive = True
        self.last_move_time = 0
        self.grow = False

        # Colors
        if is_enemy:
            self.head_color = color.pink
            self.body_color = color.magenta
        else:
            self.head_color = color.lime
            self.body_color = color.green

        # NEW: Create floating name label
        self.label = Entity(
            model=Text(name),
            color=color.white, 
            scale=15,
            position=start_pos + Vec3(0, 3, 0),
            billboard=True,
            unlit=True
        )

        self.create_initial_snake(start_pos)

    def create_initial_snake(self, start_pos):
        for i in range(3):
            segment = Entity(
                model='cube',
                color=self.head_color if i == 0 else self.body_color,
                scale=1,
                position=start_pos + Vec3(-i, 0, 0)
            )
            self.body.append(segment)

    def change_direction(self, new_direction):
        if not self.alive:
            return
        if new_direction != -self.direction:
            self.next_direction = new_direction

    def move(self):
        if not self.alive:
            return

        current_time = time.time()
        if current_time - self.last_move_time < MOVE_SPEED:
            return

        self.last_move_time = current_time
        self.direction = self.next_direction

        if not self.body:
            return
        
        old_head_pos = self.body[0].position
        new_head_pos = self.body[0].position + self.direction

        # Update label position
        if self.label:
            self.label.position = new_head_pos + Vec3(0, 3, 0)

        # CRITICAL FIX: Player dies on wall hit, enemies wrap
        if not self.check_boundaries(new_head_pos):
            if self.is_enemy:
                # Enemies wrap around to avoid getting stuck
                self.wrap_around(new_head_pos)
            else:
                # Player dies when hitting walls!
                self.die()
                return

        if self.check_self_collision(new_head_pos):
            self.die()
            return
        
        # Create new head first
        new_head = Entity(
            model='cube',
            color=self.body[0].color,
            scale=1,
            position=new_head_pos
        )

        # Update colors - old head becomes body color
        if len(self.body) > 0:
            self.body[0].color = self.body_color

        # Insert new head at the beginning
        self.body.insert(0, new_head)

        # Remove tail if not growing
        if not self.grow:
            if len(self.body) > 1:
                tail = self.body.pop()
                destroy(tail)
        else:
            self.grow = False

    def wrap_around(self, position):
        """Wrap enemy around to other side of screen"""
        half_size = GRID_SIZE // 2
        if position.x >= half_size:
            position.x = -half_size + 1
        elif position.x <= -half_size:
            position.x = half_size - 1
        elif position.z >= half_size:
            position.z = -half_size + 1
        elif position.z <= -half_size:
            position.z = half_size - 1

    def check_boundaries(self, position):
        half_size = GRID_SIZE // 2
        return (-half_size < position.x < half_size) and (-half_size < position.z < half_size)

    def check_self_collision(self, head_position):
        for segment in self.body[1:]:
            if distance(head_position, segment.position) < 0.5:
                return True
        return False

    def grow_snake(self):
        """Make the snake grow on the next move"""
        self.grow = True
        # Flash head yellow to show eating
        if self.body:
            old_color = self.head_color
            self.body[0].color = color.yellow
            invoke(lambda: setattr(self.body[0], 'color', old_color) if self.body else None, delay=0.1)
        # NEW: Play eating sound
        sounds.play_eat()

    def die(self):
        self.alive = False
        for segment in self.body:
            segment.color = color.red
        # NEW: Play death sound
        if not self.is_enemy:
            sounds.play_death()

    def destroy(self):
        """NEW: Properly clean up snake"""
        # Destroy all body segments
        for segment in self.body:
            if segment:
                destroy(segment)
        self.body.clear()

        # Destroy label
        if self.label:
            destroy(self.label)
            self.label = None

        # Mark as not alive
        self.alive = False

    def restart(self, start_pos=Vec3(0, 0, 0)):
        self.destroy()

        self.alive = True
        self.direction = Vec3(1, 0, 0)
        self.next_direction = Vec3(1, 0, 0)
        self.grow = False

        # Recreate label
        self.label = Entity(
            model=Text(self.name),
            color=color.white,
            scale=15,
            position=start_pos + Vec3(0, 3, 0),
            billboard=True,
            unlit=True
        )
        
        self.create_initial_snake(start_pos)

class EnemyAI:
    def __init__(self, snake, player_snake):
        self.snake = snake
        self.player_snake = player_snake
        self.last_decision_time = 0
        self.intelligence = 0.7

    def update(self):
        """Make AI decisions for the enemy snake"""
        if not self.snake.alive or not self.snake.body or not self.player_snake.body:
            return
        
        current_time = time.time()
        # Make decisions every 0.8 seconds (slightly slower than movement)
        if current_time - self.last_decision_time < 0.8:
            return
        
        self.last_decision_time = current_time

        # Get position
        enemy_head = self.snake.body[0].position
        player_head = self.player_snake.body[0].position

        # Calculate direction to player
        dx = player_head.x - enemy_head.x
        dz = player_head.z - enemy_head.z

        # Decide whether to be smart or random
        if random.random() < self.intelligence:
            # Smart behavior: move toward player
            self.move_toward_player(dx, dz)
        else:
            # Random behavior: move randomly
            self.move_randomly()

    def move_toward_player(self, dx, dz):
        """Move the enemy toward the player"""
        # Choose the direction that gets closer to player
        if abs(dx) > abs(dz):
            # Move horizontally
            if dx > 0:
                self.snake.change_direction(Vec3(1, 0, 0))  # Right
            else:
                self.snake.change_direction(Vec3(-1, 0, 0))   # Left
        else:
            # Move vertically
            if dz > 0:
                self.snake.change_direction(Vec3(0, 0, 1))  # Forward
            else:
                self.snake.change_direction(Vec3(0, 0, -1))  # Backward

    def move_randomly(self):
        """Move the enemy in a random direction"""
        directions = [
            Vec3(1, 0, 0),
            Vec3(-1, 0, 0),
            Vec3(0, 0, 1),
            Vec3(0, 0, -1)
        ]
        self.snake.change_direction(random.choice(directions))

class Food:
    def __init__(self):
        self.entity = None
        self.spawn_food()

    def spawn_food(self):
        if self.entity:
            destroy(self.entity)

        # Generate random position within boundaries
        half_size = GRID_SIZE // 2 - 2
        x = random.randint(-half_size, half_size)
        z = random.randint(-half_size, half_size)

        self.entity = Entity(
            model='cube',
            color=color.red,
            scale=0.8,
            position=Vec3(x, 0, z)
        )

        self.entity.animate_scale(1.2, duration=0.5, curve=curve.in_out_sine)
        invoke(lambda: self.entity.animate_scale(0.8, duration=0.5, curve=curve.in_out_sine), delay=0.5)

class GameStartScreen:
    """NEW: Game start screen with rules"""
    def __init__(self):
        self.showing = True

        self.title = Text(
            '3D SNAKE BATTLE',
            position=(0, 0.3),
            scale=4,
            origin=(0, 0),
            color=color.white
        )

        rules_text = '''GAME RULES:
        
- WASD to move your snake
- EAT red apples = +10 points
- KILL enemy tails = +50 points (they respawn)
- AVOID: Walls, your tail, enemy attacks
- WIN: Reach 200 points!
- LOSE: Hit wall or get caught by enemies

Controls:
- P = Pause    - R = Restart    - ESC = Quit

Press SPACE to start playing!'''

        self.rules = Text(
            rules_text,
            position=(0, -0.1),
            scale=1.2,
            origin=(0, 0),
            color=color.white
        )

    def hide(self):
        self.showing = False
        destroy(self.title)
        destroy(self.rules)

class GameManager:
    def __init__(self):
        self.score = 0
        self.game_started = False
        self.game_over = False
        self.won = False
        self.enemies = []

        # Start screen
        self.start_screen = GameStartScreen()

        # Game UI (created when game starts)
        self.score_text = None
        self.enemies_text = None
        self.game_over_text = None
        self.win_text = None

    def start_game(self):
        """NEW: Start the actual game"""
        self.game_started = True
        self.start_screen.hide()
        # NEW: Play start sound
        sounds.play_start()

        # Create UI
        self.score_text = Text(
            f'Score: {self.score}/200',
            position=(-0.8, 0.45),
            scale=2,
            color=color.white
        )

        self.enemies_text = Text(
            f'Enemies: {len(self.enemies)}',
            position=(-0.8, 0.35),
            scale=1.5,
            color=color.pink
        )

        self.update_enemy_count()

        self.game_over_text = Text(
            'GAME OVER! Press R to restart',
            position=(0, 0),
            scale=3, 
            color=color.red,
            origin=(0, 0),
            visible=False
        )

        # NEW: Win text
        self.win_text = Text(
            'YOU WIN! 200 POINTS! Press R to play again',
            position=(0, 0),
            scale=3,
            color=color.gold,
            origin=(0, 0),
            visible=False
        )

    def update_score(self, points):
        self.score += points
        if self.score_text:
            self.score_text.text = f'Score: {self.score}/200'

        # NEW: Check win condition
        if self.score >= TARGET_SCORE and not self.won:
            self.win_game()

    def win_game(self):
        """NEW: Handle winning the game"""
        self.won = True
        self.game_over = True
        if self.win_text:
            self.win_text.visible = True
        # NEW: Play victory sound
        sounds.play_win()

        # Create celebration effect
        for _ in range(30):
            particle = Entity(
                model='cube',
                color=color.gold,
                scale=0.3,
                position=player_snake.body[0].position + Vec3(
                    random.uniform(-3, 3),
                    random.uniform(0, -3),
                    random.uniform(-3, 3)
                )       
            )
            particle.animate_position(
                particle.position + Vec3(
                    random.uniform(-8, 8),
                    random.uniform(5, 12),
                    random.uniform(-8, 8)
                ),
                duration=3,
                curve=curve.out_expo
            )
            particle.fade_out(duration=3)

        print("Congratulations! You won the game!")

    def check_food_collision(self):
        """Check if snake ate the food"""
        if not player_snake.alive or not player_snake.body:
            return
        
        food_pos = food.entity.position

        # Player collision
        if player_snake.alive and player_snake.body:
            head_pos = player_snake.body[0].position
            if distance(head_pos, food_pos) < 1.5:
                player_snake.grow_snake()
                food.spawn_food()
                self.update_score(10)

        # Enemy collision
        for enemy in enemies:
            if enemy.alive and enemy.body:
                head_pos = enemy.body[0].position
                if distance(head_pos, food_pos) < 1.5:
                    enemy.grow_snake()
                    food.spawn_food()

    def check_enemy_collisions(self):
        if not player_snake.alive or not player_snake.body:
            return
        
        player_head = player_snake.body[0].position

        for i, enemy in enumerate(enemies):
            if not enemy.alive or not enemy.body:
                continue

            enemy_head = enemy.body[0].position

            # Player hits enemy body
            for segment in enemy.body[1:]:
                if distance(player_head, segment.position) < 0.8:
                    player_snake.die()
                    self.end_game()
                    return
                
            # Enemy hits player body
            for segment in player_snake.body[1:]:
                if distance(enemy_head, segment.position) < 0.8:
                    self.kill_enemy(enemy, i)
                    self.update_score(50)
                    break
                
            # Head collision
            if distance(player_head, enemy_head) < 0.8:
                player_snake.die()
                self.end_game()
                return
            
    def end_game(self):
        """Handle game over"""
        self.game_over = True
        if self.game_over_text:
            self.game_over_text.visible = True

    def update_enemy_count(self):
        """Update the enemy counter on screen"""
        if self.enemies_text:
            alive_count = sum(1 for e in self.enemies if e.alive)
            self.enemies_text.text = f'Enemies: {alive_count}'

    def kill_enemy(self, enemy, enemy_index):
        """NEW: Create explosion effect and respawn enemy"""
        # Play enemy detsroy sound
        sounds.play_enemy_hit()

        # Create explosion effect
        if enemy.body:
            for _ in range(10):
                particle =  Entity(
                    model='cube',
                    color=enemy.body_color,
                    scale=0.2,
                    position=enemy.body[0].position + Vec3(
                        random.uniform(-1, 1),
                        random.uniform(0, 2),
                        random.uniform(-1, 1)
                    )
                )
                particle.animate_position(
                    particle.position + Vec3(
                        random.uniform(-3, 3),
                        random.uniform(1, 4),
                        random.uniform(-3, 3)
                    ),
                    duration=1,
                    curve=curve.out_expo
                )
                particle.fade_out(duration=1)

            # Rsepawn enemy from wall
            self.respawn_enemy(enemy, enemy_index)
            self.update_enemy_count()

    def respawn_enemy(self, enemy, enemy_index):
        """NEW: Respawn enemy from a random wall"""
        # Store enemy name before destruction
        enemy_name = enemy.name
        self.update_enemy_count()

        # Choose a random wall side to spawn from
        sides = ['top', 'bottom', 'left', 'right']
        side = random.choice(sides)

        # Destroy old enemy completely
        enemy.destroy()

        # Create new enemy at wall position
        half_size = GRID_SIZE // 2
        if side == 'top':
            spawn_pos = Vec3(random.randint(-half_size, half_size), 0, half_size)
        elif side == 'bottom':
            spawn_pos = Vec3(random.randint(-half_size, half_size), 0, -half_size)
        elif side == 'left':
            spawn_pos = Vec3(-half_size, 0, random.randint(-half_size, half_size))
        else:
            spawn_pos = Vec3(half_size, 0, random.randint(-half_size, half_size))

        # Create new enemy with fresh instance
        new_enemy = Snake(is_enemy=True, start_pos=spawn_pos, name=enemy_name)

        # Replace in enemies lists immediately
        enemies[enemy_index] = new_enemy
        enemy_ais[enemy_index] = EnemyAI(new_enemy, player_snake)

        new_enemy.alive = True

        print(f"{enemy_name} respawned from {side} wall!")

    def reset_game(self):
        """Reset the game"""
        if not self.game_started:
            self.start_game()
            return
        
        self.score = 0
        self.game_over = False
        self.won = False
        self.update_enemy_count()

        if self.score_text:
            self.update_score(0)
        if self.game_over_text:
            self.game_over_text.visible = False
        if self.win_text:
            self.win_text.visible = False

        food.spawn_food()

class Wall:
    def __init__(self, position, scale):
        self.entity = Entity(
            model='cube',
            color=color.red,
            scale=scale,
            position=position
        )

def create_world():
    """Create the game world"""
    # Ground
    ground = Entity(
        model='cube',
        color=color.black,
        scale=(GRID_SIZE + 2, 1, GRID_SIZE + 2),
        position=(0, -0.5, 0)
    )

    wall_height = 3
    half_size = GRID_SIZE // 2

    for x in range(-half_size - 1, half_size + 2):
        Wall((x, wall_height / 2, half_size + 0.5), (1, wall_height, 1))
        Wall((x, wall_height / 2, -half_size - 0.5), (1, wall_height, 1))

    for z in range(-half_size, half_size + 1):
        Wall((-half_size - 0.5, wall_height / 2, z), (1, wall_height, 1))
        Wall((half_size + 0.5, wall_height / 2, z), (1, wall_height, 1))

def setup_camera():
    camera.position = (0, 45, 0)
    camera.rotation_x = 90
    camera.fov = 60

def input(key):
    if key == 'escape':
        quit()
    elif key == 'space' and not game_manager.game_started:
        game_manager.start_game()
    elif key == 'r':
        # Restart game
        if game_manager.game_started:
            player_snake.restart()
            for i, enemy in enumerate(enemies):
                enemy_positions = [Vec3(8, 0, 8), Vec3(-8, 0, -8), Vec3(-8, 0, 8)]
                enemy.restart(enemy_positions[i])
        game_manager.reset_game()
    elif key == 'p' and game_manager.game_started:
        # Pause functionality could be added here
        pass

    # Movement controls
    if key == 'w':
        player_snake.change_direction(Vec3(0, 0, 1))
    elif key == 's':
        player_snake.change_direction(Vec3(0, 0, -1))
    elif key == 'a':
        player_snake.change_direction(Vec3(-1, 0, 0))
    elif key == 'd':
        player_snake.change_direction(Vec3(1, 0, 0))

def update():
    """Called every frame"""
    if not game_manager.game_started or game_manager.game_over:
        return
    
    player_snake.move()

    # Move enemies and update AI
    for i, enemy in enumerate(enemies):
        if enemy and enemy.alive and enemy.body:
            enemy.move()
            enemy_ais[i].update()

    game_manager.check_food_collision()
    game_manager.check_enemy_collisions()

# === CREATE WORLD & CAMERA ===
create_world()
setup_camera()

# === CREATE PLAYER ===
player_snake = Snake(is_enemy=False, start_pos=Vec3(0, 0, 0), name='PLAYER')

# === CREATE ENEMIES FIRST ===
enemies = []
enemy_ais = []
enemy_positions = [Vec3(8, 0, 8), Vec3(-8, 0, -8)]

for i, pos in enumerate(enemy_positions):
    enemy = Snake(is_enemy=True, start_pos=pos, name=f'ENEMY {i+1}')
    enemy_ai = EnemyAI(enemy, player_snake)
    enemies.append(enemy)
    enemy_ais.append(enemy_ai)

# === CREATE GAME MANAGER (AFTER ENEMIES EXIST) ===
game_manager = GameManager()
game_manager.enemies = enemies  # ✅ Now this works — enemies exist!

# === CREATE FOOD ===
food = Food()

# === CREATE UI INSTRUCTIONS ===
instructions = Text(
    'Move with WASD, avoid red walls!\nR to restart, ESC to quit',
    position=(-0.8, -0.4),
    scale=1.2,
    color=color.white
)

print("Try to hit the walls! Use WASD to move, R to restart.")

# === RUN GAME ===
app.run()
