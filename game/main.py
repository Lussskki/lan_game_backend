import pygame
import os
import sys
import requests
import socket


pygame.init()
pygame.font.init()
pygame.mixer.init()

WIDTH, HEIGHT = 900, 500
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('SpaceWar')

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

def notify_backend_connection():
    try:
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
        requests.post(f'{BACKEND_IP}/game-connected', json={'client_ip': ip_address})
        print("✅ Connected to backend server")
    except Exception as e:
        print("⚠️ Could not notify backend:", e)
# Base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Backend URL 
BACKEND_IP = 'http://192.168.100.7:5000'

# Icon
ICON_PATH = os.path.join(BASE_DIR, 'Assets', 'spaceship_red.ico')
if os.path.exists(ICON_PATH):
    ICON = pygame.image.load(ICON_PATH)
    pygame.display.set_icon(ICON)
else:
    print(f"Icon file not found: {ICON_PATH}")

# Border
BORDER = pygame.Rect(WIDTH // 2, 0, 10, HEIGHT)

# Sound loader
def load_sound(file_name):
    path = os.path.join(BASE_DIR, 'Assets', file_name)
    if os.path.exists(path):
        return pygame.mixer.Sound(path)
    print(f"Sound file not found: {path}")
    return None

BULLET_HIT_SOUND = load_sound('Grenade+1.mp3')
BULLET_FIRE_SOUND = load_sound('Gun+Silencer.mp3')

# Fonts
HEALTH_FONT = pygame.font.SysFont('comicsans', 40)
WINNER_FONT = pygame.font.SysFont('comicsans', 100)

SPACESHIP_WIDTH, SPACESHIP_HEIGHT = 50, 44

YELLOW_HIT = pygame.USEREVENT + 1
RED_HIT = pygame.USEREVENT + 2

VEL = 5
BULLET_VEL = 7
MAX_BULLETS = 10

# Load spaceship images
def load_spaceship_image(file_name, rotation_angle):
    path = os.path.join(BASE_DIR, 'Assets', file_name)
    if os.path.exists(path):
        spaceship = pygame.image.load(path)
        return pygame.transform.rotate(
            pygame.transform.scale(spaceship, (SPACESHIP_WIDTH, SPACESHIP_HEIGHT)),
            rotation_angle
        )
    print(f"Image file not found: {path}")
    return pygame.Surface((SPACESHIP_WIDTH, SPACESHIP_HEIGHT))

YELLOW_SPACESHIP = load_spaceship_image('spaceship_yellow.png', 90)
RED_SPACESHIP = load_spaceship_image('spaceship_red.png', 270)

SPACE = pygame.transform.scale(
    pygame.image.load(os.path.join(BASE_DIR, 'Assets', 'crab_nebula.jpg')),
    (WIDTH, HEIGHT)
)
# -------------------------------

# -------------------------------
# 🔹 Leaderboard functions
def update_score(playerName: str, score: int):
    try:
        resp = requests.post(f'{BACKEND_IP}/update-score', json={
            'playerName': playerName,
            'score': score
        })
        data = resp.json()
        return data.get("leaderboard", [])
    except Exception as e:
        print("Error sending score:", e)
        return []

def draw_leaderboard(lb):
    WIN.fill((0, 0, 0))
    title_font = pygame.font.SysFont('comicsans', 50)
    entry_font = pygame.font.SysFont('comicsans', 30)

    title = title_font.render("Leaderboard", True, (255, 255, 255))
    WIN.blit(title, (WIDTH // 2 - title.get_width() // 2, 50))

    for i, entry in enumerate(lb):
        text = entry_font.render(f"{i+1}. {entry['playerName']} - {entry['score']}", True, (255, 255, 0))
        WIN.blit(text, (WIDTH // 2 - text.get_width() // 2, 150 + i * 40))

    pygame.display.update()
    pygame.time.delay(5000)
# -------------------------------

# Draw window
def draw_window(red, yellow, red_bullets, yellow_bullets, red_health, yellow_health):
    WIN.blit(SPACE, (0, 0))
    pygame.draw.rect(WIN, BLACK, BORDER)

    red_health_text = HEALTH_FONT.render(f'Health: {red_health}', 1, RED)
    yellow_health_text = HEALTH_FONT.render(f'Health: {yellow_health}', 1, YELLOW)

    WIN.blit(red_health_text, (WIDTH - red_health_text.get_width() - 10, 10))
    WIN.blit(yellow_health_text, (10, 10))

    WIN.blit(YELLOW_SPACESHIP, (yellow.x, yellow.y))
    WIN.blit(RED_SPACESHIP, (red.x, red.y))

    for bullet in red_bullets:
        pygame.draw.rect(WIN, RED, bullet)
    for bullet in yellow_bullets:
        pygame.draw.rect(WIN, YELLOW, bullet)

    pygame.display.update()

# Movement
def yellow_handle_movement(keys_pressed, yellow):
    if keys_pressed[pygame.K_a] and yellow.x - VEL > 0:
        yellow.x -= VEL
    if keys_pressed[pygame.K_d] and yellow.x + VEL + yellow.width < BORDER.x:
        yellow.x += VEL
    if keys_pressed[pygame.K_w] and yellow.y - VEL > 0:
        yellow.y -= VEL
    if keys_pressed[pygame.K_s] and yellow.y + VEL + yellow.height < HEIGHT - 15:
        yellow.y += VEL

def red_handle_movement(keys_pressed, red):
    if keys_pressed[pygame.K_LEFT] and red.x - VEL > BORDER.x + BORDER.width:
        red.x -= VEL
    if keys_pressed[pygame.K_RIGHT] and red.x + VEL + red.width < WIDTH:
        red.x += VEL
    if keys_pressed[pygame.K_UP] and red.y - VEL > 0:
        red.y -= VEL
    if keys_pressed[pygame.K_DOWN] and red.y + VEL + red.height < HEIGHT - 15:
        red.y += VEL

# Bullets
def handle_bullet(yellow_bullets, red_bullets, yellow, red):
    for bullet in yellow_bullets[:]:
        bullet.x += BULLET_VEL
        if red.colliderect(bullet):
            pygame.event.post(pygame.event.Event(RED_HIT))
            yellow_bullets.remove(bullet)
        elif bullet.x > WIDTH:
            yellow_bullets.remove(bullet)

    for bullet in red_bullets[:]:
        bullet.x -= BULLET_VEL
        if yellow.colliderect(bullet):
            pygame.event.post(pygame.event.Event(YELLOW_HIT))
            red_bullets.remove(bullet)
        elif bullet.x < 0:
            red_bullets.remove(bullet)

# Winner
def draw_winner(text):
    draw_text = WINNER_FONT.render(text, 1, WHITE)
    WIN.blit(draw_text, (WIDTH / 2 - draw_text.get_width() / 2, HEIGHT / 2 - draw_text.get_height() / 2))
    pygame.display.update()
    pygame.time.delay(2000)

# Reset
def reset_game():
    red = pygame.Rect(700, 300, SPACESHIP_WIDTH, SPACESHIP_HEIGHT)
    yellow = pygame.Rect(100, 300, SPACESHIP_WIDTH, SPACESHIP_HEIGHT)
    return red, yellow, [], [], 5, 5

# Main loop
def main():
    notify_backend_connection()
    red, yellow, red_bullets, yellow_bullets, yellow_health, red_health = reset_game()
    clock = pygame.time.Clock()
    run = True
    while run:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LCTRL and len(yellow_bullets) < MAX_BULLETS:
                    bullet = pygame.Rect(yellow.x + yellow.width, yellow.y + yellow.height // 2 - 2, 10, 5)
                    yellow_bullets.append(bullet)
                    if BULLET_FIRE_SOUND:
                        BULLET_FIRE_SOUND.play()
                if event.key == pygame.K_RCTRL and len(red_bullets) < MAX_BULLETS:
                    bullet = pygame.Rect(red.x, red.y + red.height // 2 - 2, 10, 5)
                    red_bullets.append(bullet)
                    if BULLET_FIRE_SOUND:
                        BULLET_FIRE_SOUND.play()

            if event.type == RED_HIT:
                red_health -= 1
                if BULLET_HIT_SOUND:
                    BULLET_HIT_SOUND.play()
            if event.type == YELLOW_HIT:
                yellow_health -= 1
                if BULLET_HIT_SOUND:
                    BULLET_HIT_SOUND.play()

        draw_window(red, yellow, red_bullets, yellow_bullets, red_health, yellow_health)

        winner_text = ''
        winner_name = ''
        if red_health <= 0:
            winner_text = 'Yellow wins!'
            winner_name = 'Yellow'
        if yellow_health <= 0:
            winner_text = 'Red wins!'
            winner_name = 'Red'

        if winner_text != '':
            draw_winner(winner_text)
            leaderboard = update_score(winner_name, 100)
            draw_leaderboard(leaderboard)
            break

        keys_pressed = pygame.key.get_pressed()
        yellow_handle_movement(keys_pressed, yellow)
        red_handle_movement(keys_pressed, red)
        handle_bullet(yellow_bullets, red_bullets, yellow, red)

    # Game end loop
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    main()
                    return
                if event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()

if __name__ == '__main__':
    main()
