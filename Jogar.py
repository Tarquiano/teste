from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina import AmbientLight
import random
import pygame
import os
import time

app = Ursina()

# Inicializando pygame para tocar o som
pygame.mixer.init()

# Customizando a skybox
sky_texture = load_texture('skybox.png')  # Substitua 'skybox.png' pela textura que deseja usar para a skybox
sky = Entity(model='sphere', texture=sky_texture, scale=500, double_sided=True)

# Iluminação mais sombria para o ambiente
ambient_light = AmbientLight(type='directional', color=color.rgb(150, 30, 30))  # Luz ambiente avermelhada suave
directional_light = DirectionalLight(color=color.rgb(255, 100, 100), shadows=True, position=(3, 10, 3), rotation=(45, -45, 0))  # Luz direcional com tom mais suave de vermelho


# Música tema de terror
theme_music = Audio('scary.mp3', loop=True, autoplay=True)

# Inimigo com aparência assustadora
enemy = Entity(model='cube', color=color.red, scale_y=2, position=(3, 1, 3),
               texture='/miau.jfif')

# Tamanho do grid do labirinto
maze_size = 21
cell_size = 4

jump_count = 0
max_jumps = 2
vitoria = False

maze = [[1 for x in range(maze_size)] for y in range(maze_size)]

def generate_maze(x, y):
    maze[y][x] = 0
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    random.shuffle(directions)
    for dx, dy in directions:
        nx, ny = x + dx * 2, y + dy * 2
        if 0 <= nx < maze_size and 0 <= ny < maze_size and maze[ny][nx] == 1:
            maze[ny - dy][nx - dx] = 0
            generate_maze(nx, ny)

start_x = random.randrange(0, maze_size, 2)
start_y = random.randrange(0, maze_size, 2)
generate_maze(start_x, start_y)

ground_size = maze_size * cell_size
ground = Entity(model='plane', scale=(ground_size, 1, ground_size), color=color.gray, texture='white_cube', texture_scale=(maze_size, maze_size), collider='box')

for y in range(maze_size):
    for x in range(maze_size):
        if maze[y][x] == 1:
            Entity(model='cube', 
                   scale=(cell_size, 2, cell_size), 
                   position=(x * cell_size - maze_size * 2, 1, y * cell_size - maze_size * 2),
                   texture='brick', 
                   color=color.red.tint(-0.4), 
                   collider='box')

for i in range(maze_size + 1):
    Entity(model='cube', scale=(cell_size, 2, cell_size), position=(-maze_size * 2 - cell_size, 1, i * cell_size - maze_size * 2), color=color.gray, collider='box')
    Entity(model='cube', scale=(cell_size, 2, cell_size), position=(maze_size * 2, 1, i * cell_size - maze_size * 2), color=color.gray, collider='box')
    Entity(model='cube', scale=(cell_size, 2, cell_size), position=(i * cell_size - maze_size * 2, 1, -maze_size * 2 - cell_size), color=color.gray, collider='box')
    Entity(model='cube', scale=(cell_size, 2, cell_size), position=(i * cell_size - maze_size * 2, 1, maze_size * 2), color=color.gray, collider='box')

while True:
    player_x = random.randrange(0, maze_size, 2)
    player_y = random.randrange(0, maze_size, 2)
    if maze[player_y][player_x] == 0:
        break

player = FirstPersonController(model='cube', collider='box', position=(player_x * cell_size - maze_size * 2, 1, player_y * cell_size - maze_size * 2))
player.jump_height = 0  # Impede que o jogador salte


while True:
    finish_x = random.randrange(0, maze_size, 2)
    finish_y = random.randrange(0, maze_size, 2)
    if maze[finish_y][finish_x] == 0:
        break

finish = Entity(model='cube', scale=(1, 1, 1), color=color.green, collider='box',
                position=(finish_x * cell_size - maze_size * 2, 1, finish_y * cell_size - maze_size * 2))

def tocar_grito():
    pygame.mixer.music.load("au.mp3")
    pygame.mixer.music.play()

def desligar_pc():
    if os.name == 'nt':
        print("Desligando em Windows...")
    else: 
        print("Desligando em Linux/Mac...")

def start_enemy_movement():
    enemy.look_at(player.position)
    enemy.position = Vec3(enemy.position.x, 1, enemy.position.z)
    enemy.position += enemy.forward * time.dt * 4

def update():
    global jump_count, vitoria
    if held_keys['space']:
        if jump_count < max_jumps and player.grounded:
            player.jump()
            jump_count += 1
            cavalo = 2
    elif player.grounded:
        jump_count = 0

    hit_info = player.intersects()
    if hit_info.hit and hit_info.entity == finish and not vitoria:
        vitoria = True
        message = Text(text='VOCÊ VENCEU DO MONSTRO MALIGNO', scale=2, origin=(0, 0), background=True, color=color.blue)
        invoke(application.quit, delay=3)
        mouse.locked = False

    if hasattr(enemy, 'start_moving'):
        start_enemy_movement()

    if distance(player.position, enemy.position) < 1 and not vitoria:
        print("Você foi pego!")
        tocar_grito()
        time.sleep(3)
        desligar_pc()
        application.quit()

countdown = 180 
def timedown():
    global countdown
    count = Text(text='Countdown: ' + str(countdown), origin=(-2, -6), color=color.white)
    count.fade_out(0, 0.5)
    countdown -= 1
    seq = invoke(timedown, delay=1)
    
    if countdown == -1 and not vitoria:
        end = Text(text='Você não conseguiu escapar do bixo maligno!', scale=2, origin=(0, 0), background=True, color=color.red)
        tocar_grito()
        time.sleep(3)
        desligar_pc()
        application.pause()
        mouse.locked = False
        seq.kill()

timedown()

invoke(setattr, enemy, 'start_moving', True, delay=5)

app.run()
