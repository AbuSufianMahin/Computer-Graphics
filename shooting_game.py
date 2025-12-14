from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import math

fovY = 120
GRID_LENGTH = 600

# window size
window_width = 1000
window_height = 800

# game stats
life_remaining = 5
game_score = 0
bullet_missed = 0
missed_bullet_limit = 10

cheat_mode = False
game_over = False

# player stats
player_x, player_y, player_z = random.randint(-300, 300), random.randint(-300, 300), 80 # spawning in somewhere in the middle

player_angle = 0
player_speed = 25
player_body_size = 40

# enemies stats
enemy_count = 5
enemy_size_multiplier = 1
enemy_speed = 0.1
enemy_body_size = 35

enemy_growing = True
enemy_info = {}

# bullet
bullet_info = {} # { int id : {'x' : _, 'y': _, 'vx': _, 'vy': _}, {...}}
bullet_speed = 10

# Camera-related variables
default_camera_position = (0, 500, 500)
camera_position = default_camera_position
first_person_mode = False
gun_tracking = True


# listeners
def keyboardListener(key, x, y):
    global life_remaining, game_score, bullet_missed, cheat_mode, game_over
    global player_x, player_y, player_z, player_speed, player_angle
    global first_person_mode, camera_position, gun_tracking

    # not allowing key press movement after game is over
    if not game_over:
        if key == b'c':
            cheat_mode = not cheat_mode 
        
        rad = math.radians(player_angle)

        # Forward
        if key == b'w':
            if (-590 < player_x + player_speed * math.sin(rad) < 590) and (- 590 < player_y - player_speed * math.cos(rad) < 590):
                player_x += player_speed * math.sin(rad)
                player_y -= player_speed * math.cos(rad)
            else:
                print("Can't move Farther. Change direction!")
                

        # Backward
        if key == b's':
            if (-590 < player_x - player_speed * math.sin(rad) < 590) and (-590 < player_y + player_speed * math.cos(rad) < 590):
                player_x -= player_speed * math.sin(rad)
                player_y += player_speed * math.cos(rad)
            else:
                print("Can't move Farther. Change direction!")
                

        if key == b'd':  # rotate right
            player_angle = (player_angle - 5) % 360

        if key == b'a':  # rotate left
            player_angle = (player_angle + 5) % 360

        # Remove FPP and set near-head third-person view
        if key == b'v':
            if cheat_mode:
                gun_tracking = not gun_tracking


    if key == b'r':
        life_remaining = 5 
        game_score = 0 
        bullet_missed = 0 
        first_person_mode = False
        game_over = False
        cheat_mode = False
        enemy_info = {}
        bullet_info = {}
        player_x, player_y, player_z = random.randint(-300, 300), random.randint(-300, 300), 80

def specialKeyListener(key, x, y):
    global camera_position, dx
    x, y, z = camera_position

    # Move camera up (UP arrow key)
    if key == GLUT_KEY_UP:
        z -= 5
    # # Move camera down (DOWN arrow key)
    if key == GLUT_KEY_DOWN:
        z += 5


    # moving camera left (LEFT arrow key)
    if key == GLUT_KEY_LEFT:
        x += 5 

    # moving camera right (RIGHT arrow key)
    if key == GLUT_KEY_RIGHT:
        x -= 5
    
    camera_position = (x, y, z)    
    
def mouseListener(button, state, x, y):
    global bullet_info, player_x, player_y, player_z, player_angle, bullet_speed, camera_position, first_person_mode, default_camera_position
    # Handle left mouse button click
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        angle_rad = math.radians(player_angle)
        
        bullet_id = len(bullet_info) + 1
        bullet_info[bullet_id] = {
            "x": player_x,
            "y": player_y,
            "vx": bullet_speed * math.sin(angle_rad), 
            "vy": -bullet_speed * math.cos(angle_rad)
        }

    if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        first_person_mode = not first_person_mode
        if not first_person_mode:
            camera_position = default_camera_position

def setupCamera():
    global camera_position, window_width, window_height, first_person_mode, player_x, player_y, player_z, player_angle, gun_tracking
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()

    gluPerspective(fovY, window_width / window_width, 0.5, 2500)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    # setting camera orientation
    if first_person_mode:
        rad = math.radians(player_angle)
        cam_x, cam_y, cam_z = player_x, player_y + 10, player_z + 40
        look_x = player_x + math.sin(rad) * 100 
        look_y = player_y + 10 - math.cos(rad) * 100
        look_z = cam_z + 10

        # changin focus point
        if gun_tracking:
            gluLookAt(cam_x, cam_y, cam_z,
                look_x, look_y, look_z,
                0, 0, 1)
        else:
            gluLookAt(cam_x, cam_y, cam_z,
                0, 0, 0,
                0, 0, 1)


    else:
        x, y, z = camera_position
        gluLookAt(x, y, z, 
                  0, 0, 0,
                  0, 0, 1)  
    
def drawText(x, y, text, font=GLUT_BITMAP_HELVETICA_18): # type: ignore
    glColor3f(1,1,1)
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

def drawGameFloor(tilesCount, borderHeight):
    # drawing the vertical border
    glBegin(GL_QUADS)

    # bottom
    glColor3f(1, 1, 1)
    glVertex3f(-GRID_LENGTH, GRID_LENGTH, 0)
    glVertex3f(-GRID_LENGTH, GRID_LENGTH, borderHeight)
    glVertex3f(GRID_LENGTH, GRID_LENGTH, borderHeight)
    glVertex3f(GRID_LENGTH, GRID_LENGTH, 0)

    # left
    glColor3f(0, 0, 1)
    glVertex3f(GRID_LENGTH, GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH, GRID_LENGTH, borderHeight)
    glVertex3f(GRID_LENGTH, -GRID_LENGTH, borderHeight)
    glVertex3f(GRID_LENGTH, -GRID_LENGTH, 0)

    # top
    glColor3f(0, 1, 1)
    glVertex3f(GRID_LENGTH, -GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH, -GRID_LENGTH, borderHeight)
    glVertex3f(-GRID_LENGTH, -GRID_LENGTH, borderHeight)
    glVertex3f(-GRID_LENGTH, -GRID_LENGTH, 0)

    # right
    glColor3f(0, 1, 0)
    glVertex3f(-GRID_LENGTH, -GRID_LENGTH, 0)
    glVertex3f(-GRID_LENGTH, -GRID_LENGTH, borderHeight)
    glVertex3f(-GRID_LENGTH, GRID_LENGTH, borderHeight)
    glVertex3f(-GRID_LENGTH, GRID_LENGTH, 0)

    glEnd()



    glBegin(GL_QUADS)
    # drawing the tiles
    titleLength = (2*(GRID_LENGTH))/tilesCount

    bottom_left_x = GRID_LENGTH
    bottom_left_y = GRID_LENGTH
    bottom_left_z = 0

    bottom_right_x = bottom_left_x - titleLength
    bottom_right_y = bottom_left_y
    bottom_right_z = bottom_left_z

    top_left_x = bottom_left_x
    top_left_y = bottom_left_y - titleLength
    top_left_z = bottom_left_z 

    top_right_x = bottom_left_x - titleLength
    top_right_y = bottom_left_y - titleLength
    top_right_z = bottom_left_z 

    for i in range(tilesCount):
        for j in range(tilesCount):
            if i%2 == 0:
                if j%2 == 0:
                    glColor3f(1, 1, 1)
                else:
                    glColor3f(0.7, 0.5, 0.95)
            else:
                if j%2 == 0:
                    glColor3f(0.7, 0.5, 0.95)
                else:
                    glColor3f(1, 1, 1)


            glVertex3f(bottom_left_x, bottom_left_y, bottom_left_z)
            glVertex3f(top_left_x, top_left_y, top_left_z)
            glVertex3f(top_right_x, top_right_y, top_right_z)
            glVertex3f(bottom_right_x, bottom_right_y, bottom_right_z)


            bottom_left_x -= titleLength

            bottom_right_x = bottom_left_x - titleLength
            bottom_right_y = bottom_left_y
            bottom_right_z = bottom_left_z

            top_left_x = bottom_left_x
            top_left_y = bottom_left_y - titleLength
            top_left_z = bottom_left_z 

            top_right_x = bottom_left_x - titleLength
            top_right_y = bottom_left_y - titleLength
            top_right_z = bottom_left_z 

        bottom_left_x = GRID_LENGTH
        bottom_left_y -= titleLength
        bottom_left_z = 0

        bottom_right_x = bottom_left_x - titleLength
        bottom_right_y = bottom_left_y
        bottom_right_z = bottom_left_z

        top_left_x = bottom_left_x
        top_left_y = bottom_left_y - titleLength
        top_left_z = bottom_left_z 

        top_right_x = bottom_left_x - titleLength
        top_right_y = bottom_left_y - titleLength
        top_right_z = bottom_left_z 
    
    glEnd()

def drawPlayer():
    global player_body_size, player_x, player_y, player_z, player_angle, game_over
    
    # headd
    glPushMatrix()
    glColor3f(0.2, 0.2, 0.2)
    glTranslatef(player_x, player_y, player_z)
    glRotatef(player_angle, 0, 0, 1)

    # Lie down on game over
    if game_over:
        glTranslatef(0, 0, -60)
        glRotatef(-90, 1, 0, 0)

    
    gluSphere(gluNewQuadric(), 15, 100, 100)

    # body
    glColor3f(0, 0.4, 0)
    glTranslatef(0, 0, -30)
    glutSolidCube(player_body_size)

    # hand1
    glColor3f(1.0, 0.5, 0.0)
    glTranslatef(15, -20, 10)
    glRotatef(90, 1, 0, 0) 
    gluCylinder(gluNewQuadric(), 6, 2, 20, 10, 10) #quadric, baseRadius, topRadius, height, slices, stacks

    # hand2
    glTranslatef(-30, 0, 0)
    gluCylinder(gluNewQuadric(), 6, 2, 20, 10, 10)

    #gun
    glColor3f(0.3, 0.3, 0.3)
    glTranslatef(15, 0, 0)
    gluCylinder(gluNewQuadric(), 6, 2, 30, 10, 10)

    # legs
    glColor3f(1.0, 0.5, 0.0)
    glRotatef(90, 1, 0, 0)
    glTranslatef(-10, -15, 20)
    gluCylinder(gluNewQuadric(), 10, 5, 40, 10, 10) #quadric, baseRadius, topRadius, height, slices, stacks

    glTranslatef(20, 0, 0)
    gluCylinder(gluNewQuadric(), 10, 5, 40, 10, 10)

    glPopMatrix()

def drawEnemy(x, y):
    global enemy_size_multiplier,  enemy_body_size

    # enemy head
    glPushMatrix()
    glColor3f(0.2, 0.2, 0.2)
    glTranslatef(x, y, 70)
    glScalef(enemy_size_multiplier, enemy_size_multiplier, enemy_size_multiplier)
    gluSphere(gluNewQuadric(), 15, 100, 100)
    glPopMatrix()

    # enemy body
    glPushMatrix()
    glColor3f(1.0, 0.0, 0.0)
    glTranslatef(x, y, 30)
    glScalef(enemy_size_multiplier, enemy_size_multiplier, enemy_size_multiplier)
    gluSphere(gluNewQuadric(), enemy_body_size, 100, 100)
    glPopMatrix()

def drawBullet(x, y):
    global player_z
    glPushMatrix()
    glColor3f(1.0, 0, 0.0)
    glTranslatef(x, y, player_z - 20)
    glutSolidCube(10)
    glPopMatrix()

def animate():
    global enemy_size_multiplier, enemy_body_size, enemy_growing, bullet_info, bullet_missed, missed_bullet_limit, game_over
    global enemy_info, enemy_speed, player_x, player_y, life_remaining, game_score, player_angle
    
    step = 0.002

    if enemy_growing:
        if enemy_size_multiplier < 1.25:
            enemy_size_multiplier += step
        else:
            enemy_growing = False
    else:
        if enemy_size_multiplier > 1:
            enemy_size_multiplier -= step
        else:
            enemy_growing = True
    
    # Update bullets
    if not game_over:
        if cheat_mode:
            player_angle = (player_angle + 1.5) % 360

            alignment_tolerance = 1  # degrees
            for key, enemy in enemy_info.items():
                enemy_x = enemy['x']
                enemy_y = enemy['y']

                dx = enemy_x - player_x
                dy = enemy_y - player_y
                
                angle_to_enemy = math.degrees(math.atan2(dx, -dy)) % 360
                angle_diff = abs(player_angle - angle_to_enemy)

                if angle_diff <= alignment_tolerance:
                    # adding a bullet when aligned with an enemy
                    angle_rad = math.radians(player_angle)
                    bullet_id = len(bullet_info) + 1
                    bullet_info[bullet_id] = {
                        "x": player_x,
                        "y": player_y,
                        "vx": bullet_speed * math.sin(angle_rad),
                        "vy": -bullet_speed * math.cos(angle_rad)
                    }
                    break

        for key, bullet_value in list(bullet_info.items()):
            bullet_value["x"] += bullet_value["vx"]
            bullet_value["y"] += bullet_value["vy"]

            # bullet-boundary collision detection
            if abs(bullet_value["x"]) > GRID_LENGTH or abs(bullet_value["y"]) > GRID_LENGTH:
                bullet_missed += 1
                print(f"Bullet missed: {bullet_missed}")

                if bullet_missed >= missed_bullet_limit:
                    game_over = True

                bullet_info.pop(key)

            # bullet-enemy hit detection
            for enemy_id, enemy in list(enemy_info.items()):
                enemy_bullet_dx = bullet_value["x"] - enemy["x"]
                enemy_bullet_dy = bullet_value["y"] - enemy["y"]
                distance = math.sqrt(enemy_bullet_dx**2 + enemy_bullet_dy**2)
                
                # Check collision 
                if distance < enemy_body_size:
                    bullet_info.pop(key)
                    enemy_info.pop(enemy_id)
                    game_score += 1
                    break

    
        # enemy moving towards player
        for enemy_id, enemy in list(enemy_info.items()):

            player_enemy_dx = player_x - enemy["x"]
            player_enemy_dy = player_y - enemy["y"]
            distance = math.sqrt(player_enemy_dx**2 + player_enemy_dy**2)
            
            # player-enemy collision detection
            if distance < 45:
                life_remaining -= 1
                print(f"Remaining Player Life: {life_remaining}")
                enemy_info.pop(enemy_id)

                if life_remaining <= 0:
                    game_over = True
            
            else:
                enemy["x"] += (player_enemy_dx / distance) * enemy_speed
                enemy["y"] += (player_enemy_dy / distance) * enemy_speed
    
    glutPostRedisplay()

def showWindow():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, window_width, window_height)

    setupCamera()

    # drawing the corners
    glPointSize(1)
    glBegin(GL_POINTS)
    # bottom left
    glVertex3f(GRID_LENGTH, GRID_LENGTH, 0)
    # bottom right
    glVertex3f(-GRID_LENGTH, GRID_LENGTH, 0)
    # top left
    glVertex3f(GRID_LENGTH, -GRID_LENGTH, 0)
    # top right
    glVertex3f(-GRID_LENGTH, -GRID_LENGTH, 0)
    glEnd()

    # game instructions
    if game_over:
        drawText(10, 770, f"Game Over. Your score is {game_score}.")
        drawText(10, 750, f"Press 'R' to RESTART the game.")
    else:
        drawText(10, 770, f"Life Remaining: {life_remaining}")
        drawText(10, 750, f"Game Score: {game_score}")
        drawText(10, 730, f"Missed Bullet: {bullet_missed}")

        if cheat_mode:
            drawText(10, 710, f"Cheat Mode: ON")
        else:
            drawText(10, 710, f"Cheat Mode: OFF")
        


    # drawing the game floor tiles
    tiles_count = 15
    border_height = 100
    drawGameFloor(tiles_count, border_height)


    # drawing the player
    drawPlayer()


    if not game_over:
        # drawing enemy
        for i in range(enemy_count):
            if i not in enemy_info:
                enemy_info[i] = {
                    "x": random.randint(-500, 500),
                    "y": random.randint(-500, 500),
                }
    
        for value in enemy_info.values():
            x, y = value["x"], value["y"]
            drawEnemy(x, y)

        # draw bullets
        for b in bullet_info.values():
            drawBullet(b["x"], b["y"])

    glutSwapBuffers()


def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    # window related functions
    glutInitWindowSize(window_width, window_height)
    glutInitWindowPosition(300,100)
    glutCreateWindow(b"Shooting Game")
    glEnable(GL_DEPTH_TEST)
    glutDisplayFunc(showWindow)


    # listeners
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutKeyboardFunc(keyboardListener)

    # animate function
    glutIdleFunc(animate)
    

    glutMainLoop()

if __name__ == "__main__":
    main()