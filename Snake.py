import json
import pygame
import random
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SAVE_FILE = "save.json"

def load_save():
    try:
        with open(SAVE_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"high_score": 0}

pygame.init()
pygame.mixer.init()

# ---------------- MUSIC ----------------
pygame.mixer.music.load(os.path.join(BASE_DIR, "assets/music/background.mp3"))
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)
death_sound = pygame.mixer.Sound(os.path.join(BASE_DIR, "assets/sounds/death.wav"))

# ---------------- SCREEN ----------------
WIDTH, HEIGHT = 600, 420
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake")

# ---------------- COLORS ----------------
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
GRAY = (80, 80, 80)
YELLOW = (255, 255, 0)

# ---------------- GAME ----------------
snake_size = 20
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 35)

paused = False

# ---------------- SETTINGS ----------------
sound_enabled = True

speed_modes = {
    "SLOW": 5,
    "NORMAL": 7,
    "FAST": 9,
    "EXTREME": 12
}
selected_speed = "NORMAL"

# ---------------- HELP ----------------
def is_key(event, key):
    return event.type == pygame.KEYDOWN and event.key == key

# ---------------- GRID ----------------
def draw_grid():
    for x in range(0, WIDTH, snake_size):
        pygame.draw.line(screen, (30, 30, 30), (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, snake_size):
        pygame.draw.line(screen, (30, 30, 30), (0, y), (WIDTH, y))

# ---------------- BUTTON ----------------
class Button:
    def __init__(self, x, y, w, h, text):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text

    def draw(self):
        mouse = pygame.mouse.get_pos()
        color = GRAY if self.rect.collidepoint(mouse) else WHITE
        pygame.draw.rect(screen, color, self.rect, border_radius=10)
        label = font.render(str(self.text), True, BLACK)
        screen.blit(label, (self.rect.x + 15, self.rect.y + 10))

    def clicked(self, event):
        return (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and self.rect.collidepoint(event.pos)
        )

# ---------------- SAVE ----------------
def save_game(high_score, score, snake, direction, food_x, food_y):
    with open("save.json", "w") as f:
        json.dump({
            "high_score": high_score,
            "sound": sound_enabled,
            "speed": selected_speed,
            "score": score,
            "snake": snake,
            "direction": direction,
            "food_x": food_x,
            "food_y": food_y
        }, f)

# ---------------- GAME STATE ----------------
def new_game():
    snake = [[100, 100]]

    while True:
        fx = random.randrange(0, WIDTH, snake_size)
        fy = random.randrange(0, HEIGHT, snake_size)
        if [fx, fy] not in snake:
            break

    return {
        "high_score": high_score,
        "sound": True,
        "speed": "NORMAL",
        "score": 0,
        "snake": [[100, 100]],
        "direction": "RIGHT",
        "food_x": fx,
        "food_y": fy
    }

# ---------------- CONTROLS ----------------
def controls_screen():
    back = Button(190, 300, 220, 45, "BACK (ESC)")

    while True:
        screen.fill(BLACK)
        screen.blit(font.render("CONTROLS", True, GREEN), (220, 50))
        screen.blit(font.render("Arrows = Move", True, WHITE), (200, 120))
        screen.blit(font.render("P = Pause", True, WHITE), (200, 160))
        screen.blit(font.render("F = Turbo", True, WHITE), (200, 200))

        back.draw()
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_game(high_score, score, snake, direction, food_x, food_y)
                pygame.quit()
                exit()

            if back.clicked(event) or is_key(event, pygame.K_ESCAPE):
                return

# ---------------- SETTINGS ----------------
def settings_menu():
    global sound_enabled, selected_speed

    sound_btn = Button(140, 120, 320, 45, "")
    speed_btn = Button(140, 180, 320, 45, "")
    back_btn = Button(140, 260, 320, 45, "BACK")

    speed_keys = list(speed_modes.keys())

    while True:
        screen.fill(BLACK)
        screen.blit(font.render("SETTINGS", True, GREEN), (220, 50))

        sound_btn.text = f"SOUND: {'ON' if sound_enabled else 'OFF'}"
        speed_btn.text = f"SPEED: {selected_speed}"

        sound_btn.draw()
        speed_btn.draw()
        back_btn.draw()

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_game(high_score, score, snake, direction, food_x, food_y)
                pygame.quit()
                exit()

            if sound_btn.clicked(event):
                sound_enabled = not sound_enabled
                pygame.mixer.music.set_volume(0.5 if sound_enabled else 0)

            if speed_btn.clicked(event):
                i = speed_keys.index(selected_speed)
                selected_speed = speed_keys[(i + 1) % len(speed_keys)]

            if back_btn.clicked(event) or is_key(event, pygame.K_ESCAPE):
                return

# ---------------- GAME OVER ----------------
def game_over_screen(score):
    restart = Button(170, 180, 260, 45, "RESTART")
    menu = Button(170, 240, 260, 45, "MENU")

    while True:
        screen.fill(BLACK)
        screen.blit(font.render("GAME OVER", True, RED), (200, 100))
        screen.blit(font.render(f"Score: {score}", True, WHITE), (230, 140))

        restart.draw()
        menu.draw()
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_game(high_score, score, snake, direction, food_x, food_y)
                pygame.quit()
                exit()
            if restart.clicked(event):
                return "restart"
            if menu.clicked(event):
                return "menu"

# ---------------- MAIN MENU ----------------
def main_menu():
    new_btn = Button(150, 120, 300, 45, "NEW GAME")
    cont_btn = Button(150, 180, 300, 45, "CONTINUE")
    ctrl_btn = Button(150, 240, 300, 45, "CONTROLS")
    set_btn = Button(150, 300, 300, 45, "SETTINGS")
    quit_btn = Button(150, 360, 300, 45, "QUIT")

    while True:
        screen.fill(BLACK)

        screen.blit(font.render("SNAKE", True, GREEN), (260, 50))
        screen.blit(font.render(f"HIGH SCORE: {high_score}", True, YELLOW), (160, 90))

        new_btn.draw()
        cont_btn.draw()
        ctrl_btn.draw()
        set_btn.draw()
        quit_btn.draw()

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_game(high_score, score, snake, direction, food_x, food_y)
                pygame.quit()
                exit()

            if new_btn.clicked(event):
                return "new"

            if cont_btn.clicked(event):
                return "continue"

            if ctrl_btn.clicked(event):
                controls_screen()

            if set_btn.clicked(event):
                settings_menu()

            if quit_btn.clicked(event):
                save_game(high_score, score, snake, direction, food_x, food_y)
                pygame.quit()
                exit()

# ---------------- INIT ----------------
saved = load_save()
high_score = saved["high_score"]

sound_enabled = saved.get("sound", True)
selected_speed = saved.get("speed", "NORMAL")

pygame.mixer.music.set_volume(0.5 if sound_enabled else 0)

choice = main_menu()

if choice == "continue":
    state = {
        "score": saved.get("score", 0),
        "snake": saved.get("snake", [[100, 100]]),
        "direction": saved.get("direction", "RIGHT"),
        "food_x": saved.get("food_x", 200),
        "food_y": saved.get("food_y", 200),
    }
else:
    state = new_game()

score = state["score"]
snake = state["snake"]
direction = state["direction"]
food_x = state["food_x"]
food_y = state["food_y"]

# ---------------- GAME LOOP ----------------
running = True

while running:

    keys = pygame.key.get_pressed()
    speed = speed_modes[selected_speed]

    if keys[pygame.K_f]:
        speed += 3

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            save_game(high_score, score, snake, direction, food_x, food_y)
            pygame.quit()
            exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                paused = not paused

            if not paused:
                if event.key == pygame.K_LEFT and direction != "RIGHT":
                    direction = "LEFT"
                elif event.key == pygame.K_RIGHT and direction != "LEFT":
                    direction = "RIGHT"
                elif event.key == pygame.K_UP and direction != "DOWN":
                    direction = "UP"
                elif event.key == pygame.K_DOWN and direction != "UP":
                    direction = "DOWN"

    if paused:
        screen.fill(BLACK)
        screen.blit(font.render("PAUSED", True, WHITE), (260, 150))
        pygame.display.update()
        clock.tick(10)
        continue

    # ---------------- MOVE ----------------
    x, y = snake[0]

    if direction == "LEFT":
        x -= snake_size
    elif direction == "RIGHT":
        x += snake_size
    elif direction == "UP":
        y -= snake_size
    elif direction == "DOWN":
        y += snake_size

    new_head = [x, y]

    snake.insert(0, new_head)

    # ---------------- COLLISION ----------------
    if x < 0 or x >= WIDTH or y < 0 or y >= HEIGHT or new_head in snake[1:]:
        if sound_enabled:
            death_sound.play()

        result = game_over_screen(score)

        if result == "restart":
            state = new_game()

        elif result == "menu":
            choice = main_menu()

            if choice == "continue":
                saved = load_save()
                state = {
                    "score": saved.get("score", 0),
                    "snake": saved.get("snake", [[100, 100]]),
                    "direction": saved.get("direction", "RIGHT"),
                    "food_x": saved.get("food_x", 200),
                    "food_y": saved.get("food_y", 200),
                }
            else:
                state = new_game()

        score = state["score"]
        snake = state["snake"]
        direction = state["direction"]
        food_x = state["food_x"]
        food_y = state["food_y"]

        continue

    # FOOD FIX
    if new_head == [food_x, food_y]:
        score += 1
        high_score = max(high_score, score)

        while True:
            food_x = random.randrange(0, WIDTH, snake_size)
            food_y = random.randrange(0, HEIGHT, snake_size)
            if [food_x, food_y] not in snake:
                break
    else:
        if len(snake) > 1:
            snake.pop()
    # DRAW
    screen.fill(BLACK)
    draw_grid()

    pygame.draw.rect(screen, RED, (food_x, food_y, snake_size, snake_size))

    for i, seg in enumerate(snake):
        pygame.draw.rect(screen, GREEN, (seg[0], seg[1], snake_size, snake_size))

        if i == 0:
            pygame.draw.circle(screen, WHITE, (seg[0] + 6, seg[1] + 6), 3)
            pygame.draw.circle(screen, WHITE, (seg[0] + 14, seg[1] + 6), 3)

    screen.blit(font.render(f"Score: {score}", True, WHITE), (10, 10))
    screen.blit(font.render(f"High Score: {high_score}", True, WHITE), (10, 40))

    pygame.display.update()
    clock.tick(speed)