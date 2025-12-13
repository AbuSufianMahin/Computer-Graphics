from OpenGL.GL import *     
from OpenGL.GLUT import *   
from OpenGL.GLU import *
import random

window_width, window_height = 800, 500

ball_speed = 0.01
speed_step = 0.01

max_speed = 0.5
min_speed = 0.01

freezed = False
blink = False


# current-direction can be 0 -> 45 degree, 1->135 degree, 2->225 degree and 3->315 degree
'''{
    "direction": random.randint(0,3),
    "x": x,
    "y": convert_coordinate(y),
    "color": (random.random(), random.random(), random.random())
}'''

particles = []

def convert_coordinate(y):
    # converting glutMouseFunc to my own defined coordinate
    return window_height - y

def special_key_listener(key, x, y):
    global ball_speed, speed_step, max_speed, min_speed
    if key == GLUT_KEY_UP:
        if (ball_speed + speed_step) > max_speed:
            print("Max speed reached!!")
        else:
            ball_speed += speed_step
            print("Ball Speed increased")

    elif key == GLUT_KEY_DOWN:
        if (ball_speed - speed_step) < min_speed:
            print("Min speed reached!!")
        else:
            ball_speed -= speed_step
            print("Ball Speed decreased")
    glutPostRedisplay()

def keyboard_listener(key, x, y):
    global freezed
    if key == b' ': 
        freezed = not freezed
        if freezed:
            print("Display is Frozen")
        else:
            print("Display is Running")
    glutPostRedisplay()

def mouse_event_listener(button, state, x, y):
    global particles, blink

    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        blink = not blink
        if blink:
            print("Color Blinked")
        else:
            print("Color Unblinked")

    elif button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:

        new_info = {
            "direction": random.randint(0,3),
            "x": x,
            "y": convert_coordinate(y),
            "color": (random.random(), random.random(), random.random())
        }
        particles.append(new_info)

        print(f"New Ball spawned at ({x}, {convert_coordinate(y)})")

def draw_point(x,y, size=5):
    glPointSize(size)
    glBegin(GL_POINTS)
    glVertex2f(x, y)
    glEnd()

def animate_balls():
    global particles, ball_speed, freezed, window_width, window_height

    if not freezed:
        for ball_info in particles:
            x1, y1 = ball_info["x"], ball_info["y"]
            direction = ball_info["direction"]

            if direction == 0:      #45 degree
                x1 += ball_speed
                y1 += ball_speed

            elif direction == 1:    #135 degree
                x1 -= ball_speed
                y1 += ball_speed
            
            elif direction == 2:    #225 degree
                x1 -= ball_speed
                y1 -= ball_speed

            elif direction == 3:    #315 degree
                x1 += ball_speed
                y1 -= ball_speed

            # bounce effect
            if direction == 0:
                if x1 >= window_width:
                    direction = 1
                elif y1 >= window_height:
                    direction = 3

            elif direction == 1:
                if x1 <= 0:
                    direction = 0
                elif y1 >= window_height:
                    direction = 2

            elif direction == 2:
                if x1 <= 0:
                    direction = 3
                elif y1 <= 0:
                    direction = 1
            
            elif direction == 3:
                if x1 >= window_width:
                    direction = 2
                elif y1 <= 0:
                    direction = 0
             
                

            ball_info["x"], ball_info["y"] = x1, y1
            ball_info["direction"] = direction

    glutPostRedisplay()

def setup_projection():
    glViewport(0, 0, window_width, window_height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity() 

    # Xmin, Xmax, Ymin, Ymax
    glOrtho(0.0, window_width, 0.0, window_height, 0.0, 1.0)
    glMatrixMode(GL_MODELVIEW)  

def display():
    global particles, blink
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    setup_projection()

    # display balls

    for ball_info in particles:
        x1, y1 = ball_info["x"], ball_info["y"]
        R, G, B = ball_info["color"]

        if blink:
            glColor3f(0.0, 0.0, 0.0)
        else:
            glColor3f(R, G, B)
        draw_point(x1,y1, 5)

    glutSwapBuffers() 

def main():
    glutInit()                      
    glutInitDisplayMode(GLUT_RGBA)  

    screen_width, screen_height = glutGet(GLUT_SCREEN_WIDTH), glutGet(GLUT_SCREEN_HEIGHT)

    glutInitWindowSize(window_width, window_height)

    # window position (centered)
    starting_x, starting_y = (screen_width - window_width)//2, (screen_height-window_height)//2
    glutInitWindowPosition(starting_x, starting_y)

    glutCreateWindow(b"Ping pong")
    glutDisplayFunc(display)
    
    # animation
    glutIdleFunc(animate_balls)

    # event listener
    glutMouseFunc(mouse_event_listener)
    glutSpecialFunc(special_key_listener)
    glutKeyboardFunc(keyboard_listener)

    glutMainLoop()

if __name__ == "__main__":
    main()