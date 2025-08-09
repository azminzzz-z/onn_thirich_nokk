import pygame
import random

# --- Configuration ---
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
BLOCK_SIZE = 20
FPS = 10

# Define colors
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)

# --- Snake and Food Classes ---
class Snake:
    def __init__(self):
        # Initialize head position at center
        self.x = SCREEN_WIDTH // 2
        self.y = SCREEN_HEIGHT // 2
        self.dx = BLOCK_SIZE  # start moving right
        self.dy = 0
        self.body = [(self.x, self.y)]
        self.length = 1

    def move(self):
        self.x += self.dx
        self.y += self.dy
        self.body.insert(0, (self.x, self.y))
        if len(self.body) > self.length:
            self.body.pop()

    def draw(self, surface):
        for segment in self.body:
            pygame.draw.rect(surface, GREEN, (*segment, BLOCK_SIZE, BLOCK_SIZE))

    def grow(self):
        self.length += 1

    def check_collision(self):
        head = (self.x, self.y)
        # Hitting walls
        if head[0] < 0 or head[0] >= SCREEN_WIDTH or head[1] < 0 or head[1] >= SCREEN_HEIGHT:
            return True
        # Hitting itself
        if head in self.body[1:]:
            return True
        return False

class Food:
    def __init__(self):
        self.x = random.randrange(0, SCREEN_WIDTH, BLOCK_SIZE)
        self.y = random.randrange(0, SCREEN_HEIGHT, BLOCK_SIZE)

    def draw(self, surface):
        pygame.draw.rect(surface, RED, (self.x, self.y, BLOCK_SIZE, BLOCK_SIZE))

    def respawn(self, snake_body):
        while True:
            self.x = random.randrange(0, SCREEN_WIDTH, BLOCK_SIZE)
            self.y = random.randrange(0, SCREEN_HEIGHT, BLOCK_SIZE)
            if (self.x, self.y) not in snake_body:
                break

# --- Main Game Loop ---
def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Snake Game")
    clock = pygame.time.Clock()

    snake = Snake()
    food = Food()
    score = 0

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                # Prevent reverse direction
                if event.key == pygame.K_UP and snake.dy == 0:
                    snake.dx, snake.dy = 0, -BLOCK_SIZE
                elif event.key == pygame.K_DOWN and snake.dy == 0:
                    snake.dx, snake.dy = 0, BLOCK_SIZE
                elif event.key == pygame.K_LEFT and snake.dx == 0:
                    snake.dx, snake.dy = -BLOCK_SIZE, 0
                elif event.key == pygame.K_RIGHT and snake.dx == 0:
                    snake.dx, snake.dy = BLOCK_SIZE, 0

        snake.move()

        # Check if food eaten
        if (snake.x, snake.y) == (food.x, food.y):
            snake.grow()
            score += 10
            food.respawn(snake.body)

        # Check for collisions
        if snake.check_collision():
            running = False

        # Drawing
        screen.fill(BLACK)
        snake.draw(screen)
        food.draw(screen)

        # Display score
        font = pygame.font.SysFont(None, 36)
        text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(text, (10, 10))

        pygame.display.update()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
