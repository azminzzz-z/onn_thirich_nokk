import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import time
import random

# Define colors for faces
WHITE = (1, 1, 1)    # Up
YELLOW = (1, 1, 0)   # Down
RED = (1, 0, 0)      # Front
ORANGE = (1, 0.5, 0) # Back
BLUE = (0, 0, 1)     # Left
GREEN = (0, 1, 0)    # Right
BLACK = (0, 0, 0)

face_indices = {'U':0, 'D':1, 'F':2, 'B':3, 'L':4, 'R':5}
positions = [-1.05, 0, 1.05]

colors_list = [WHITE, YELLOW, RED, ORANGE, BLUE, GREEN]

class Cubie:
    def __init__(self, x_idx, y_idx, z_idx):
        self.x_idx = x_idx
        self.y_idx = y_idx
        self.z_idx = z_idx
        self.size = 0.98
        self.colors = [BLACK]*6
        self.set_initial_colors()
        self.update_position()

    def set_initial_colors(self):
        self.colors = [BLACK]*6
        if self.y_idx == 2: self.colors[face_indices['U']] = WHITE
        if self.y_idx == 0: self.colors[face_indices['D']] = YELLOW
        if self.z_idx == 2: self.colors[face_indices['F']] = RED
        if self.z_idx == 0: self.colors[face_indices['B']] = ORANGE
        if self.x_idx == 0: self.colors[face_indices['L']] = BLUE
        if self.x_idx == 2: self.colors[face_indices['R']] = GREEN

    def update_position(self):
        self.x = positions[self.x_idx]
        self.y = positions[self.y_idx]
        self.z = positions[self.z_idx]

    def draw(self):
        s = self.size / 2
        vertices = [
            (self.x - s, self.y - s, self.z - s),
            (self.x + s, self.y - s, self.z - s),
            (self.x + s, self.y + s, self.z - s),
            (self.x - s, self.y + s, self.z - s),
            (self.x - s, self.y - s, self.z + s),
            (self.x + s, self.y - s, self.z + s),
            (self.x + s, self.y + s, self.z + s),
            (self.x - s, self.y + s, self.z + s),
        ]

        edges = [
            (0, 1), (1, 2), (2, 3), (3, 0),
            (4, 5), (5, 6), (6, 7), (7, 4),
            (0, 4), (1, 5), (2, 6), (3, 7)
        ]

        faces = [
            (3, 2, 6, 7),  # Up
            (0, 1, 5, 4),  # Down
            (4, 5, 6, 7),  # Front
            (0, 1, 2, 3),  # Back
            (0, 3, 7, 4),  # Left
            (1, 2, 6, 5),  # Right
        ]

        glBegin(GL_QUADS)
        for i, face in enumerate(faces):
            glColor3fv(self.colors[i])
            for vertex in face:
                glVertex3fv(vertices[vertex])
        glEnd()

        glColor3fv(BLACK)
        glBegin(GL_LINES)
        for edge in edges:
            for vertex in edge:
                glVertex3fv(vertices[vertex])
        glEnd()

class RubiksCube:
    def __init__(self):
        # 3D list of cubies indexed by x_idx, y_idx, z_idx (0 to 2)
        self.cube = [[[Cubie(x,y,z) for z in range(3)] for y in range(3)] for x in range(3)]
        self.animating = False
        self.animation_axis = None
        self.animation_layer = None
        self.animation_direction = 1
        self.animation_angle = 0
        self.animation_speed = 5
        self.animation_cubies = []

    def draw(self):
        for x in range(3):
            for y in range(3):
                for z in range(3):
                    cubie = self.cube[x][y][z]
                    if self.animating and cubie in self.animation_cubies:
                        glPushMatrix()
                        glTranslatef(cubie.x, cubie.y, cubie.z)
                        angle = self.animation_angle * self.animation_direction
                        if self.animation_axis == 'x':
                            glRotatef(angle, 1, 0, 0)
                        elif self.animation_axis == 'y':
                            glRotatef(angle, 0, 1, 0)
                        elif self.animation_axis == 'z':
                            glRotatef(angle, 0, 0, 1)
                        glTranslatef(-cubie.x, -cubie.y, -cubie.z)
                        cubie.draw()
                        glPopMatrix()
                    else:
                        cubie.draw()

    def start_rotation(self, axis, layer, clockwise=True):
        if self.animating:
            return
        self.animating = True
        self.animation_axis = axis
        self.animation_layer = layer
        self.animation_direction = 1 if clockwise else -1
        self.animation_angle = 0
        self.animation_cubies = []
        for x in range(3):
            for y in range(3):
                for z in range(3):
                    cubie = self.cube[x][y][z]
                    pos = {'x':x,'y':y,'z':z}[axis]
                    if pos == layer:
                        self.animation_cubies.append(cubie)

    def update_animation(self):
        if not self.animating:
            return
        self.animation_angle += self.animation_speed
        if self.animation_angle >= 90:
            self.animation_angle = 90
            self.animating = False
            self.finish_rotation()

    def finish_rotation(self):
        axis = self.animation_axis
        layer = self.animation_layer
        direction = self.animation_direction

        # Extract layer cubies into 2D matrix for rotation
        matrix = [[None]*3 for _ in range(3)]
        for x in range(3):
            for y in range(3):
                for z in range(3):
                    cubie = self.cube[x][y][z]
                    pos = {'x':x,'y':y,'z':z}[axis]
                    if pos == layer:
                        if axis == 'x':
                            matrix[y][2-z] = cubie
                        elif axis == 'y':
                            matrix[2-z][x] = cubie
                        else:
                            matrix[y][x] = cubie

        # Rotate the matrix clockwise or anticlockwise by 90 degrees
        if direction == 1:
            matrix = [list(reversed(col)) for col in zip(*matrix)]
        else:
            matrix = list(zip(*matrix[::-1]))
            matrix = [list(row) for row in matrix]

        # Update cubie indices and positions based on rotation
        for i in range(3):
            for j in range(3):
                cubie = matrix[i][j]
                if axis == 'x':
                    cubie.x_idx = layer
                    cubie.y_idx = i
                    cubie.z_idx = 2 - j
                elif axis == 'y':
                    cubie.x_idx = j
                    cubie.y_idx = layer
                    cubie.z_idx = 2 - i
                else:
                    cubie.x_idx = j
                    cubie.y_idx = i
                    cubie.z_idx = layer
                cubie.update_position()
                self.rotate_cubie_colors(cubie, axis, direction)

        # Rebuild cube structure with updated cubies
        new_cube = [[[None]*3 for _ in range(3)] for _ in range(3)]
        for x in range(3):
            for y in range(3):
                for z in range(3):
                    for ox in range(3):
                        for oy in range(3):
                            for oz in range(3):
                                cubie = self.cube[ox][oy][oz]
                                if (cubie.x_idx, cubie.y_idx, cubie.z_idx) == (x,y,z):
                                    new_cube[x][y][z] = cubie
        self.cube = new_cube

    def rotate_cubie_colors(self, cubie, axis, direction):
        c = cubie.colors[:]
        if axis == 'x':
            if direction == 1:
                cubie.colors[0] = c[3]
                cubie.colors[3] = c[1]
                cubie.colors[1] = c[2]
                cubie.colors[2] = c[0]
                cubie.colors[4] = c[4]
                cubie.colors[5] = c[5]
            else:
                cubie.colors[0] = c[2]
                cubie.colors[2] = c[1]
                cubie.colors[1] = c[3]
                cubie.colors[3] = c[0]
                cubie.colors[4] = c[4]
                cubie.colors[5] = c[5]
        elif axis == 'y':
            if direction == 1:
                cubie.colors[2] = c[4]
                cubie.colors[5] = c[2]
                cubie.colors[3] = c[5]
                cubie.colors[4] = c[3]
                cubie.colors[0] = c[0]
                cubie.colors[1] = c[1]
            else:
                cubie.colors[2] = c[5]
                cubie.colors[5] = c[3]
                cubie.colors[3] = c[4]
                cubie.colors[4] = c[2]
                cubie.colors[0] = c[0]
                cubie.colors[1] = c[1]
        elif axis == 'z':
            if direction == 1:
                cubie.colors[0] = c[4]
                cubie.colors[5] = c[0]
                cubie.colors[1] = c[5]
                cubie.colors[4] = c[1]
                cubie.colors[2] = c[2]
                cubie.colors[3] = c[3]
            else:
                cubie.colors[0] = c[5]
                cubie.colors[5] = c[1]
                cubie.colors[1] = c[4]
                cubie.colors[4] = c[0]
                cubie.colors[2] = c[2]
                cubie.colors[3] = c[3]

    def randomize_colors(self):
        # Randomly reassign face colors for all cubies (for color change effect)
        for x in range(3):
            for y in range(3):
                for z in range(3):
                    cubie = self.cube[x][y][z]
                    # Only assign colors to faces that have color (non-black) originally
                    new_colors = []
                    for c in cubie.colors:
                        if c == BLACK:
                            new_colors.append(BLACK)
                        else:
                            new_colors.append(random.choice(colors_list))
                    cubie.colors = new_colors

def main():
    pygame.init()
    display = (900, 700)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    glEnable(GL_DEPTH_TEST)

    gluPerspective(45, display[0]/display[1], 0.1, 50)
    glTranslatef(0, 0, -15)
    glRotatef(20, 2, 1, 0)

    cube = RubiksCube()

    clock = pygame.time.Clock()

    rotation_x = 0
    rotation_y = 0

    mouse_down = False
    last_pos = None

    last_color_change = time.time()

    print("Controls:")
    print("Mouse drag to rotate cube view")
    print("U/u: Up layer CW/CCW")
    print("M/m: Middle Y layer CW/CCW")
    print("D/d: Down layer CW/CCW")
    print("L/l: Left layer CW/CCW")
    print("E/e: Middle X layer CW/CCW")
    print("R/r: Right layer CW/CCW")
    print("F/f: Front layer CW/CCW")
    print("S/s: Middle Z layer CW/CCW")
    print("B/b: Back layer CW/CCW")

    running = True
    while running:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_down = True
                    last_pos = pygame.mouse.get_pos()

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    mouse_down = False

            elif event.type == pygame.MOUSEMOTION:
                if mouse_down:
                    x, y = pygame.mouse.get_pos()
                    dx = x - last_pos[0]
                    dy = y - last_pos[1]
                    rotation_y += dx * 0.5
                    rotation_x += dy * 0.5
                    last_pos = (x, y)

            elif event.type == pygame.KEYDOWN:
                if not cube.animating:
                    char = event.unicode
                    if char == 'u':
                        cube.start_rotation('y', 2, clockwise=False)
                    elif char == 'U':
                        cube.start_rotation('y', 2, clockwise=True)
                    elif char == 'm':
                        cube.start_rotation('y', 1, clockwise=False)
                    elif char == 'M':
                        cube.start_rotation('y', 1, clockwise=True)
                    elif char == 'd':
                        cube.start_rotation('y', 0, clockwise=False)
                    elif char == 'D':
                        cube.start_rotation('y', 0, clockwise=True)
                    elif char == 'l':
                        cube.start_rotation('x', 0, clockwise=False)
                    elif char == 'L':
                        cube.start_rotation('x', 0, clockwise=True)
                    elif char == 'e':
                        cube.start_rotation('x', 1, clockwise=False)
                    elif char == 'E':
                        cube.start_rotation('x', 1, clockwise=True)
                    elif char == 'r':
                        cube.start_rotation('x', 2, clockwise=False)
                    elif char == 'R':
                        cube.start_rotation('x', 2, clockwise=True)
                    elif char == 'f':
                        cube.start_rotation('z', 2, clockwise=False)
                    elif char == 'F':
                        cube.start_rotation('z', 2, clockwise=True)
                    elif char == 's':
                        cube.start_rotation('z', 1, clockwise=False)
                    elif char == 'S':
                        cube.start_rotation('z', 1, clockwise=True)
                    elif char == 'b':
                        cube.start_rotation('z', 0, clockwise=False)
                    elif char == 'B':
                        cube.start_rotation('z', 0, clockwise=True)

        # Change colors every 10 seconds
        if time.time() - last_color_change > 10:
            last_color_change = time.time()
            cube.randomize_colors()

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glPushMatrix()
        glRotateHere's the full updated code with:

- Proper Rubik's cube layer rotation (positions and colors updated),
- Every 10 seconds, all visible colored faces randomly change colors,
- Smooth animation of rotations,
- Mouse drag to rotate view,
- Key controls for all layers including middle layers.

```python
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import time
import random

# Colors
WHITE = (1, 1, 1)
YELLOW = (1, 1, 0)
RED = (1, 0, 0)
ORANGE = (1, 0.5, 0)
BLUE = (0, 0, 1)
GREEN = (0, 1, 0)
BLACK = (0, 0, 0)

face_indices = {'U':0, 'D':1, 'F':2, 'B':3, 'L':4, 'R':5}
positions = [-1.05, 0, 1.05]
colors_list = [WHITE, YELLOW, RED, ORANGE, BLUE, GREEN]

class Cubie:
    def __init__(self, x_idx, y_idx, z_idx):
        self.x_idx = x_idx
        self.y_idx = y_idx
        self.z_idx = z_idx
        self.size = 0.98
        self.colors = [BLACK]*6
        self.set_initial_colors()
        self.update_position()

    def set_initial_colors(self):
        self.colors = [BLACK]*6
        if self.y_idx == 2: self.colors[face_indices['U']] = WHITE
        if self.y_idx == 0: self.colors[face_indices['D']] = YELLOW
        if self.z_idx == 2: self.colors[face_indices['F']] = RED
        if self.z_idx == 0: self.colors[face_indices['B']] = ORANGE
        if self.x_idx == 0: self.colors[face_indices['L']] = BLUE
        if self.x_idx == 2: self.colors[face_indices['R']] = GREEN

    def update_position(self):
        self.x = positions[self.x_idx]
        self.y = positions[self.y_idx]
        self.z = positions[self.z_idx]

    def draw(self):
        s = self.size / 2
        vertices = [
            (self.x - s, self.y - s, self.z - s),
            (self.x + s, self.y - s, self.z - s),
            (self.x + s, self.y + s, self.z - s),
            (self.x - s, self.y + s, self.z - s),
            (self.x - s, self.y - s, self.z + s),
            (self.x + s, self.y - s, self.z + s),
            (self.x + s, self.y + s, self.z + s),
            (self.x - s, self.y + s, self.z + s),
        ]

        edges = [
            (0, 1), (1, 2), (2, 3), (3, 0),
            (4, 5), (5, 6), (6, 7), (7, 4),
            (0, 4), (1, 5), (2, 6), (3, 7)
        ]

        faces = [
            (3, 2, 6, 7),  # Up
            (0, 1, 5, 4),  # Down
            (4, 5, 6, 7),  # Front
            (0, 1, 2, 3),  # Back
            (0, 3, 7, 4),  # Left
            (1, 2, 6, 5),  # Right
        ]

        glBegin(GL_QUADS)
        for i, face in enumerate(faces):
            glColor3fv(self.colors[i])
            for vertex in face:
                glVertex3fv(vertices[vertex])
        glEnd()

        glColor3fv(BLACK)
        glBegin(GL_LINES)
        for edge in edges:
            for vertex in edge:
                glVertex3fv(vertices[vertex])
        glEnd()

class RubiksCube:
    def __init__(self):
        self.cube = [[[Cubie(x,y,z) for z in range(3)] for y in range(3)] for x in range(3)]
        self.animating = False
        self.animation_axis = None
        self.animation_layer = None
        self.animation_direction = 1
        self.animation_angle = 0
        self.animation_speed = 5
        self.animation_cubies = []

    def draw(self):
        for x in range(3):
            for y in range(3):
                for z in range(3):
                    cubie = self.cube[x][y][z]
                    if self.animating and cubie in self.animation_cubies:
                        glPushMatrix()
                        glTranslatef(cubie.x, cubie.y, cubie.z)
                        angle = self.animation_angle * self.animation_direction
                        if self.animation_axis == 'x':
                            glRotatef(angle, 1, 0, 0)
                        elif self.animation_axis == 'y':
                            glRotatef(angle, 0, 1, 0)
                        elif self.animation_axis == 'z':
                            glRotatef(angle, 0, 0, 1)
                        glTranslatef(-cubie.x, -cubie.y, -cubie.z)
                        cubie.draw()
                        glPopMatrix()
                    else:
                        cubie.draw()

    def start_rotation(self, axis, layer, clockwise=True):
        if self.animating:
            return
        self.animating = True
        self.animation_axis = axis
        self.animation_layer = layer
        self.animation_direction = 1 if clockwise else -1
        self.animation_angle = 0
        self.animation_cubies = []
        for x in range(3):
            for y in range(3):
                for z in range(3):
                    cubie = self.cube[x][y][z]
                    pos = {'x':x,'y':y,'z':z}[axis]
                    if pos == layer:
                        self.animation_cubies.append(cubie)

    def update_animation(self):
        if not self.animating:
            return
        self.animation_angle += self.animation_speed
        if self.animation_angle >= 90:
            self.animation_angle = 90
            self.animating = False
            self.finish_rotation()

    def finish_rotation(self):
        axis = self.animation_axis
        layer = self.animation_layer
        direction = self.animation_direction

        matrix = [[None]*3 for _ in range(3)]
        for x in range(3):
            for y in range(3):
                for z in range(3):
                    cubie = self.cube[x][y][z]
                    pos = {'x':x,'y':y,'z':z}[axis]
                    if pos == layer:
                        if axis == 'x':
                            matrix[y][2-z] = cubie
                        elif axis == 'y':
                            matrix[2-z][x] = cubie
                        else:
                            matrix[y][x] = cubie

        if direction == 1:
            matrix = [list(reversed(col)) for col in zip(*matrix)]
        else:
            matrix = list(zip(*matrix[::-1]))
            matrix = [list(row) for row in matrix]

        for i in range(3):
            for j in range(3):
                cubie = matrix[i][j]
                if axis == 'x':
                    cubie.x_idx = layer
                    cubie.y_idx = i
                    cubie.z_idx = 2 - j
                elif axis == 'y':
                    cubie.x_idx = j
                    cubie.y_idx = layer
                    cubie.z_idx = 2 - i
                else:
                    cubie.x_idx = j
                    cubie.y_idx = i
                    cubie.z_idx = layer
                cubie.update_position()
                self.rotate_cubie_colors(cubie, axis, direction)

        new_cube = [[[None]*3 for _ in range(3)] for _ in range(3)]
        for x in range(3):
            for y in range(3):
                for z in range(3):
                    for ox in range(3):
                        for oy in range(3):
                            for oz in range(3):
                                cubie = self.cube[ox][oy][oz]
                                if (cubie.x_idx, cubie.y_idx, cubie.z_idx) == (x,y,z):
                                    new_cube[x][y][z] = cubie
        self.cube = new_cube

    def rotate_cubie_colors(self, cubie, axis, direction):
        c = cubie.colors[:]
        if axis == 'x':
            if direction == 1:
                cubie.colors[0] = c[3]
                cubie.colors[3] = c[1]
                cubie.colors[1] = c[2]
                cubie.colors[2] = c[0]
                cubie.colors[4] = c[4]
                cubie.colors[5] = c[5]
            else:
                cubie.colors[0] = c[2]
                cubie.colors[2] = c[1]
                cubie.colors[1] = c[3]
                cubie.colors[3] = c[0]
                cubie.colors[4] = c[4]
                cubie.colors[5] = c[5]
        elif axis == 'y':
            if direction == 1:
                cubie.colors[2] = c[4]
                cubie.colors[5] = c[2]
                cubie.colors[3] = c[5]
                cubie.colors[4] = c[3]
                cubie.colors[0] = c[0]
                cubie.colors[1] = c[1]
            else:
                cubie.colors[2] = c[5]
                cubie.colors[5] = c[3]
                cubie.colors[3] = c[4]
                cubie.colors[4] = c[2]
                cubie.colors[0] = c[0]
                cubie.colors[1] = c[1]
        elif axis == 'z':
            if direction == 1:
                cubie.colors[0] = c[4]
                cubie.colors[5] = c[0]
                cubie.colors[1] = c[5]
                cubie.colors[4] = c[1]
                cubie.colors[2] = c[2]
                cubie.colors[3] = c[3]
            else:
                cubie.colors[0] = c[5]
                cubie.colors[5] = c[1]
                cubie.colors[1] = c[4]
                cubie.colors[4] = c[0]
                cubie.colors[2] = c[2]
                cubie.colors[3] = c[3]

    def randomize_colors(self):
        for x in range(3):
            for y in range(3):
                for z in range(3):
                    cubie = self.cube[x][y][z]
                    new_colors = []
                    for c in cubie.colors:
                        if c == BLACK:
                            new_colors.append(BLACK)
                        else:
                            new_colors.append(random.choice(colors_list))
                    cubie.colors = new_colors

def main():
    pygame.init()
    display = (900, 700)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    glEnable(GL_DEPTH_TEST)

    gluPerspective(45, display[0]/display[1], 0.1, 50)
    glTranslatef(0, 0, -15)
    glRotatef(20, 2, 1, 0)

    cube = RubiksCube()

    clock = pygame.time.Clock()

    rotation_x = 0
    rotation_y = 0

    mouse_down = False
    last_pos = None

    last_color_change = time.time()

    print("Controls:")
    print("Mouse drag to rotate cube view")
    print("U/u: Up layer CW/CCW")
    print("M/m: Middle Y layer CW/CCW")
    print("D/d: Down layer CW/CCW")
    print("L/l: Left layer CW/CCW")
    print("E/e: Middle X layer CW/CCW")
    print("R/r: Right layer CW/CCW")
    print("F/f: Front layer CW/CCW")
    print("S/s: Middle Z layer CW/CCW")
    print("B/b: Back layer CW/CCW")

    running = True
    while running:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_down = True
                    last_pos = pygame.mouse.get_pos()

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    mouse_down = False

            elif event.type == pygame.MOUSEMOTION:
                if mouse_down:
                    x, y = pygame.mouse.get_pos()
