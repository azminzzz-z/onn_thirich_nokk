import pygame
import random
import sys

# --- Configuration ---
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
BLOCK_SIZE = 20
FPS = 8 # The snake now moves slower (was 10)

# --- Colors ---
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# --- Initialize Pygame ---
pygame.init()

# --- Load Images and Handle Errors ---
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
try:
    # Use convert_alpha() for transparency
    snake_image = pygame.image.load("snake.png").convert_alpha()
    food_image = pygame.image.load("food.png").convert_alpha()

    # Scale the images to fit the block size
    snake_image = pygame.transform.scale(snake_image, (BLOCK_SIZE, BLOCK_SIZE))
    food_image = pygame.transform.scale(food_image, (BLOCK_SIZE, BLOCK_SIZE))
except pygame.error as e:
    print(f"Error: Could not load image files. {e}")
    print("Please make sure 'snake.png' and 'food.png' are in the same folder as the script.")
    pygame.quit()
    sys.exit()
# --- Snake and Food Classes ---
class Snake:
    """The AI-controlled snake that chases the food."""
    def __init__(self):
        self.x = SCREEN_WIDTH // 2
        self.y = SCREEN_HEIGHT // 2
        self.dx = 0
        self.dy = 0
        self.body = [(self.x, self.y)]
        self.length = 1

    def move(self, food_x, food_y):
        """AI logic to move the snake towards the food."""
        if self.x < food_x:
            self.dx, self.dy = BLOCK_SIZE, 0
        elif self.x > food_x:
            self.dx, self.dy = -BLOCK_SIZE, 0
        elif self.y < food_y:
            self.dx, self.dy = 0, BLOCK_SIZE
        elif self.y > food_y:
            self.dx, self.dy = 0, -BLOCK_SIZE

        self.x += self.dx
        self.y += self.dy
        self.body.insert(0, (self.x, self.y))

        if len(self.body) > self.length:
            self.body.pop()

    def draw(self, surface):
        """Draws the snake using the loaded image for each segment."""
        for segment in self.body:
            surface.blit(snake_image, segment)

    def grow(self):
        self.length += 1

    def check_collision(self):
        """Check if the snake hits a wall or itself."""
        head = (self.x, self.y)
        # Check wall collision
        if head[0] < 0 or head[0] >= SCREEN_WIDTH or head[1] < 0 or head[1] >= SCREEN_HEIGHT:
            return True
        # Check self-collision
        if head in self.body[1:]:
            return True
        return False

class Food:
    """The player-controlled food block."""
    def __init__(self):
        self.x = random.randrange(0, SCREEN_WIDTH, BLOCK_SIZE)
        self.y = random.randrange(0, SCREEN_HEIGHT, BLOCK_SIZE)

    def move(self, dx, dy):
        """Move the food based on player input and keep it within bounds."""
        self.x += dx
        self.y += dy

        # Clamp position to stay within the screen
        self.x = max(0, min(self.x, SCREEN_WIDTH - BLOCK_SIZE))
        self.y = max(0, min(self.y, SCREEN_HEIGHT - BLOCK_SIZE))

    def draw(self, surface):
        """Draws the food using the loaded image."""
        surface.blit(food_image, (self.x, self.y))

# --- Main Game Loop ---
def main():

    pygame.display.set_caption("Inverse Snake - Control the Food!")
    clock = pygame.time.Clock()

    snake = Snake()
    food = Food()
    score = 0

    running = True
    while running:
        # --- Event Loop (for quitting the game) ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        # --- Continuous Input Handling for Food ---
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            food.move(-BLOCK_SIZE, 0)
        if keys[pygame.K_RIGHT]:
            food.move(BLOCK_SIZE, 0)
        if keys[pygame.K_UP]:
            food.move(0, -BLOCK_SIZE)
        if keys[pygame.K_DOWN]:
            food.move(0, BLOCK_SIZE)

        # --- Game Logic ---
        snake.move(food.x, food.y)

        # Check if snake "eats" the food
        if (snake.x, snake.y) == (food.x, food.y):
            snake.grow()
            score += 10

        # Check for game over
        if snake.check_collision():
            running = False

        # --- Drawing ---
        screen.fill(BLACK)
        snake.draw(screen)
        food.draw(screen)

        # Display score
        font = pygame.font.SysFont(None, 36)
        text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(text, (10, 10))

        # Update the display
        pygame.display.update()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()