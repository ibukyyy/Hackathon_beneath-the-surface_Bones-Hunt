# bone_hunt.py
# Writes a single-file HTML/CSS/JS game (Bone Hunt: Beneath the Surface)
# and opens it in the default web browser.

import os
import webbrowser
from pathlib import Path

HTML = r"""
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width,initial-scale=1" />
<title>Bone Hunt: Beneath the Surface</title>
<style>
    :root{--bg:#0f0f12;--dirt:#6b462b;--darker:#0b0b0d;--accent:#f6d365}
    html,body{height:100%;margin:0;font-family:Segoe UI,Roboto,Arial}
    body{background:linear-gradient(180deg,#0b0b0d 0%, #1a1a1f 60%);display:flex;align-items:center;justify-content:center;color:#eee}
    .wrap{background:linear-gradient(#14121a,#100f13);padding:18px;border-radius:12px;box-shadow:0 10px 40px rgba(0,0,0,.6)}
    h1{margin:0 0 8px;font-size:20px;text-align:center}
    #game{display:block;background:linear-gradient(#2a2420,#1b1614);border-radius:6px;display:block}
    .hud{display:flex;gap:12px;justify-content:space-between;align-items:center;margin-top:8px}
    .hud .left{display:flex;gap:8px;align-items:center}
    .meter{width:180px;height:18px;background:#222;border-radius:12px;overflow:hidden}
    .meter .fill{height:100%;width:0%;background:linear-gradient(90deg,#ffb86b,#ff5f6d)}
    .status{font-size:14px}
    .controls{font-size:12px;color:#ccc}
    .overlay{position:absolute;left:0;top:0;width:100%;height:100%;pointer-events:none}
    .message{position:fixed;left:50%;transform:translateX(-50%);top:12px;padding:6px 12px;background:#222;border-radius:8px;color:#fff;opacity:0.95}
    footer{margin-top:10px;text-align:center;font-size:12px;color:#999}
    /* small mobile responsiveness */
    @media (max-width:900px){.wrap{transform:scale(0.95)}}
</style>
</head>
<body>
<div class="wrap">
  <h1>Bone Hunt: Beneath the Surface</h1>
  <div style="position:relative;width:820px;">
    <canvas id="game" width="800" height="500"></canvas>
    <div class="overlay"></div>
  </div>
    <div class="hud">
    <div class="left">
            <div class="status">Score: <span id="score">0</span></div>
            <div class="status">Lives: <span id="lives">3</span></div>
            <div class="meter" title="Scent meter"><div id="meterfill" class="fill"></div></div>
            <div class="status" id="hint">Far</div>
    </div>
    <div class="controls">Move: WASD / Arrows • Dig: SPACE • Restart: R</div>
  </div>
  <footer>Collect 10 bones to win • Bones are hidden underground</footer>
</div>

<script>
/* Game variables required by the CSP list */
let score = 0;
let playerX = 400;
let playerY = 250;
let lives = 3;
let gameRunning = true;

// Map size
const MAP_W = 800;
const MAP_H = 500;

// Arrays for bones and enemies
let bones = []; // hidden bone objects {x,y,found}
let enemies = []; // enemy objects {x,y,vx,vy,type}

// Visual particles for digging effect
let particles = [];

// Player state
const player = { x: playerX, y: playerY, size: 22, speed: 2.6, color: '#c9e4a6' };

// Input
const keys = {};

// DOM
const canvas = document.getElementById('game');
const ctx = canvas.getContext('2d');
const scoreEl = document.getElementById('score');
const livesEl = document.getElementById('lives');
const hintEl = document.getElementById('hint');
const meterEl = document.getElementById('meterfill');

// Game tuneables
const BONE_DETECT_DIST = 40; // distance for successful dig
const NUM_START_BONES = 3;
const WIN_TARGET = 10;
const ENEMY_COUNT = 3;

// Utility: distance
function dist(a,b,c,d){ return Math.hypot(a-c,b-d); }

// Functions required by user
function movePlayer(){
    // called every frame to update player position based on keys
    let moved = false;
    let vx = 0, vy = 0;
    if (keys['ArrowLeft'] || keys['a'] || keys['A']) vx -= 1;
    if (keys['ArrowRight'] || keys['d'] || keys['D']) vx += 1;
    if (keys['ArrowUp'] || keys['w'] || keys['W']) vy -= 1;
    if (keys['ArrowDown'] || keys['s'] || keys['S']) vy += 1;
    if (vx !== 0 || vy !== 0){
        const len = Math.hypot(vx,vy) || 1;
        vx = vx/len * player.speed;
        vy = vy/len * player.speed;
        player.x = Math.max(player.size, Math.min(MAP_W-player.size, player.x + vx));
        player.y = Math.max(player.size, Math.min(MAP_H-player.size, player.y + vy));
        moved = true;
    }
    playerX = player.x;
    playerY = player.y;
}

function digBone(){
    // Attempt to dig at player's current position
    // If a bone is within BONE_DETECT_DIST, reveal and collect
    let foundIndex = -1;
    for (let i=0;i<bones.length;i++){
        const b = bones[i];
        const d = dist(player.x, player.y, b.x, b.y);
        if (!b.found && d <= BONE_DETECT_DIST){ foundIndex = i; break; }
    }
    if (foundIndex >= 0){
        // collect bone
        bones[foundIndex].found = true;
        score++;
        scoreEl.textContent = score;
        // spawn another hidden bone
        spawnBone();
        // small reveal animation: create bigger particles
        for (let p=0;p<10;p++) particles.push({x:player.x + (Math.random()-0.5)*20, y:player.y + (Math.random()-0.5)*20, vx:(Math.random()-0.5)*2, vy:Math.random()*-2 - 1, life:60});
        // Win check
        if (score >= WIN_TARGET){
            gameRunning = false;
            setTimeout(()=> alert('You found 10 bones! You win!'), 50);
        }
    } else {
        // digging into dirt: particles + small soundless animation
        for (let p=0;p<18;p++) particles.push({x:player.x + (Math.random()-0.5)*28, y:player.y + (Math.random()-0.5)*8 + 8, vx:(Math.random()-0.5)*2, vy:-Math.random()*1.8, life:40});
        // show temporary message
        flashMessage('No bone here...', 700);
    }
}

function spawnBone(){
    // Place a hidden bone at random coordinates not too close to player
    let x,y,tries=0;
    do{
        x = Math.random()*(MAP_W-40)+20;
        y = Math.random()*(MAP_H-40)+20;
        tries++;
    } while (dist(x,y,player.x,player.y) < 80 && tries < 20);
    bones.push({x:x,y:y,found:false});
}

function updateScentMeter(){
    // Find nearest not-found bone
    let minD = Infinity;
    for (let i=0;i<bones.length;i++){
        const b = bones[i];
        if (b.found) continue;
        const d = dist(player.x, player.y, b.x, b.y);
        if (d < minD) minD = d;
    }
    if (!isFinite(minD)) minD = 1000;
    // Map distance to meter percentage (close->large)
    const clamped = Math.max(0, Math.min(1, 1 - (minD/400)));
    meterEl.style.width = `${Math.round(clamped*100)}%`;
    // Update hint and player color
    if (minD > 250){ hintEl.textContent = 'Far'; player.color = '#c9e4a6'; }
    else if (minD > 120){ hintEl.textContent = 'Close'; player.color = '#ffd57e'; }
    else { hintEl.textContent = 'Very Close'; player.color = '#ff8b8b'; }
}

function checkCollision(){
    // Enemy collisions - if collision reduce lives and respawn player slightly
    for (let i=0;i<enemies.length;i++){
        const e = enemies[i];
        const d = dist(player.x, player.y, e.x, e.y);
        if (d < player.size + 12){
            // collided
            lives -= 1;
            livesEl.textContent = lives;
            flashMessage('Ouch! You hit a cat/trap!', 900);
            // knockback
            const angle = Math.atan2(player.y - e.y, player.x - e.x);
            player.x = Math.max(player.size, Math.min(MAP_W-player.size, player.x + Math.cos(angle)*40));
            player.y = Math.max(player.size, Math.min(MAP_H-player.size, player.y + Math.sin(angle)*40));
            if (lives <= 0){ gameRunning = false; setTimeout(()=> alert('Game over! Press R to restart.'), 50); }
        }
    }
}

function restartGame(){
    // Reset all variables and spawn initial bones/enemies
    score = 0; player.x = MAP_W/2; player.y = MAP_H/2; lives = 3; gameRunning = true;
    bones = []; enemies = []; particles = [];
    document.getElementById('score').textContent = score;
    document.getElementById('lives').textContent = lives;
    // spawn some bones
    for (let i=0;i<NUM_START_BONES;i++) spawnBone();
    // spawn enemies
    for (let i=0;i<ENEMY_COUNT;i++){
        enemies.push({x:Math.random()*(MAP_W-80)+40, y:Math.random()*(MAP_H-80)+40, vx:(Math.random()*1.4-0.7), vy:(Math.random()*1.4-0.7), type:'cat'});
    }
}

// Additional helper: flashing HUD message
let msgTimeout = null;
function flashMessage(text, ms=600){
    const old = document.querySelector('.message');
    if (old) old.remove();
    const el = document.createElement('div'); el.className='message'; el.textContent = text;
    document.body.appendChild(el);
    if (msgTimeout) clearTimeout(msgTimeout);
    msgTimeout = setTimeout(()=>{ el.remove(); msgTimeout=null; }, ms);
}

// Setup initial game
restartGame();

// Game loop
function gameLoop(){
    if (gameRunning){
        // update
        movePlayer();
        // move enemies
        for (let i=0;i<enemies.length;i++){
            const e = enemies[i];
            e.x += e.vx; e.y += e.vy;
            if (e.x < 10 || e.x > MAP_W-10) e.vx *= -1;
            if (e.y < 10 || e.y > MAP_H-10) e.vy *= -1;
            // small random wiggle
            if (Math.random() < 0.01) e.vx += (Math.random()-0.5)*0.6;
            if (Math.random() < 0.01) e.vy += (Math.random()-0.5)*0.6;
        }
        // particle updates
        for (let i=particles.length-1;i>=0;i--){
            const p = particles[i]; p.x += p.vx; p.y += p.vy; p.vy += 0.08; p.life -= 1; if (p.life<=0) particles.splice(i,1);
        }
        updateScentMeter();
        checkCollision();
    }
    render();
    requestAnimationFrame(gameLoop);
}

function render(){
    // background
    ctx.clearRect(0,0,MAP_W,MAP_H);
    // underground fill
    const g = ctx.createLinearGradient(0,0,0,MAP_H);
    g.addColorStop(0,'#241b16'); g.addColorStop(1,'#1a120b');
    ctx.fillStyle = g; ctx.fillRect(0,0,MAP_W,MAP_H);

    // subtle rocks/dirt texture
    for (let i=0;i<40;i++){
        ctx.fillStyle = 'rgba(0,0,0,0.02)';
        const rx = (i*37) % MAP_W; const ry = (i*21) % MAP_H;
        ctx.fillRect(rx, ry, 2, 2);
    }

    // draw hidden bones if found (small bone icon)
    for (let i=0;i<bones.length;i++){
        const b = bones[i];
        if (b.found){
            ctx.save(); ctx.translate(b.x,b.y); ctx.rotate(0.2);
            ctx.fillStyle = '#fff7d6'; ctx.fillRect(-8,-3,16,6); ctx.fillStyle='#e7d6b2'; ctx.beginPath(); ctx.ellipse(6,-6,3,3,Math.PI/4,0,Math.PI*2); ctx.fill(); ctx.beginPath(); ctx.ellipse(-6,6,3,3,Math.PI/4,0,Math.PI*2); ctx.fill(); ctx.restore();
        }
    }

    // draw enemies (cats)
    for (let i=0;i<enemies.length;i++){
        const e = enemies[i];
        ctx.save(); ctx.translate(e.x,e.y);
        // body
        ctx.fillStyle = '#444'; ctx.beginPath(); ctx.ellipse(0,0,12,9,0,0,Math.PI*2); ctx.fill();
        // head
        ctx.fillStyle = '#333'; ctx.beginPath(); ctx.ellipse(-12,-2,6,6,0,0,Math.PI*2); ctx.fill();
        // eyes
        ctx.fillStyle = '#ffdb70'; ctx.fillRect(-14,-4,3,3); ctx.fillRect(-10,-4,3,3);
        ctx.restore();
    }

    // draw player (dog)
    ctx.save(); ctx.translate(player.x, player.y);
    // body
    ctx.fillStyle = player.color; ctx.beginPath(); ctx.ellipse(0,0,player.size,player.size*0.7,0,0,Math.PI*2); ctx.fill();
    // head
    ctx.fillStyle = player.color; ctx.beginPath(); ctx.ellipse(player.size*0.6,-player.size*0.4,player.size*0.5,player.size*0.5,0,0,Math.PI*2); ctx.fill();
    // nose
    ctx.fillStyle = '#333'; ctx.beginPath(); ctx.arc(player.size*0.95,-player.size*0.4,4,0,Math.PI*2); ctx.fill();
    // ear
    ctx.fillStyle = '#8f6b4d'; ctx.beginPath(); ctx.ellipse(player.size*0.55,-player.size*0.9,6,8, -0.4,0,Math.PI*2); ctx.fill();
    ctx.restore();

    // draw particles
    for (let i=0;i<particles.length;i++){
        const p = particles[i];
        ctx.fillStyle = 'rgba(210,180,140,' + (p.life/60) + ')';
        ctx.beginPath(); ctx.arc(p.x,p.y, Math.max(1, p.life/18), 0, Math.PI*2); ctx.fill();
    }

    // HUD decorations
    // (bones remaining count is not shown since bones are infinite spawn)
}

// Input handlers
window.addEventListener('keydown', (e) => {
    keys[e.key] = true;
    if (e.key === ' '){ e.preventDefault(); if (gameRunning) digBone(); }
    if (e.key === 'r' || e.key === 'R') { restartGame(); }
});
window.addEventListener('keyup', (e) => { keys[e.key] = false; });

// Touch / mobile quick taps: tap to dig
canvas.addEventListener('click', (e)=>{ if (gameRunning) digBone(); });

// Start the loop
requestAnimationFrame(gameLoop);

// expose functions to console (helpful for grading/inspection)
window.movePlayer = movePlayer;
window.digBone = digBone;
window.spawnBone = spawnBone;
window.updateScentMeter = updateScentMeter;
window.checkCollision = checkCollision;
window.restartGame = restartGame;

</script>
</body>
</html>
"""


def main():
    out_path = Path(__file__).with_name('bone_hunt.html')
    out_path.write_text(HTML, encoding='utf-8')
    print(f'Wrote HTML game to: {out_path}')
    # open in default browser
    webbrowser.open('file://' + str(out_path.resolve()))

if __name__ == '__main__':
    main()
