<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tower Defense HTML5</title>
    <style>
        body {
            margin: 0;
            padding: 0;
            background-color: #2c3e50;
            color: #ecf0f1;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            display: flex;
            flex-direction: column;
            align-items: center;
            height: 100vh;
        }
        #ui-bar {
            width: 800px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            background-color: #34495e;
            padding: 10px 20px;
            box-sizing: border-box;
            border-bottom: 3px solid #2980b9;
        }
        .stats {
            display: flex;
            gap: 20px;
            font-size: 1.2rem;
            font-weight: bold;
        }
        .controls {
            display: flex;
            gap: 10px;
        }
        button {
            padding: 8px 16px;
            font-size: 1rem;
            font-weight: bold;
            color: white;
            background-color: #2980b9;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            transition: background-color 0.2s;
        }
        button:hover {
            background-color: #3498db;
        }
        button.active {
            background-color: #e67e22;
        }
        #canvas-container {
            position: relative;
            width: 800px;
            height: 600px;
            background-color: #78e08f; /* Grass */
            box-shadow: 0 4px 15px rgba(0,0,0,0.5);
            cursor: crosshair;
        }
        canvas {
            display: block;
        }
    </style>
</head>
<body>

    <div id="ui-bar">
        <div class="stats">
            <div>Lives: <span id="lives">20</span></div>
            <div>Gold: $<span id="gold">100</span></div>
            <div>Wave: <span id="wave">1</span></div>
        </div>
        <div class="controls">
            <button id="btn-build">Buy Tower ($50)</button>
            <button id="btn-pause">Pause</button>
            <button id="btn-speed">Speed: 1x</button>
        </div>
    </div>

    <div id="canvas-container">
        <canvas id="gameCanvas" width="800" height="600"></canvas>
    </div>

    <script>
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        
        // UI Elements
        const livesEl = document.getElementById('lives');
        const goldEl = document.getElementById('gold');
        const waveEl = document.getElementById('wave');
        const btnBuild = document.getElementById('btn-build');
        const btnPause = document.getElementById('btn-pause');
        const btnSpeed = document.getElementById('btn-speed');

        // Game State
        let lives = 20;
        let gold = 100;
        let wave = 1;
        let isPaused = false;
        let speedMultiplier = 1;
        let buildMode = false;
        const towerCost = 50;
        
        let lastTime = performance.now();
        let waveTimer = 0;
        let enemiesToSpawn = 5;
        let spawnCooldown = 1000;
        let spawnTimer = 0;

        // Path Definition (Center points of the road)
        const path = [
            {x: 0, y: 150},
            {x: 300, y: 150},
            {x: 300, y: 450},
            {x: 600, y: 450},
            {x: 600, y: 250},
            {x: 800, y: 250}
        ];
        const pathWidth = 40;

        // Game Arrays
        const enemies = [];
        const towers = [];
        const projectiles = [];
        const particles = [];

        // Classes
        class Enemy {
            constructor(hp, speed) {
                this.x = path[0].x - 20;
                this.y = path[0].y;
                this.pathIndex = 0;
                this.maxHp = hp;
                this.hp = hp;
                this.speed = speed;
                this.radius = 12;
            }

            update(dt) {
                const target = path[this.pathIndex + 1];
                if (!target) return;

                const dx = target.x - this.x;
                const dy = target.y - this.y;
                const distance = Math.hypot(dx, dy);
                const moveDist = this.speed * dt * speedMultiplier;

                if (distance < moveDist) {
                    this.x = target.x;
                    this.y = target.y;
                    this.pathIndex++;
                    if (this.pathIndex >= path.length - 1) {
                        this.hp = 0; // Destroy
                        lives--;
                        livesEl.innerText = lives;
                    }
                } else {
                    this.x += (dx / distance) * moveDist;
                    this.y += (dy / distance) * moveDist;
                }
            }

            draw(ctx) {
                ctx.fillStyle = '#e74c3c';
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
                ctx.fill();
                
                // HP Bar
                ctx.fillStyle = 'red';
                ctx.fillRect(this.x - 10, this.y - 20, 20, 4);
                ctx.fillStyle = '#2ecc71';
                ctx.fillRect(this.x - 10, this.y - 20, 20 * (this.hp / this.maxHp), 4);
            }
        }

        class Tower {
            constructor(x, y) {
                this.x = x;
                this.y = y;
                this.range = 120;
                this.damage = 25;
                this.cooldown = 800; // ms
                this.lastShot = 0;
            }

            update(dt) {
                this.lastShot += dt * speedMultiplier;
                if (this.lastShot >= this.cooldown) {
                    // Find target
                    for (let e of enemies) {
                        const dist = Math.hypot(e.x - this.x, e.y - this.y);
                        if (dist <= this.range) {
                            this.shoot(e);
                            this.lastShot = 0;
                            break;
                        }
                    }
                }
            }

            shoot(enemy) {
                projectiles.push(new Projectile(this.x, this.y, enemy, this.damage));
            }

            draw(ctx) {
                ctx.fillStyle = '#2980b9';
                ctx.fillRect(this.x - 15, this.y - 15, 30, 30);
                ctx.fillStyle = '#34495e';
                ctx.beginPath();
                ctx.arc(this.x, this.y, 8, 0, Math.PI * 2);
                ctx.fill();
            }
        }

        class Projectile {
            constructor(x, y, target, damage) {
                this.x = x;
                this.y = y;
                this.target = target;
                this.damage = damage;
                this.speed = 350;
            }

            update(dt) {
                const dx = this.target.x - this.x;
                const dy = this.target.y - this.y;
                const distance = Math.hypot(dx, dy);
                const moveDist = this.speed * dt * speedMultiplier;

                if (distance < moveDist) {
                    this.target.hp -= this.damage;
                    this.hit = true; // Mark for removal
                    if (this.target.hp <= 0 && !this.target.dead) {
                        this.target.dead = true;
                        gold += 10;
                        goldEl.innerText = gold;
                    }
                } else {
                    this.x += (dx / distance) * moveDist;
                    this.y += (dy / distance) * moveDist;
                }
            }

            draw(ctx) {
                ctx.fillStyle = '#f1c40f';
                ctx.beginPath();
                ctx.arc(this.x, this.y, 4, 0, Math.PI * 2);
                ctx.fill();
            }
        }

        // Input & Controls
        btnPause.addEventListener('click', () => {
            isPaused = !isPaused;
            btnPause.innerText = isPaused ? 'Resume' : 'Pause';
            btnPause.classList.toggle('active', isPaused);
            if (!isPaused) lastTime = performance.now();
        });

        btnSpeed.addEventListener('click', () => {
            if (speedMultiplier === 1) speedMultiplier = 2;
            else if (speedMultiplier === 2) speedMultiplier = 4;
            else speedMultiplier = 1;
            btnSpeed.innerText = `Speed: ${speedMultiplier}x`;
        });

        btnBuild.addEventListener('click', () => {
            buildMode = !buildMode;
            btnBuild.classList.toggle('active', buildMode);
        });

        canvas.addEventListener('click', (e) => {
            if (!buildMode || gold < towerCost) return;

            const rect = canvas.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;

            // Simple check to prevent building on path
            let onPath = false;
            for (let i = 0; i < path.length - 1; i++) {
                const p1 = path[i];
                const p2 = path[i+1];
                const minX = Math.min(p1.x, p2.x) - pathWidth;
                const maxX = Math.max(p1.x, p2.x) + pathWidth;
                const minY = Math.min(p1.y, p2.y) - pathWidth;
                const maxY = Math.max(p1.y, p2.y) + pathWidth;

                if (x >= minX && x <= maxX && y >= minY && y <= maxY) {
                    onPath = true;
                    break;
                }
            }

            if (!onPath) {
                towers.push(new Tower(x, y));
                gold -= towerCost;
                goldEl.innerText = gold;
                buildMode = false;
                btnBuild.classList.remove('active');
            }
        });

        // Game Loop
        function drawPath() {
            ctx.strokeStyle = '#95a5a6';
            ctx.lineWidth = pathWidth * 1.5;
            ctx.lineJoin = 'round';
            ctx.lineCap = 'square';
            
            ctx.beginPath();
            ctx.moveTo(path[0].x, path[0].y);
            for (let i = 1; i < path.length; i++) {
                ctx.lineTo(path[i].x, path[i].y);
            }
            ctx.stroke();

            // Draw dashed center line
            ctx.strokeStyle = '#bdc3c7';
            ctx.lineWidth = 2;
            ctx.setLineDash([10, 10]);
            ctx.beginPath();
            ctx.moveTo(path[0].x, path[0].y);
            for (let i = 1; i < path.length; i++) {
                ctx.lineTo(path[i].x, path[i].y);
            }
            ctx.stroke();
            ctx.setLineDash([]);
        }

        function gameLoop(timestamp) {
            if (isPaused) {
                requestAnimationFrame(gameLoop);
                return;
            }

            const dt = (timestamp - lastTime) / 1000; // Delta time in seconds
            lastTime = timestamp;

            // Clear Canvas
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            // Draw Environment
            drawPath();

            // Wave Logic
            if (enemiesToSpawn > 0) {
                spawnTimer += dt * 1000 * speedMultiplier;
                if (spawnTimer >= spawnCooldown) {
                    const hp = 50 + (wave * 20);
                    const spd = 60 + (wave * 5);
                    enemies.push(new Enemy(hp, spd));
                    enemiesToSpawn--;
                    spawnTimer = 0;
                }
            } else if (enemies.length === 0) {
                waveTimer += dt * 1000 * speedMultiplier;
                if (waveTimer >= 3000) { // 3 seconds between waves
                    wave++;
                    waveEl.innerText = wave;
                    enemiesToSpawn = 5 + Math.floor(wave * 1.5);
                    spawnCooldown = Math.max(400, 1000 - (wave * 50));
                    waveTimer = 0;
                }
            }

            // Update & Draw Entities
            for (let i = enemies.length - 1; i >= 0; i--) {
                const e = enemies[i];
                e.update(dt);
                if (e.hp <= 0 || e.pathIndex >= path.length - 1) {
                    enemies.splice(i, 1);
                } else {
                    e.draw(ctx);
                }
            }

            for (let t of towers) {
                t.update(dt);
                t.draw(ctx);
            }

            for (let i = projectiles.length - 1; i >= 0; i--) {
                const p = projectiles[i];
                p.update(dt);
                if (p.hit) {
                    projectiles.splice(i, 1);
                } else {
                    p.draw(ctx);
                }
            }

            // Build mode UI feedback
            if (buildMode) {
                ctx.fillStyle = 'rgba(41, 128, 185, 0.2)';
                ctx.beginPath();
                // We don't have mouse coordinates actively tracked in loop, 
                // so we just show an overlay text to indicate build mode.
                ctx.fillStyle = '#fff';
                ctx.font = '20px Arial';
                ctx.fillText("Click anywhere off the path to place a tower", 20, 30);
            }

            if (lives <= 0) {
                ctx.fillStyle = 'rgba(0,0,0,0.7)';
                ctx.fillRect(0,0,canvas.width,canvas.height);
                ctx.fillStyle = '#e74c3c';
                ctx.font = '48px Arial';
                ctx.fillText("GAME OVER", canvas.width/2 - 140, canvas.height/2);
                return; // End loop
            }

            requestAnimationFrame(gameLoop);
        }

        // Start Game
        requestAnimationFrame(gameLoop);
    </script>
</body>
</html>
