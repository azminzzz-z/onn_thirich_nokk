import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import time
import tkinter as tk
import threading

# Define face colors (R, G, B)
WHITE = (1, 1, 1)
YELLOW = (1, 1, 0)
RED = (1, 0, 0)
ORANGE = (1, 0.5, 0)
BLUE = (0, 0, 1)
GREEN = (0, 1, 0)
BLACK = (0, 0, 0)

# Define the color swap mapping
COLOR_SWAP_MAP = {
    WHITE: YELLOW,
    YELLOW: WHITE,
    RED: ORANGE,
    ORANGE: RED,
    BLUE: GREEN,
    GREEN: BLUE
}

class Cubie:
    def __init__(self, x, y, z, size=0.9):
        self.x = x
        self.y = y
        self.z = z
        self.size = size
        self.colors = [WHITE, YELLOW, RED, ORANGE, BLUE, GREEN]

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

    def swap_colors(self):
        # Create a new list with swapped colors
        self.colors = [COLOR_SWAP_MAP.get(color, color) for color in self.colors]


def create_rubiks_cube():
    cubies = []
    spacing = 1.05
    for x in [-spacing, 0, spacing]:
        for y in [-spacing, 0, spacing]:
            for z in [-spacing, 0, spacing]:
                cubies.append(Cubie(x, y, z))
    return cubies

# Global state variables for the game
global_state = {
    "rubiks_cube": create_rubiks_cube(),
    "rotation_x": 25,
    "rotation_y": 30,
    "start_time": time.time(),
    "last_swap_time": time.time(),
    "running": True
}

def main():
    pygame.init()
    display = (800, 600)
    try:
        pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    except Exception as e:
        print(f"Failed to initialize OpenGL display: {e}")
        return

    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LESS)
    glClearColor(0.1, 0.1, 0.1, 1.0)
    gluPerspective(45, display[0] / display[1], 0.1, 100.0)
    glTranslatef(0.0, 0.0, -10)
    glRotatef(global_state["rotation_x"], 1, 0, 0)
    glRotatef(global_state["rotation_y"], 0, 1, 0)

    clock = pygame.time.Clock()
    while global_state["running"]:
        clock.tick(60)

        # Check for color swap
        current_time = time.time()
        if current_time - global_state["last_swap_time"] >= 10:
            for cubie in global_state["rubiks_cube"]:
                cubie.swap_colors()
            global_state["last_swap_time"] = current_time

        for event in pygame.event.get():
            if event.type == QUIT:
                global_state["running"] = False
                pygame.quit()
                return

        keys = pygame.key.get_pressed()
        if keys[K_LEFT]:
            global_state["rotation_y"] -= 1
        if keys[K_RIGHT]:
            global_state["rotation_y"] += 1
        if keys[K_UP]:
            global_state["rotation_x"] -= 1
        if keys[K_DOWN]:
            global_state["rotation_x"] += 1

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glPushMatrix()
        glRotatef(global_state["rotation_x"], 1, 0, 0)
        glRotatef(global_state["rotation_y"], 0, 1, 0)
        for cubie in global_state["rubiks_cube"]:
            cubie.draw()
        glPopMatrix()
        pygame.display.flip()

def reset_game():
    global_state["rubiks_cube"] = create_rubiks_cube()
    global_state["start_time"] = time.time()
    global_state["last_swap_time"] = time.time()

def solve_game():
    # This is a placeholder for a solve function
    # A real implementation would require a solve algorithm
    print("Solve function called!")

def create_ui_window():
    root = tk.Tk()
    root.title("Dynamic Cube UI")
    root.geometry("300x200")
    root.configure(bg="#222222")

    title_label = tk.Label(root, text="Dynamic Cube", font=("Helvetica", 16, "bold"), fg="white", bg="#222222")
    title_label.pack(pady=10)

    game_time_label = tk.Label(root, text="Time: 00:00", font=("Helvetica", 12), fg="white", bg="#222222")
    game_time_label.pack(pady=5)

    swap_time_label = tk.Label(root, text="Next Swap: 00:10", font=("Helvetica", 12), fg="white", bg="#222222")
    swap_time_label.pack(pady=5)

    def update_labels():
        if global_state["running"]:
            elapsed_time = int(time.time() - global_state["start_time"])
            time_str = f"Time: {elapsed_time // 60:02d}:{elapsed_time % 60:02d}"
            game_time_label.config(text=time_str)

            time_to_swap = 10 - int(time.time() - global_state["last_swap_time"])
            swap_str = f"Next Swap: {time_to_swap:02d}"
            swap_time_label.config(text=swap_str)
            root.after(1000, update_labels)

    update_labels()

    control_frame = tk.Frame(root, bg="#222222")
    control_frame.pack(pady=10)

    reset_button = tk.Button(control_frame, text="Reset", command=reset_game, width=10, bg="#444444", fg="white")
    reset_button.pack(side=tk.LEFT, padx=5)

    solve_button = tk.Button(control_frame, text="Solve", command=solve_game, width=10, bg="#444444", fg="white")
    solve_button.pack(side=tk.RIGHT, padx=5)

    root.mainloop()

if __name__ == "__main__":
    game_thread = threading.Thread(target=main)
    game_thread.start()
    create_ui_window()