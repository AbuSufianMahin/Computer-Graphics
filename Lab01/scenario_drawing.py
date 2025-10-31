from OpenGL.GL import *     
from OpenGL.GLUT import *   
from OpenGL.GLU import *

window_width, window_height = 1000, 600

# sky color
sky_RGB = 1.0

def keyboard_listener(key,x,y):
    global sky_RGB

    if key == b'w':
        sky_RGB += 0.1
        if sky_RGB > 1.0:
            sky_RGB = 0.0

    elif key == b's':
        sky_RGB -= 0.1
        if sky_RGB < 0.0:
            sky_RGB = 1.0

    glutPostRedisplay()

def draw_point(size, x, y):
    glPointSize(size)      
    glBegin(GL_POINTS)      
    glVertex2f(x,y)
    glEnd()

def draw_line(width, p1,p2, p3,p4):
    glLineWidth(width)
    glBegin(GL_LINES)

    glColor3f(0.0, 0.0, 0.0)
    glVertex2f(p1, p2)
    glVertex2f(p3, p4)

    glEnd()

def draw_triangle(p1, p2, p3, p4, p5, p6):
    glBegin(GL_TRIANGLES)
    glVertex2f(p1, p2)
    glVertex2f(p3, p4)
    glVertex2f(p5, p6)
    glEnd()

def draw_rectangle(p1, p2, p3, p4, p5, p6, p7, p8):
    glBegin(GL_QUADS)
    glVertex2f(p1, p2)
    glVertex2f(p3, p4)
    glVertex2f(p5, p6)
    glVertex2f(p7, p8)
    glEnd()

def draw_background_trees():
    # background Triangles (trees? may be?)
    tree_left_x, tree_left_y = 0,(0+320)
    tree_right_x, tree_right_y = 50,(0+320)
    tree_top_x, tree_top_y = 25,(60+320)

    while tree_left_x <= window_width and tree_right_x <= window_width:
        glColor3f(0.5, 0.8, 0)
        draw_triangle(tree_left_x,tree_left_y, 
                       tree_right_x,tree_right_y, 
                       tree_top_x,tree_top_y)

        tree_left_x += 50
        tree_right_x += 50
        tree_top_x += 50

def draw_house():
    # roof 
    glColor3f(0.6, 0.0, 1.0)
    draw_triangle(250,360, 750,360, 500,480)

    # house body
    glColor3f(1.0, 0.9, 0.9)
    draw_rectangle(300,180, 700,180, 700,360, 300,360)

    # door
    glColor3f(0.0, 0.8, 1.0)
    draw_rectangle(460,180, 540,180, 540,300, 460,300)
    
    # door knob
    glColor3f(0.0, 0.0, 0.0)  
    draw_point(8, 525,240)
    

    # window color
    glColor3f(0.0, 0.8, 1.0)
    # left window
    draw_rectangle(360,240, 430,240, 430,300, 360,300)
    draw_line(3, 395,240, 395,300)
    draw_line(3, 360,270, 430,270)

    # right window
    glColor3f(0.0, 0.8, 1.0)
    draw_rectangle(570,240, 640,240, 640,300, 570,300)
    draw_line(3, 605,240, 605,300)
    draw_line(3, 570,270, 640,270)


def draw_scenario():
    # drawing sky 
    glColor3f(sky_RGB, sky_RGB, sky_RGB) 
    draw_rectangle(0,420, 1000,420, 1000,600, 0,600)

    # drawing ground
    glColor3f(0.6, 0.4, 0.1) #trial and error for brown color
    draw_rectangle(0,0, 1000,0, 1000,420, 0,420)

    # drawing trees
    draw_background_trees()

    # drawing house
    glColor3f(0.1, 0.0, 0.0)
    draw_house()


def setup_projection():
    glViewport(0, 0, window_width, window_height)                   # Define the portion of the window to render to
    glMatrixMode(GL_PROJECTION)                                     # Switch to the projection matrix
    glLoadIdentity()                                                # Reset the projection matrix
    glOrtho(0.0, window_width, 0.0, window_height, 0.0, 1.0)        # Define a 2D orthographic projection
    glMatrixMode(GL_MODELVIEW)  

def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    setup_projection()

    # scenario initialization
    draw_scenario()
    
    glutSwapBuffers() 


def main():
    glutInit()                      
    glutInitDisplayMode(GLUT_RGBA)  

    screen_width, screen_height = glutGet(GLUT_SCREEN_WIDTH), glutGet(GLUT_SCREEN_HEIGHT)

    glutInitWindowSize(window_width, window_height)

    # window position (centered)
    starting_x, starting_y = (screen_width - window_width)//2, (screen_height-window_height)//2

    glutInitWindowPosition(starting_x, starting_y)
    glutCreateWindow(b"Rainy Weather")
    glutDisplayFunc(display)

    # event listener
    glutKeyboardFunc(keyboard_listener)

    glutMainLoop()

if __name__ == "__main__":
    main()