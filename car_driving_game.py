from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import time
import math

fovY = 90

window_width, window_height = 1000, 800

# camera variables
camera_position = (0, 4100, 250)

fpp_mode = False

# game stats

# Distance and difficulty scaling
total_distance = 0
initial_speed = 10
max_speed = 20
game_speed = 10
speed_increase_rate = 0.2

life_remaining = 10
game_score = 0
bullet_count = 0
nitro_count = 0
last_time = time.time()
isPaused = False

cheatMode = False


# graphics related variables
isDay = True

road_width = 400
road_length = 4500

element_offset = 0

tree_offset = 0

# car stats
car_x, car_y, car_z = 0, 3700, 16
car_rotation = 0

# ramp variables
ramp_positions = {}

ramp_spawn_delay = 2
last_ramp_time = time.time()

is_jumping = False
max_height = 400
jump_phase = None


ramp_length = 200
ramp_width = 200
ramp_angle = -45

# ============== OBSTACLE SYSTEM ==============
obstacle_positions = {}
obstacle_spawn_delay = 1.5
last_obstacle_time = time.time()
obstacle_size = 120
obstacle_speed = 50

# ============== COLLECTIBLE AMMO SYSTEM ==============
ammo_positions = {}
ammo_spawn_delay = 2.5
last_ammo_time = time.time()
ammo_size = 30

# ============== COLLECTIBLE NITRO SYSTEM ==============
nitro_positions = {}
isNitroMode = False
nitro_rotation_angle = 0
nitro_spawn_delay = 5
last_nitro_time = time.time()
nitro_time_per_unit = 0.3
nitro_duration = 0
previous_speed = game_speed
nitro_speed = 50

# ============== SHOOTING SYSTEM ==============
player_bullets = {}
player_bullet_speed = 500
next_bullet_id = 1


def reshape(w, h):
    global window_width, window_height
    window_width = w
    window_height = h
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(fovY, w / h, 0.1, 6000)
    glMatrixMode(GL_MODELVIEW)

def restart_game():
    global life_remaining, game_score, bullet_count, nitro_count
    global car_x, car_y, car_z, car_rotation
    global obstacle_positions, ammo_positions, nitro_positions
    global player_bullets, ramp_positions
    global is_jumping, jump_phase, isPaused, last_time
    global total_distance, game_speed, isNitroMode
    global nitro_duration, previous_speed
    global last_ramp_time, last_obstacle_time, last_ammo_time, last_nitro_time

    # stats
    life_remaining = 10
    game_score = 0
    bullet_count = 0
    nitro_count = 0
    total_distance = 0

    # car
    car_x, car_y, car_z = 0, 3700, 16
    car_rotation = 0

    # speed & nitro
    game_speed = initial_speed
    previous_speed = game_speed
    isNitroMode = False
    nitro_duration = 0

    # states
    is_jumping = False
    jump_phase = None
    isPaused = False

    # clear entities
    obstacle_positions.clear()
    ammo_positions.clear()
    nitro_positions.clear()
    player_bullets.clear()
    ramp_positions.clear()

    # timers
    last_time = time.time()
    last_ramp_time = last_time
    last_obstacle_time = last_time
    last_ammo_time = last_time
    last_nitro_time = last_time

    print("Game Restarted!")


def specialKeyboardListener(key, x, y):
    global camera_position

    cam_x, cam_y, cam_z = camera_position
    step = 10

    if key == GLUT_KEY_LEFT:
        cam_x = min(cam_x + step, 200)
        camera_position = (cam_x, cam_y, cam_z)


    if key == GLUT_KEY_RIGHT:
        cam_x = max(cam_x - step, -200)
        camera_position = (cam_x, cam_y, cam_z)

    if key == GLUT_KEY_UP:
        cam_z = min(cam_z + step, 420)
        cam_y = min(cam_y + 5, 4100)
        camera_position = (cam_x, cam_y, cam_z)

    if key == GLUT_KEY_DOWN:
        cam_z = max(cam_z - step, 50)
        cam_y = max(cam_y - 5, 4000)
        camera_position = (cam_x, cam_y, cam_z)

def mouseListener(button, state, x, y):
    global bullet_count, player_bullets, car_x, car_y, car_z, next_bullet_id, life_remaining

    if life_remaining > 0:
        if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
            if bullet_count > 0:
                bullet_data = (car_x, car_y + 50, car_z + 30, 0, -player_bullet_speed, 0)
                player_bullets[next_bullet_id] = bullet_data
                bullet_count -= 1
                next_bullet_id += 1

def keyboardListener(key, x, y):
    global road_width, isDay, car_x, car_y, car_z, ramp_positions, isPaused, fpp_mode, life_remaining, nitro_rotation_angle,  nitro_count, isNitroMode, nitro_start_time, nitro_time_per_unit, nitro_duration, game_speed, cheatMode, nitro_duration

    if key == b'r' or key == b'R':
        restart_game()
        
    if life_remaining > 0:
        if key == b'n' or key == b'N': #day and night shifter
            isDay = not isDay

        if key == b'a' or key == b'A':
            car_x = min(car_x+10, road_width-50)
    
        if key == b'd' or key == b'D':
            car_x = max(car_x-10, -road_width+50)
    
        if key == b'p' or key == b'P':
            isPaused = not isPaused
    
        if key == b'v' or key == b'V':
            fpp_mode = not fpp_mode
        
        if key == b'c' or key == b'C':
            cheatMode = not cheatMode 
            print(f"Cheat Mode: {cheatMode}")

        if key == b' ':
            if nitro_count > 0:
                isNitroMode = True
                nitro_start_time = time.time()
                nitro_duration = nitro_count * nitro_time_per_unit
                nitro_count = 0

def setupCamera():
    global camera_position, window_width, window_height, fpp_mode, car_x, car_y, car_z, car_rotation

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()

    gluPerspective(fovY, window_width / window_height, 0.1, 6000)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    if fpp_mode:
        cam_x = car_x
        cam_y = car_y
        cam_z = car_z + 60

        # Look straight forward along the road
        pitch = math.radians(car_rotation)

        look_x = car_x
        look_y = car_y - math.cos(pitch) * 1000
        look_z = car_z - math.sin(pitch) * 1000

        gluLookAt(
            cam_x, cam_y, cam_z,
            look_x, look_y, look_z,
            0, 0, 1
        )
    else:
        cam_x, cam_y, cam_z = camera_position

        gluLookAt(cam_x,cam_y,cam_z,
                  0, 0, 0,
                  0, 0, 1)

def draw_sky():
    if isDay:
        glClearColor(0.5, 0.8, 0.9, 1.0)
    else:
        glClearColor(0.1, 0.1, 0.15, 1.0)

def draw_trees(tree_x):
    global road_width, road_length, element_offset

    gap = 500
    x = tree_x
    common_tree_y_term = road_length - gap - element_offset
    z = 2

    while common_tree_y_term > -road_length:
        if -road_length < common_tree_y_term < road_length:
            glPushMatrix()
            glTranslatef(x, common_tree_y_term, z)

            trunk_height = 40
            glColor3f(0.55, 0.27, 0.07)
            quad = gluNewQuadric()
            gluCylinder(quad, 12, 8, trunk_height, 32, 32)

            glTranslatef(0, 0, trunk_height)

            glColor3f(0, 0.3, 0)
            for i in range(3):
                if i == 2:
                    gluCylinder(quad, 25, 0, trunk_height/1.2, 32, 32)
                    glTranslatef(0, 0, trunk_height/2)
                else:
                    gluCylinder(quad, 25, 5, trunk_height, 32, 32)
                    glTranslatef(0, 0, trunk_height/2)

            glPopMatrix()

        common_tree_y_term -= gap

def draw_border():
    glPushMatrix()
    glColor3f(0.2, 0.7, 0.3)
    glBegin(GL_QUADS)
    glVertex3f(road_width+200, road_length, -2)
    glVertex3f(road_width+200, -road_length, -2)
    glVertex3f(-road_width-200, -road_length, -2)
    glVertex3f(-road_width-200, road_length, -2)
    glEnd()

    draw_trees(road_width + 100)
    draw_trees(-road_width - 100)

    glPopMatrix()

def draw_road():
    global element_offset, road_length

    glPushMatrix()

    glColor3f(0.3, 0.3, 0.3)
    glBegin(GL_QUADS)
    glVertex3f(road_width, road_length, 0)
    glVertex3f(road_width, -road_length, 0)
    glVertex3f(-road_width, -road_length, 0)
    glVertex3f(-road_width, road_length, 0)
    glEnd()

    glColor3f(1, 1, 1)
    divider_width = 10
    divider_height = 200
    gap = 150
    z = 1

    common_y = road_length - gap - element_offset

    while common_y > -road_length:
        if -road_length < common_y < road_length:
            glBegin(GL_QUADS)
            glVertex3f(-divider_width, common_y,z)
            glVertex3f(-divider_width, common_y - divider_height,z)
            glVertex3f(divider_width, common_y - divider_height,z)
            glVertex3f(divider_width, common_y,z)
            glEnd()

        common_y -= divider_height + gap

    glPopMatrix()

def draw_ramp():
    global road_length, ramp_length, ramp_width, ramp_angle, ramp_positions

    for ramp_id in list(ramp_positions.keys()):
        ramp_x, ramp_y, ramp_z = ramp_positions[ramp_id]

        if -road_length < ramp_y < road_length:
            glPushMatrix()
            glTranslatef(ramp_x, ramp_y, ramp_z)
            glRotatef(ramp_angle, 1, 0, 0)
            glColor3f(0.1, 0.1, 0.1)
            glBegin(GL_QUADS)
            glVertex3f(-(ramp_width/2), 0, 0)
            glVertex3f((ramp_width/2), 0, 0)
            glVertex3f((ramp_width/2), -ramp_length, 0)
            glVertex3f(-(ramp_width/2), -ramp_length, 0)
            glEnd()
            glPopMatrix()
        else:
            ramp_positions.pop(ramp_id)

def spawn_obstacle():
    global obstacle_positions, last_obstacle_time, game_speed

    current_time = time.time()
    adjusted_spawn_delay = obstacle_spawn_delay / (1 + game_speed / 15)

    if current_time - last_obstacle_time >= adjusted_spawn_delay:
        lane_x = random.choice([-200, 0, 200])
        spawn_y = 0
        spawn_z = obstacle_size / 2

        obstacle_type = random.choice(["cube", "square", "cylinder"])
        is_moving = random.random() < 0.3
        direction = random.choice([1, -1]) if is_moving else 0

        obstacle_id = max(obstacle_positions.keys(), default=0) + 1
        obstacle_positions[obstacle_id] = (lane_x, spawn_y, spawn_z, obstacle_type, is_moving, direction)
        last_obstacle_time = current_time

def spawn_ammo():
    global ammo_positions, last_ammo_time

    current_time = time.time()

    if current_time - last_ammo_time >= ammo_spawn_delay:
        lane_x = random.choice([-200, 0, 200])
        spawn_y = 0
        spawn_z = ammo_size

        ammo_id = max(ammo_positions.keys(), default=0) + 1
        ammo_positions[ammo_id] = (lane_x, spawn_y, spawn_z)
        last_ammo_time = current_time

def spawn_nitro():
    global nitro_positions, last_nitro_time, nitro_spawn_delay

    current_time = time.time()

    if current_time - last_nitro_time >= nitro_spawn_delay:
        lane_x = random.choice([-200, 0, 200])
        spawn_y = 0
        spawn_z = 20

        nitro_id = max(nitro_positions.keys(), default=0) + 1
        nitro_positions[nitro_id] = (lane_x, spawn_y, spawn_z)
        last_nitro_time = current_time

def draw_obstacle(x, y, z, obstacle_type):
    glPushMatrix()
    glTranslatef(x, y, z)

    if obstacle_type == "cube":
        glColor3f(1, 0.5, 0)
        glBegin(GL_QUADS)

        glVertex3f(-obstacle_size/2, -obstacle_size/2, -obstacle_size/2)
        glVertex3f(obstacle_size/2, -obstacle_size/2, -obstacle_size/2)
        glVertex3f(obstacle_size/2, obstacle_size/2, -obstacle_size/2)
        glVertex3f(-obstacle_size/2, obstacle_size/2, -obstacle_size/2)

        glVertex3f(-obstacle_size/2, -obstacle_size/2, obstacle_size/2)
        glVertex3f(obstacle_size/2, -obstacle_size/2, obstacle_size/2)
        glVertex3f(obstacle_size/2, obstacle_size/2, obstacle_size/2)
        glVertex3f(-obstacle_size/2, obstacle_size/2, obstacle_size/2)

        glVertex3f(-obstacle_size/2, -obstacle_size/2, -obstacle_size/2)
        glVertex3f(-obstacle_size/2, obstacle_size/2, -obstacle_size/2)
        glVertex3f(-obstacle_size/2, obstacle_size/2, obstacle_size/2)
        glVertex3f(-obstacle_size/2, -obstacle_size/2, obstacle_size/2)

        glVertex3f(obstacle_size/2, -obstacle_size/2, -obstacle_size/2)
        glVertex3f(obstacle_size/2, obstacle_size/2, -obstacle_size/2)
        glVertex3f(obstacle_size/2, obstacle_size/2, obstacle_size/2)
        glVertex3f(obstacle_size/2, -obstacle_size/2, obstacle_size/2)

        glVertex3f(-obstacle_size/2, obstacle_size/2, -obstacle_size/2)
        glVertex3f(obstacle_size/2, obstacle_size/2, -obstacle_size/2)
        glVertex3f(obstacle_size/2, obstacle_size/2, obstacle_size/2)
        glVertex3f(-obstacle_size/2, obstacle_size/2, obstacle_size/2)

        glVertex3f(-obstacle_size/2, -obstacle_size/2, -obstacle_size/2)
        glVertex3f(obstacle_size/2, -obstacle_size/2, -obstacle_size/2)
        glVertex3f(obstacle_size/2, -obstacle_size/2, obstacle_size/2)
        glVertex3f(-obstacle_size/2, -obstacle_size/2, obstacle_size/2)

        glEnd()

    elif obstacle_type == "square":
        glColor3f(1, 0, 0)
        glBegin(GL_QUADS)

        width = obstacle_size * 0.8
        height = obstacle_size * 1.5

        glVertex3f(-width/2, -obstacle_size/2, -width/2)
        glVertex3f(width/2, -obstacle_size/2, -width/2)
        glVertex3f(width/2, height, -width/2)
        glVertex3f(-width/2, height, -width/2)

        glVertex3f(-width/2, -obstacle_size/2, width/2)
        glVertex3f(width/2, -obstacle_size/2, width/2)
        glVertex3f(width/2, height, width/2)
        glVertex3f(-width/2, height, width/2)

        glVertex3f(-width/2, -obstacle_size/2, -width/2)
        glVertex3f(-width/2, height, -width/2)
        glVertex3f(-width/2, height, width/2)
        glVertex3f(-width/2, -obstacle_size/2, width/2)

        glVertex3f(width/2, -obstacle_size/2, -width/2)
        glVertex3f(width/2, height, -width/2)
        glVertex3f(width/2, height, width/2)
        glVertex3f(width/2, -obstacle_size/2, width/2)

        glVertex3f(-width/2, height, -width/2)
        glVertex3f(width/2, height, -width/2)
        glVertex3f(width/2, height, width/2)
        glVertex3f(-width/2, height, width/2)

        glVertex3f(-width/2, -obstacle_size/2, -width/2)
        glVertex3f(width/2, -obstacle_size/2, -width/2)
        glVertex3f(width/2, -obstacle_size/2, width/2)
        glVertex3f(-width/2, -obstacle_size/2, width/2)

        glEnd()

    elif obstacle_type == "cylinder":
        glColor3f(0.8, 0, 1)
        quad = gluNewQuadric()
        glRotatef(90, 1, 0, 0)
        gluCylinder(quad, obstacle_size/2, obstacle_size/2, obstacle_size * 1.3, 32, 32)

        glPushMatrix()
        gluDisk(quad, 0, obstacle_size/2, 32, 32)
        glPopMatrix()

        glPushMatrix()
        glTranslatef(0, 0, obstacle_size * 1.3)
        gluDisk(quad, 0, obstacle_size/2, 32, 32)
        glPopMatrix()

    glPopMatrix()

def draw_obstacles():
    global road_length, obstacle_positions

    for obstacle_id in list(obstacle_positions.keys()):
        obs_x, obs_y, obs_z, obs_type, is_moving, direction = obstacle_positions[obstacle_id]

        if obs_y > road_length + 500:
            obstacle_positions.pop(obstacle_id)
            continue

        if -road_length < obs_y < road_length:
            draw_obstacle(obs_x, obs_y, obs_z, obs_type)

def draw_diamond(x, y, z):
    glPushMatrix()
    glTranslatef(x, y, z)
    # Yellow Color for Diamond Bullets
    glColor3f(1, 1, 0)

    size = ammo_size

    glBegin(GL_TRIANGLES)
    glVertex3f(0, 0, size)
    glVertex3f(size, 0, 0)
    glVertex3f(0, size, 0)

    glVertex3f(0, 0, size)
    glVertex3f(0, size, 0)
    glVertex3f(-size, 0, 0)

    glVertex3f(0, 0, size)
    glVertex3f(-size, 0, 0)
    glVertex3f(0, -size, 0)

    glVertex3f(0, 0, size)
    glVertex3f(0, -size, 0)
    glVertex3f(size, 0, 0)

    glVertex3f(0, 0, -size)
    glVertex3f(0, size, 0)
    glVertex3f(size, 0, 0)

    glVertex3f(0, 0, -size)
    glVertex3f(-size, 0, 0)
    glVertex3f(0, size, 0)

    glVertex3f(0, 0, -size)
    glVertex3f(0, -size, 0)
    glVertex3f(-size, 0, 0)

    glVertex3f(0, 0, -size)
    glVertex3f(size, 0, 0)
    glVertex3f(0, -size, 0)

    glEnd()
    glPopMatrix()

def draw_ammo():
    global road_length, ammo_positions

    for ammo_id in list(ammo_positions.keys()):
        ammo_x, ammo_y, ammo_z = ammo_positions[ammo_id]

        if ammo_y > road_length + 500:
            ammo_positions.pop(ammo_id)
            continue

        if -road_length < ammo_y < road_length:
            draw_diamond(ammo_x, ammo_y, ammo_z)


def draw_nitro_cylinder(nitro_x, nitro_y, nitro_z):
    glPushMatrix()
    glTranslatef(nitro_x, nitro_y, nitro_z+15)
    glRotatef(nitro_rotation_angle, 0, 0, 1)
    glRotatef(25, 0, 1, 0)
    
    glColor3f(1, 1, 0)


    quad = gluNewQuadric()
    gluCylinder(quad, 10, 10, 30, 32, 32) #quadric, baseRadius, topRadius, height, slices, stacks


    glPopMatrix()


def draw_nitro():
    global nitro_positions

    for nitro_id in list(nitro_positions.keys()):
        nitro_x, nitro_y, nitro_z = nitro_positions[nitro_id]

        if nitro_y > road_length + 500:
            nitro_positions.pop(nitro_id)
            continue

        if -road_length < nitro_y < road_length:
            draw_nitro_cylinder(nitro_x, nitro_y, nitro_z)


def draw_player_bullets():
    global road_length, road_width, player_bullets

    for bullet_id in list(player_bullets.keys()):
        px, py, pz, vx, vy, vz = player_bullets[bullet_id]

        if py < -road_length - 500 or py > road_length + 500 or px < -road_width - 100 or px > road_width + 100:
            player_bullets.pop(bullet_id)
            continue

        glPushMatrix()
        glTranslatef(px, py, pz)
        glColor3f(1, 1, 0)  # Bullet color changed to Yellow
        quad = gluNewQuadric()
        gluSphere(quad, 10, 16, 16)
        glPopMatrix()

def check_ammo_collision():
    global ammo_positions, bullet_count, car_x, car_y, car_z

    collection_distance = 80

    for ammo_id in list(ammo_positions.keys()):
        ammo_x, ammo_y, ammo_z = ammo_positions[ammo_id]

        distance = math.sqrt((car_x - ammo_x)**2 + (car_y - ammo_y)**2 + (car_z - ammo_z)**2)

        if distance < collection_distance:
            bullet_count += 1
            ammo_positions.pop(ammo_id)

def check_nitro_collision():
    global nitro_positions, nitro_count, car_x, car_y, car_z

    collection_distance = 80

    for nitro_id in list(nitro_positions.keys()):
        nitro_x, nitro_y, nitro_z = nitro_positions[nitro_id]

        distance = math.sqrt((car_x - nitro_x)**2 + (car_y - nitro_y)**2 + (car_z - nitro_z)**2)

        if distance < collection_distance:
            nitro_count += 1
            nitro_positions.pop(nitro_id)


def check_obstacle_collision():
    global obstacle_positions, life_remaining, car_x, car_y, car_z, cheatMode

    if not cheatMode:
        collision_distance = 150

        for obstacle_id in list(obstacle_positions.keys()):
            obs_x, obs_y, obs_z, obs_type, is_moving, direction = obstacle_positions[obstacle_id]

            distance = math.sqrt((car_x - obs_x)**2 + (car_y - obs_y)**2 + (car_z - obs_z)**2)

            if distance < collision_distance:
                life_remaining -= 1
                obstacle_positions.pop(obstacle_id)

def check_bullet_hit():
    global player_bullets, obstacle_positions, game_score

    hit_distance = 100

    for bullet_id in list(player_bullets.keys()):
        px, py, pz, vx, vy, vz = player_bullets[bullet_id]

        for obstacle_id in list(obstacle_positions.keys()):
            obs_x, obs_y, obs_z, obs_type, is_moving, direction = obstacle_positions[obstacle_id]

            distance = math.sqrt((px - obs_x)**2 + (py - obs_y)**2 + (pz - obs_z)**2)

            if distance < hit_distance:
                if bullet_id in player_bullets:
                    player_bullets.pop(bullet_id)
                if obstacle_id in obstacle_positions:
                    obstacle_positions.pop(obstacle_id)
                    game_score += 10 # Score increases by 10
                break

def draw_car():
    global car_x, car_y, car_z, car_rotation

    glPushMatrix()
    glTranslatef(car_x, car_y + 50, car_z)
    glRotatef(car_rotation, 1, 0, 0)
    glTranslatef(-car_x, -(car_y + 50), -car_z)

    glColor3f(0.1, 0.1, 0.1)
    quad = gluNewQuadric()
    for i in range(4):
        glPushMatrix()
        if i == 0:
            glTranslatef(car_x + 30, car_y, car_z)
            glRotatef(90, 0, 1, 0)
        elif i == 1:
            glTranslatef(car_x - 30, car_y, car_z)
            glRotatef(-90, 0, 1, 0)
        elif i == 2:
            glTranslatef(car_x + 30, car_y+100, car_z)
            glRotatef(90, 0, 1, 0)
        else:
            glTranslatef(car_x - 30, car_y+100, car_z)
            glRotatef(-90, 0, 1, 0)

        gluCylinder(quad, 12, 12, 20, 32, 32)
        glPopMatrix()

    glColor3f(0.7, 0.7, 0.7)
    glPushMatrix()
    glTranslatef(car_x, car_y-15, car_z + 12*2)
    glBegin(GL_QUADS)
    Y_LEN = 130

    glVertex3f(-50, 0, -15)
    glVertex3f( 50, 0, -15)
    glVertex3f( 50, Y_LEN, -15)
    glVertex3f(-50, Y_LEN, -15)

    glVertex3f(-50, 0, 15)
    glVertex3f( 50, 0, 15)
    glVertex3f( 50, Y_LEN, 15)
    glVertex3f(-50, Y_LEN, 15)

    glVertex3f(-50, Y_LEN, -15)
    glVertex3f( 50, Y_LEN, -15)
    glVertex3f( 50, Y_LEN, 15)
    glVertex3f(-50, Y_LEN, 15)

    glVertex3f(-50, 0, -15)
    glVertex3f( 50, 0, -15)
    glVertex3f( 50, 0, 15)
    glVertex3f(-50, 0, 15)

    glVertex3f(-50, 0, -15)
    glVertex3f(-50, Y_LEN, -15)
    glVertex3f(-50, Y_LEN, 15)
    glVertex3f(-50, 0, 15)

    glVertex3f(50, 0, -15)
    glVertex3f(50, Y_LEN, -15)
    glVertex3f(50, Y_LEN, 15)
    glVertex3f(50, 0, 15)

    glEnd()
    glPopMatrix()

    glPopMatrix()


def draw_Text(x, y, text, font=GLUT_BITMAP_HELVETICA_18): # type: ignore
    glColor3f(0.9,0.9,0.9)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()

    gluOrtho2D(0, 1000, 0, 800)

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    glRasterPos2f(x, y)
    glRasterPos2f(x, y)
    
    for char in text:
        glutBitmapCharacter(font, ord(char))
    
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def showScreen():
    global bullet_count, life_remaining, nitro_count, window_width,  window_height, cheatMode, isDay, game_score, isNitroMode, nitro_duration

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, window_width, window_height)

    setupCamera()

    # Draw 3D scene
    draw_sky()
    draw_road()
    draw_border()
    draw_ramp()
    draw_obstacles()
    draw_ammo()
    draw_nitro()
    draw_player_bullets()
    draw_car()

    # Draw 2D HUD - BULLETS TEXT IN BLACK
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, window_width, window_height, 0)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    if life_remaining == 0:
        draw_Text(440, 380, f"GAME OVER!")
        draw_Text(380, 350, f"Press 'R' to Restart the game")
    else:
        if cheatMode:
            draw_Text(window_width//2 - 75, window_height-30, f"Cheat Mode is ON!")

        draw_Text(20, 80, f"Life remaining: {life_remaining}")
        draw_Text(20, 50, f"Game Score: {int(game_score)}")
        draw_Text(20, 20, f"Bullets: {bullet_count}")
        draw_Text(150, 20, f"Nitro: {nitro_count}")
    

    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()

    glutSwapBuffers()

# ================= AUTO AVOIDANCE LOGIC =================
def auto_avoid_obstacles():
    global car_x, obstacle_positions, road_width

    lanes = [-200, 0, 200]
    current_lane_index = 0
    min_dist = float('inf')
    
    # Find which lane we are currently closest
    for i, lane_x in enumerate(lanes):
        dist = abs(car_x - lane_x)
        if dist < min_dist:
            min_dist = dist
            current_lane_index = i

    # Analyze threats in all lanes
    lane_safety = {0: 9999, 1: 9999, 2: 9999}
    
    CAR_Y = 3700
    
    for obs in obstacle_positions.values():
        ox, oy, _, _, _, _ = obs
        
        # Calculate distance to car (assuming obstacle is approaching)
        dist_to_car = CAR_Y - oy
        
        # Scan range: look 2000 units ahead
        if 0 < dist_to_car < 2000:
            obs_lane = -1
            if abs(ox - (-200)) < 80: obs_lane = 0
            elif abs(ox - 0) < 80: obs_lane = 1
            elif abs(ox - 200) < 80: obs_lane = 2
            
            if obs_lane != -1:
                # Update safety score (keep smallest distance)
                if dist_to_car < lane_safety[obs_lane]:
                    lane_safety[obs_lane] = dist_to_car

    # current lane has a obstacle closer than SAFE_DISTANCE ==> move.
    SAFE_DISTANCE = 800
    
    target_lane_index = current_lane_index
    current_lane_safety = lane_safety[current_lane_index]
    
    if current_lane_safety < SAFE_DISTANCE:
        # Find best neighbor
        options = []
        if current_lane_index > 0: options.append(current_lane_index - 1)
        if current_lane_index < 2: options.append(current_lane_index + 1)
            
        best_option = -1
        max_safety = -1
        
        for op in options:
            if lane_safety[op] > max_safety:
                max_safety = lane_safety[op]
                best_option = op
        
        # Move if neighbor is safer
        if max_safety > current_lane_safety:
            target_lane_index = best_option
        else:
            # Trap logic: Pick global safest if stuck
            best_global = max(lane_safety, key=lane_safety.get)
            if lane_safety[best_global] > current_lane_safety:
                if best_global > current_lane_index: target_lane_index += 1
                elif best_global < current_lane_index: target_lane_index -= 1

    # 4. Execute Move (Smooth but fast steer)
    target_x = lanes[target_lane_index]
    steer_speed = 30
    
    if car_x < target_x:
        car_x += steer_speed
        if car_x > target_x: car_x = target_x
    elif car_x > target_x:
        car_x -= steer_speed
        if car_x < target_x: car_x = target_x

def animate():
    # Game state & timing
    global game_speed, last_time, isPaused, total_distance, game_score, initial_speed

    # World / scrolling
    global element_offset

    # Car state & movement
    global car_x, car_y, car_z, car_rotation
    global is_jumping, jump_phase, max_height

    # Ramp system
    global ramp_positions, ramp_width, ramp_angle
    global last_ramp_time, ramp_spawn_delay

    # Obstacles & combat
    global obstacle_positions
    global ammo_positions, player_bullets

    # Nitro system
    global nitro_rotation_angle, isNitroMode, nitro_count, nitro_speed, previous_speed

    current_time = time.time()
    
    if life_remaining > 0:
        if not isPaused:

            if cheatMode:
                auto_avoid_obstacles()
            
            game_score = total_distance//1000
            calculated_speed = min(initial_speed + (game_score * speed_increase_rate), max_speed)
            previous_speed = calculated_speed

            dt = current_time - last_time
            last_time = current_time

            if isNitroMode:
                game_speed = nitro_speed
                if current_time - nitro_start_time >= nitro_duration:
                    isNitroMode = False
                    game_speed = previous_speed
            else:
                game_speed = previous_speed
    
            distance_this_frame = game_speed * dt * 100
            total_distance += distance_this_frame
    
            element_offset -= game_speed * dt * 100

            

    
            for id, positions in ramp_positions.items():
                ramp_x, ramp_y, ramp_z = positions
                ramp_y += game_speed * dt * 100
                ramp_positions[id] = (ramp_x, ramp_y, ramp_z)
    
            if current_time - last_ramp_time >= ramp_spawn_delay:
                new_x = random.randint(-200, 200)
                new_y = 0
                new_z = 2
                ramp_id = max(ramp_positions.keys(), default=0) + 1
                ramp_positions[ramp_id] = (new_x, new_y, new_z)
                last_ramp_time = current_time
    
            for obstacle_id in list(obstacle_positions.keys()):
                obs_x, obs_y, obs_z, obs_type, is_moving, direction = obstacle_positions[obstacle_id]
    
                obs_y += game_speed * dt * 100
    
                if is_moving:
                    obs_x += direction * obstacle_speed * dt
    
                obstacle_positions[obstacle_id] = (obs_x, obs_y, obs_z, obs_type, is_moving, direction)
    
            for ammo_id in list(ammo_positions.keys()):
                ammo_x, ammo_y, ammo_z = ammo_positions[ammo_id]
    
                ammo_y += game_speed * dt * 100
    
                ammo_positions[ammo_id] = (ammo_x, ammo_y, ammo_z)
    
            for bullet_id in list(player_bullets.keys()):
                px, py, pz, vx, vy, vz = player_bullets[bullet_id]
    
                px += vx * dt
                py += vy * dt
                pz += vz * dt
    
                player_bullets[bullet_id] = (px, py, pz, vx, vy, vz)


            for id, positions in nitro_positions.items():
                nitro_x, nitro_y, nitro_z = positions
                nitro_y += game_speed * dt * 100
                nitro_positions[id] = (nitro_x, nitro_y, nitro_z)

            
            nitro_rotation_angle = (nitro_rotation_angle + 1) % 360

            spawn_obstacle()
            spawn_ammo()
            spawn_nitro()
    
            check_ammo_collision()
            check_obstacle_collision()
            check_nitro_collision()
            check_bullet_hit()
    
    
            # jumping animation
            if not is_jumping:
                for ramp_x, ramp_y, ramp_z in ramp_positions.values():
                    if abs(car_x - ramp_x) < (ramp_width/2 + 50) and abs(car_y - ramp_y) < ramp_length/2:
                        is_jumping = True
                        jump_phase = "ramp"
                        break
                    
            if is_jumping:
                rotation_step = 20 * dt * game_speed
                jumping_step = 60 * dt * game_speed
    
                if jump_phase == "ramp":
                    car_rotation -= rotation_step
                    car_z += jumping_step
                    if car_rotation <= -45:
                        car_rotation = -45
                        jump_phase = "going_up"
    
                elif jump_phase == "going_up":
                    car_z += jumping_step
                    if car_z >= max_height/2:
                        car_rotation = min(car_rotation+rotation_step, 0)
                    if car_z >= max_height:
                        car_z = max_height
                        jump_phase = "land"
    
                elif jump_phase == "land":
                    car_z -= jumping_step
                    if car_z <= max_height/2:
                        car_rotation = max(car_rotation-rotation_step, 0)
                    
                    if car_z <= 16:
                        car_z = 16
    
                        is_jumping = False

    glutPostRedisplay()

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(window_width, window_height)
    glutInitWindowPosition(300,100)
    glutCreateWindow(b"Noob Driver")

    glEnable(GL_DEPTH_TEST)

    glutDisplayFunc(showScreen)
    glutIdleFunc(animate)

    glutSpecialFunc(specialKeyboardListener)
    glutMouseFunc(mouseListener)
    glutKeyboardFunc(keyboardListener)

    glutMainLoop()

if __name__ == "__main__":
    main()