import sys, math, random, time
import pygame, numpy as np

# ---------- SETTINGS ----------
SCREEN_W, SCREEN_H = 800, 600
PLAYER_SPEED = 4.0
SNAKE_SPEED = 2.0
SNAKE_LENGTH = 12
FPS = 60

pygame.init()
pygame.mixer.pre_init(44100, -16, 1, 512)
pygame.mixer.init()

screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("Reverse Snake ✨")
clock = pygame.time.Clock()
font = pygame.font.SysFont("consolas", 22)

# ---------- SOUND ----------
def make_tone(freq=440, duration_ms=200, volume=0.2, sample_rate=44100):
    t = np.linspace(0, duration_ms/1000.0, int(sample_rate * duration_ms/1000.0), False)
    wave = 32767 * np.sin(2 * np.pi * freq * t)
    audio = wave.astype(np.int16)
    snd = pygame.mixer.Sound(buffer=audio.tobytes())
    snd.set_volume(volume)
    return snd

SND_GAME_OVER = make_tone(130, 700, 0.25)
SND_BEEP = make_tone(660, 70, 0.12)

# ---------- GRADIENT BACKGROUND ----------
def draw_gradient_background(surf, time_shift):
    for y in range(SCREEN_H):
        r = int(150 + 105 * math.sin(time_shift + y/150))
        g = int(150 + 105 * math.sin(time_shift + y/200 + 2))
        b = int(150 + 105 * math.sin(time_shift + y/180 + 4))
        pygame.draw.line(surf, (r, g, b), (0, y), (SCREEN_W, y))

# ---------- GLOW DRAW ----------
def draw_glow_circle(surf, color, pos, radius, intensity=6):
    glow = pygame.Surface((radius*4, radius*4), pygame.SRCALPHA)
    for i in range(intensity, 0, -1):
        alpha = int(25 * i)
        pygame.draw.circle(glow, (*color, alpha),
                           (radius*2, radius*2), radius + i*3)
    surf.blit(glow, (pos[0]-radius*2, pos[1]-radius*2), special_flags=pygame.BLEND_RGBA_ADD)

# ---------- PLAYER ----------
class Player:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.radius = 12
        self.pulse_time = 0

    def move(self, dx, dy):
        self.x = max(self.radius, min(self.x + dx, SCREEN_W - self.radius))
        self.y = max(self.radius, min(self.y + dy, SCREEN_H - self.radius))

    def draw(self, surf, dt):
        self.pulse_time += dt
        pulse = 2 * math.sin(self.pulse_time * 4)
        grad_color1 = (255, 180, 255)
        grad_color2 = (180, 255, 255)
        draw_glow_circle(surf, grad_color1, (self.x, self.y), self.radius+int(pulse), intensity=8)
        pygame.draw.circle(surf, grad_color2, (int(self.x), int(self.y)), self.radius)

# ---------- SNAKE ----------
class AISnake:
    def __init__(self, x, y, length=SNAKE_LENGTH):
        self.segments = [[x - i*15, y] for i in range(length)]
        self.speed = SNAKE_SPEED
        self.dir_x, self.dir_y = 1.0, 0.0

    def update(self, tx, ty):
        head = self.segments[0]
        vec_x, vec_y = tx - head[0], ty - head[1]
        dist = math.hypot(vec_x, vec_y) + 1e-6
        self.dir_x += (vec_x/dist - self.dir_x) * 0.15
        self.dir_y += (vec_y/dist - self.dir_y) * 0.15
        dlen = math.hypot(self.dir_x, self.dir_y) + 1e-9
        self.dir_x /= dlen; self.dir_y /= dlen
        head[0] += self.dir_x * self.speed
        head[1] += self.dir_y * self.speed
        for i in range(1, len(self.segments)):
            prev, cur = self.segments[i-1], self.segments[i]
            dx, dy = prev[0]-cur[0], prev[1]-cur[1]
            d = math.hypot(dx, dy) + 1e-6
            if d > 15:
                cur[0] += (dx/d)*(d-15)
                cur[1] += (dy/d)*(d-15)

    def draw(self, surf):
        for i, seg in enumerate(self.segments):
            fade = 255 - i*15
            col = (180, 255, 200)
            draw_glow_circle(surf, col, (seg[0], seg[1]), 10, intensity=4)
            pygame.draw.circle(surf, col, (int(seg[0]), int(seg[1])), 8)

    def collides_with_point(self, px, py, radius=10):
        return any(math.hypot(seg[0]-px, seg[1]-py) < radius for seg in self.segments)

# ---------- MAIN ----------
def main():
    player = Player(SCREEN_W//2, SCREEN_H//2)
    snake = AISnake(100, 100)
    score, game_over, go_time = 0, False, None
    t_shift = 0
    while True:
        dt = clock.tick(FPS) / 1000
        for e in pygame.event.get():
            if e.type == pygame.QUIT: return
        keys = pygame.key.get_pressed()
        dx = (keys[pygame.K_RIGHT] or keys[pygame.K_d]) - (keys[pygame.K_LEFT] or keys[pygame.K_a])
        dy = (keys[pygame.K_DOWN] or keys[pygame.K_s]) - (keys[pygame.K_UP] or keys[pygame.K_w])
        if dx and dy: dx*=0.707; dy*=0.707

        if not game_over:
            player.move(dx*PLAYER_SPEED, dy*PLAYER_SPEED)
            snake.update(player.x, player.y)
            if snake.collides_with_point(player.x, player.y, radius=player.radius+2):
                SND_GAME_OVER.play(); game_over, go_time = True, time.time()
            score += dt*10

        # DRAW
        t_shift += dt
        draw_gradient_background(screen, t_shift)
        player.draw(screen, dt)
        snake.draw(screen)
        txt = font.render(f"Score: {int(score)}", True, (255,255,255))
        screen.blit(txt, (10, 10))

        if game_over:
            alpha = min(200, int((time.time()-go_time)*200))
            overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            overlay.fill((0,0,0,alpha))
            screen.blit(overlay, (0,0))
            big_font = pygame.font.SysFont("consolas", 48)
            text = big_font.render("GAME OVER", True, (255,180,200))
            screen.blit(text, (SCREEN_W//2 - text.get_width()//2, SCREEN_H//2 - 40))
            if time.time()-go_time > 3: return

        pygame.display.flip()

if __name__ == "__main__":
    main()