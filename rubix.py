import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import math

# Define colors (R, G, B)
WHITE = (1, 1, 1)
YELLOW = (1, 1, 0)
RED = (1, 0, 0)
ORANGE = (1, 0.5, 0)
BLUE = (0, 0, 1)
GREEN = (0, 1, 0)
BLACK = (0, 0, 0)

# Each cubie is a small cube with colored faces
class Cubie:
    def __init__(self, x, y, z, size=0.98):
        self.x = x
        self.y = y
        self.z = z
        self.size = size
        self.colors = [WHITE, YELLOW, RED, ORANGE, BLUE, GREEN]  # default

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
            (0, 1, 2, 3),  # back
            (4, 5, 6, 7),  # front
            (0, 4, 7, 3),  # left
            (1, 5, 6, 2),  # right
            (3, 2, 6, 7),  # top
            (0, 1, 5, 4)   # bottom
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


# Build 3×3×3 Rubik's cube of Cubies
def create_rubiks_cube():
    cubies = []
    positions = [-1.05, 0, 1.05]  # space between cubies
    for x in positions:
        for y in positions:
            for z in positions:
                cubies.append(Cubie(x, y, z))
    return cubies


def main():
    pygame.init()
    display = (800, 600)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    glEnable(GL_DEPTH_TEST)

    gluPerspective(45, display[0] / display[1], 0.1, 50.0)
    glTranslatef(0.0, 0.0, -10)
    glRotatef(25, 2, 1, 0)

    rubiks_cube = create_rubiks_cube()

    clock = pygame.time.Clock()
    rotation_x = 0
    rotation_y = 0

    running = True
    while running:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Keyboard input
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            rotation_y -= 1
        if keys[pygame.K_RIGHT]:
            rotation_y += 1
        if keys[pygame.K_UP]:
            rotation_x -= 1
        if keys[pygame.K_DOWN]:
            rotation_x += 1

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glPushMatrix()
        glRotatef(rotation_x, 1, 0, 0)
        glRotatef(rotation_y, 0, 1, 0)

        for cubie in rubiks_cube:
            cubie.draw()

        glPopMatrix()
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
