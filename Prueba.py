import pygame
import random
import sys

# Inicialización de PyGame
pygame.init()

# Configuraciones de pantalla
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Escape del laberinto")

# Colores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
MENU_COLOR = (0, 150, 150)

# Configuración del reloj
clock = pygame.time.Clock()

# Cargar imágenes
background_img = pygame.image.load("fondo.jpg")
player_img = pygame.image.load("pez.png")
enemy_img = pygame.image.load("pulpo.png")
coin_img = pygame.image.load("moneda.png")
wall_img = pygame.image.load("barco.png")

# Redimensionar imágenes
background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))
player_img = pygame.transform.scale(player_img, (40, 40))
enemy_img = pygame.transform.scale(enemy_img, (50, 50))
coin_img = pygame.transform.scale(coin_img, (30, 30))
wall_img = pygame.transform.scale(wall_img, (50, 50))

# Configuración inicial
player_pos = [50, 50]
player_speed = 5
player_size = 40

# Variables del juego
score = 0
lives = 3
level = 1
max_level = 5
enemy_speed = 3

# Fuente
font = pygame.font.Font(None, 36)

# Función para mostrar texto centrado
def draw_text_centered(text, font, color, surface, y_offset=0):
    label = font.render(text, True, color)
    text_rect = label.get_rect(center=(WIDTH // 2, HEIGHT // 2 + y_offset))
    surface.blit(label, text_rect)

# Pantalla de inicio
def start_screen():
    screen.fill(MENU_COLOR)
    draw_text_centered("¡Bienvenido a Escape del Laberinto!", font, WHITE, screen, -50)
    draw_text_centered("Usa las teclas de flecha para moverte", font, WHITE, screen, 0)
    draw_text_centered("Evita los enemigos, recoge monedas y completa los niveles", font, WHITE, screen, 50)
    draw_text_centered("Presiona ENTER tecla para empezar", font, WHITE, screen, 150)
    pygame.display.flip()
    wait_for_key()

# Pantalla de fin de nivel
def level_complete_screen():
    screen.fill(MENU_COLOR)
    draw_text_centered(f"¡Nivel {level} completado!", font, WHITE, screen, -50)
    draw_text_centered("Preparándote para el próximo nivel...", font, WHITE, screen, 50)
    pygame.display.flip()
    pygame.time.wait(2000)

# Pantalla de fin del juego
def end_game_screen(message):
    screen.fill(BLACK)
    draw_text_centered(message, font, WHITE, screen, -50)
    draw_text_centered("Presiona R para reiniciar o Q para salir", font, WHITE, screen, 50)
    pygame.display.flip()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    main()
                elif event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()

# Función para esperar una tecla
def wait_for_key():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                return

# Generar enemigos, monedas y paredes
def generate_objects():
    global enemies, coins, walls
    enemies = [[random.randint(100, WIDTH - 100), random.randint(100, HEIGHT - 100), random.choice([-1, 1]), random.choice([-1, 1])] for _ in range(2 + level)]
    coins = [[random.randint(50, WIDTH - 50), random.randint(50, HEIGHT - 50)] for _ in range(5 + level)]
    walls = [[random.randint(50, WIDTH - 100), random.randint(50, HEIGHT - 100), 50, 50] for _ in range(8 + level)]

# Dibujar paredes
def draw_walls():
    for wall in walls:
        screen.blit(wall_img, (wall[0], wall[1]))

# Dibujar monedas
def draw_coins():
    for coin in coins:
        screen.blit(coin_img, (coin[0], coin[1]))

# Dibujar enemigos
def draw_enemies():
    for enemy in enemies:
        screen.blit(enemy_img, (enemy[0], enemy[1]))

# Dibujar jugador
def draw_player():
    screen.blit(player_img, (player_pos[0], player_pos[1]))

# Movimiento del jugador y verificación de colisiones con paredes
def move_player(keys):
    global player_pos
    x, y = player_pos
    original_pos = x, y

    if keys[pygame.K_LEFT]:
        x -= player_speed
    if keys[pygame.K_RIGHT]:
        x += player_speed
    if keys[pygame.K_UP]:
        y -= player_speed
    if keys[pygame.K_DOWN]:
        y += player_speed

    # Limitar movimiento dentro de los límites de la pantalla
    x = max(0, min(WIDTH - player_size, x))
    y = max(0, min(HEIGHT - player_size, y))

    player_pos = [x, y]

    # Verificar colisión con paredes
    if any(pygame.Rect(x, y, player_size, player_size).colliderect(pygame.Rect(wall[0], wall[1], wall[2], wall[3])) for wall in walls):
        player_pos = list(original_pos)

# Movimiento de enemigos
def move_enemies():
    for enemy in enemies:
        enemy[0] += enemy[2] * enemy_speed
        enemy[1] += enemy[3] * enemy_speed

        # Cambiar dirección si tocan los bordes
        if enemy[0] <= 0 or enemy[0] >= WIDTH - 50:
            enemy[2] *= -1
        if enemy[1] <= 0 or enemy[1] >= HEIGHT - 50:
            enemy[3] *= -1

# Colisiones
def check_collisions():
    global score, lives, coins, level
    # Colisión con enemigos
    for enemy in enemies:
        if pygame.Rect(player_pos[0], player_pos[1], player_size, player_size).colliderect(enemy[0], enemy[1], 50, 50):
            lives -= 1
            reset_player()
    # Colisión con monedas
    for coin in coins[:]:
        if pygame.Rect(player_pos[0], player_pos[1], player_size, player_size).colliderect(coin[0], coin[1], 30, 30):
            coins.remove(coin)
            score += 10
    # Si no quedan monedas, avanzar nivel
    if not coins:
        level_up()

# Colisión del jugador con paredes (con margen)
def check_wall_collision():
    margin = 8 # Permite que el jugador pase más cerca de las paredes
    for wall in walls:
        if (player_pos[0] + margin < wall[0] + wall[2] and
            player_pos[0] + player_size - margin > wall[0] and
            player_pos[1] + margin < wall[1] + wall[3] and
            player_pos[1] + player_size - margin > wall[1]):
            return True
    return False


# Reiniciar jugador
def reset_player():
    player_pos[0] = 50
    player_pos[1] = 50

# Avanzar nivel
def level_up():
    global level
    level += 1
    if level > max_level:
        end_game_screen("¡Ganaste el juego!")
    else:
        level_complete_screen()
        generate_objects()

# Juego principal
def main():
    global score, lives, level

    score = 0
    lives = 3
    level = 1
    generate_objects()

    start_screen()

    while True:
        screen.blit(background_img, (0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        keys = pygame.key.get_pressed()
        move_player(keys)
        move_enemies()
        check_collisions()

        draw_player()
        draw_enemies()
        draw_coins()
        draw_walls()

        # Mostrar HUD
        hud_text = f"Puntuación: {score} | Vidas: {lives} | Nivel: {level}"
        draw_text_centered(hud_text, font, WHITE, screen, -250)

        if lives <= 0:
            end_game_screen("¡Perdiste!")

        pygame.display.flip()
        clock.tick(30)

# Iniciar el juego
if __name__ == "__main__":
    main()
