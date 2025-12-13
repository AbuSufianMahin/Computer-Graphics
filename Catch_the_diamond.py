from OpenGL.GL import *     
from OpenGL.GLUT import *   
from OpenGL.GLU import *
import random
import time

def generate_random_color():
    lower_limit = 0.3
    upper_limit = 1
    return ( random.uniform(lower_limit, upper_limit), random.uniform(lower_limit, upper_limit), random.uniform(lower_limit, upper_limit))

last_time = time.time()
window_width, window_height = 600, 700

isPaused = False
gameOver = False
cheatMode = False
score = 0
diamond_falling_speed = 200

# diamond_top_x = random.randint(20, 580)
diamond_top_x = 20
diamond_top_y = 630
diamond_color = generate_random_color()

catcher_width = 130
catcher_height = 20
catcher_offset_x = 15

catcher_top_left_x = random.randint(10, 600 - 10 - catcher_width)
catcher_ceiling_y = 40

catcher_step = 15



def convert_coordinate(y):
    return window_height - y

def mouse_event_listener(button, state, x, y):
    global isPaused, gameOver, cheatMode, score, diamond_falling_speed, diamond_top_x, diamond_top_y, catcher_top_left_x, diamond_color
    y = convert_coordinate(y)
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        if 650 <= y <= 690:
            # reset button
            if 20 <= x <= 80:
                isPaused = False
                gameOver = False
                cheatMode = False
                score = 0
                diamond_top_x = random.randint(20, 580)
                diamond_top_y = 630
                catcher_top_left_x = random.randint(10, 600 - 10 - catcher_width)
                diamond_falling_speed = 200
                diamond_color = generate_random_color()
                print("Game Restarted! Score: 0")

            # pause button
            elif 280 <= x <= 320:
                isPaused = not isPaused

            # close button
            elif 540 <= x <= 580:
                print(f"Goodbye!\nScore: {score}")
                glutLeaveMainLoop()

def keyboard_listener(key,x,y):
    global cheatMode
    if key == b'c':
        cheatMode = not cheatMode
        if cheatMode:
            print("Cheat Mode Activated")
        else:
            print("Cheat Mode Deactivated")

def special_keyboard_listener(key, x, y):
    global isPaused, gameOver, cheatMode, catcher_top_left_x, catcher_width, catcher_step

    # disabling user controll on cheat mode
    if isPaused != True and gameOver != True and cheatMode != True:
        if key == GLUT_KEY_RIGHT:
            if (catcher_top_left_x + catcher_width + catcher_step) <= 590 :
                catcher_top_left_x += catcher_step

        elif key == GLUT_KEY_LEFT:
            if (catcher_top_left_x - catcher_step) >= 10 :
                catcher_top_left_x -= catcher_step
    
    
    glutPostRedisplay()

def draw_point(x,y, size):
    glPointSize(size)      
    glBegin(GL_POINTS)      
    glVertex2f(x,y)
    glEnd()

def find_zone(dx, dy):
    # top right quadrant
    if dx >= 0 and dy >= 0:
        if abs(dx) >= abs(dy):
            return 0
        else:
            return 1
        
    # top left quadrant
    elif dx <= 0 and dy >= 0:
        if abs(dy) > abs(dx):
            return 2
        else:
            return 3
    
    # bottom left quadrant
    elif dx <= 0 and dy <= 0:
        if abs(dx) > abs(dy):
            return 4
        else:
            return 5

    # bottom right
    else:
        if abs(dy) > abs(dx):
            return 6
        else:
            return 7

def convert_to_zoneX(x, y, zone_number):
    # target zone == zone_number from zone 0
    if zone_number == 1:
        return (y, x)
    elif zone_number == 2:
        return (-y, x)
    elif zone_number == 3:
        return (-x, y)
    elif zone_number == 4:
        return (-x, -y)
    elif zone_number == 5:
        return (-y, -x)
    elif zone_number == 6:
        return (y, -x)
    elif zone_number == 7:
        return (x, -y)

def convert_to_zone0(x,y, zone_number):
    # target zone == 0 from zone x
    if zone_number == 1:
        return (y, x)
    elif zone_number == 2:
        return (y, -x)
    elif zone_number == 3:
        return (-x, y)
    elif zone_number == 4:
        return (-x, -y)
    elif zone_number == 5:
        return (-y, -x)
    elif zone_number == 6:
        return (-y, x)
    elif zone_number == 7:
        return (x, -y)

def draw_line_MPL(x0,y0, x1,y1, width=2):
    zone_number = find_zone(x1 - x0, y1 - y0)

    if zone_number != 0:
        x0, y0 = convert_to_zone0(x0, y0, zone_number)
        x1, y1 = convert_to_zone0(x1, y1, zone_number)

    dx = x1 - x0
    dy = y1 - y0

    dx_double = 2*dx
    dy_double = 2*dy

    d = dy_double - dx

    while x0 <= x1:
        if zone_number != 0:
            x, y = convert_to_zoneX(x0, y0, zone_number)
        else: 
            x, y = x0, y0

        draw_point(x,y, width)

        if d > 0:
            x0 += 1
            y0 += 1
            d = d + dy_double - dx_double
        else:   
            x0 += 1
            d = d + dy_double

def draw_reset_button():
    glColor3f(0.0, 1.0, 1.0)

    draw_line_MPL(20,670, 40,690)
    draw_line_MPL(20,670, 80,670)
    draw_line_MPL(20,670, 40,650)

def draw_pause_button():
    glColor3f(1.0, 0.8, 0.0)
    if isPaused:
        draw_line_MPL(280,690, 280,650)     
        draw_line_MPL(280,690, 320,670)
        draw_line_MPL(280,650, 320,670)
    else:
        draw_line_MPL(290,690, 290,650)
        draw_line_MPL(310,690, 310,650)

def draw_exit_button():
    glColor3f(1.0, 0.0, 0.0)
    draw_line_MPL(540,690, 580,650)
    draw_line_MPL(540,650, 580,690)

def calculate_diamond_coords():
    global diamond_top_x, diamond_top_y, diamond_color
    
    offset_x = 12
    offset_y = 18

    diamond_left_x, diamond_left_y = (diamond_top_x - offset_x), (diamond_top_y - offset_y)
    diamond_right_x, diamond_right_y = (diamond_top_x + offset_x), (diamond_top_y - offset_y)
    diamond_bottom_x, diamond_bottom_y = diamond_top_x, (diamond_top_y - offset_y*2)

    return {
        "top": (diamond_top_x, diamond_top_y),
        "left": (diamond_left_x, diamond_left_y),
        "right": (diamond_right_x, diamond_right_y),
        "bottom": (diamond_bottom_x, diamond_bottom_y)
    }

def draw_diamond():
    global gameOver

    if not gameOver:
        diamond_position = calculate_diamond_coords()

        top_x, top_y = diamond_position["top"]
        left_x, left_y = diamond_position["left"]
        right_x, right_y = diamond_position["right"]
        bottom_x, bottom_y = diamond_position["bottom"]

        glColor3f(diamond_color[0], diamond_color[1], diamond_color[2])

        draw_line_MPL(top_x, top_y, left_x, left_y)
        draw_line_MPL(top_x, top_y, right_x, right_y)
        draw_line_MPL(left_x, left_y, bottom_x, bottom_y)
        draw_line_MPL(right_x, right_y, bottom_x, bottom_y)


def calculate_catcher_coords():
    global catcher_top_left_x, catcher_ceiling_y, catcher_width, catcher_height, catcher_offset_x

    catcher_floor_y = catcher_ceiling_y - catcher_height

    catcher_top_right_x = catcher_top_left_x + catcher_width

    catcher_bottom_left_x = catcher_top_left_x + catcher_offset_x
    catcher_bottom_right_x = catcher_top_right_x - catcher_offset_x

    return {
        "top_left": (catcher_top_left_x, catcher_ceiling_y),
        "top_right": (catcher_top_right_x, catcher_ceiling_y),
        "bottom_left": (catcher_bottom_left_x, catcher_floor_y),
        "bottom_right": (catcher_bottom_right_x, catcher_floor_y)
    }

def draw_catcher(): 
    positions = calculate_catcher_coords()

    top_left_x, top_left_y = positions["top_left"]
    top_right_x, top_right_y = positions["top_right"]
    bottom_left_x, bottom_left_y = positions["bottom_left"]
    bottom_right_x, bottom_right_y = positions["bottom_right"]

    if gameOver:
        glColor3f(1.0, 0.0, 0.0)
    else:
        glColor3f(1.0, 1.0, 1.0)
    
    # ceiling & floor
    draw_line_MPL(top_left_x, top_left_y, top_right_x, top_right_y)
    draw_line_MPL(bottom_left_x, bottom_left_y, bottom_right_x, bottom_right_y)

    # left & right walls
    draw_line_MPL(top_left_x, top_left_y, bottom_left_x, bottom_left_y)
    draw_line_MPL(top_right_x, top_right_y, bottom_right_x, bottom_right_y)


def animate_diamond_fall():
    global isPaused, gameOver, window_width, catcher_width, diamond_falling_speed, diamond_top_x, diamond_top_y, score, catcher_ceiling_y, last_time, catcher_step, diamond_color, catcher_top_left_x

    current_time = time.time()
    dt = current_time - last_time
    last_time = current_time
    
    if not isPaused and not gameOver:
        diamond_top_y -= diamond_falling_speed * dt

        diamond_position = calculate_diamond_coords()
        catcher_positions = calculate_catcher_coords()

        dia_bottom_x, dia_bottom_y = diamond_position["bottom"]
        catcher_top_right_x = catcher_positions["top_right"][0]

        if cheatMode: 
            vertical_distance = dia_bottom_y - catcher_ceiling_y
            time_to_impact = vertical_distance / (diamond_falling_speed * dt)
            
            catcher_center_x = (catcher_top_left_x + catcher_top_right_x)/2
            horizontal_distance = dia_bottom_x - catcher_center_x

            required_speed = horizontal_distance / time_to_impact

            catcher_top_left_x += required_speed

            # if catcher_top_left_x < 10:
            #     catcher_top_left_x = 10
            # elif catcher_top_left_x > window_width - catcher_width - 10:
            #     catcher_top_left_x = window_width - catcher_width - 10
            # else:
            #     catcher_top_left_x += required_speed
                



        if  0 < dia_bottom_y <= catcher_ceiling_y:
            if catcher_top_left_x <= dia_bottom_x <= catcher_top_right_x:
                score += 1
                print("Score:", score)
                diamond_falling_speed += 20

                diamond_top_x = random.randint(20, 580)
                diamond_top_y = 630

                diamond_color = generate_random_color()

        elif dia_bottom_y <= 0:
            print("Game Over! Your score:", score)
            gameOver = True

    glutPostRedisplay()
    
   
def setup_projection():
    glViewport(0, 0, window_width, window_height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0.0, window_width, 0.0, window_height, 0.0, 1.0)
    glMatrixMode(GL_MODELVIEW)  

def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    setup_projection()
    
    # all functions
    # buttons
    draw_reset_button()
    draw_pause_button()
    draw_exit_button()

    # game components
    draw_diamond()
    draw_catcher()
    # shows graphics on the screen
    glutSwapBuffers() 

def main():
    glutInit()                      
    glutInitDisplayMode(GLUT_RGBA)  

    glutInitWindowSize(window_width, window_height)

    # window position (centered)
    screen_width, screen_height = glutGet(GLUT_SCREEN_WIDTH), glutGet(GLUT_SCREEN_HEIGHT)
    starting_x, starting_y = (screen_width - window_width)//2, (screen_height-window_height)//2
    # starting_x, starting_y = 500, 200
    glutInitWindowPosition(starting_x, starting_y)

    glutCreateWindow(b"Catch the Diamonds!")
    glutDisplayFunc(display)

    glutIdleFunc(animate_diamond_fall)


    # even listeners
    glutMouseFunc(mouse_event_listener)
    glutKeyboardFunc(keyboard_listener)
    glutSpecialFunc(special_keyboard_listener)
    

    glutMainLoop()

if __name__ == "__main__":
    main()