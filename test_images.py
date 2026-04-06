import pygame
import random

pygame.init()

WIDTH, HEIGHT = 800, 500
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Helmet Hunter 2D")

clock = pygame.time.Clock()

# PLAYER
run_frames = [
    pygame.transform.scale(pygame.image.load("assets/run/run1.jpg"), (90,120)),
    pygame.transform.scale(pygame.image.load("assets/run/run2.jpg"), (90,120))
]
idle_img = pygame.transform.scale(pygame.image.load("assets/idle.jpg"), (90,120))

frame_index = 0

player = pygame.Rect(200, 260, 90, 120)
vel_y = 0
gravity = 1
jump_power = -15
on_ground = False

platform = pygame.Rect(0, 400, 2000, 50)

riders = []
spawn_timer = 0

score = 0
font = pygame.font.SysFont(None, 30)

running = True
while running:
    clock.tick(60)
    screen.fill((20,20,20))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()

            for rider in riders[:]:
                if rider["rect"].collidepoint(mx, my):
                    riders.remove(rider)
                    score += 10

    # SPAWN RIDERS
    spawn_timer += 1
    if spawn_timer > 100:
        riders.append({
            "rect": pygame.Rect(800, 320, 60, 60),
            "speed": random.randint(3,6),
            "color": random.choice([(255,0,0), (255,150,0)])  # visual change
        })
        spawn_timer = 0

    # MOVE RIDERS (with animation feel)
    for rider in riders[:]:
        rider["rect"].x -= rider["speed"]

        # small up-down motion (fake animation)
        rider["rect"].y += random.choice([-1, 1])

        if rider["rect"].x < -100:
            riders.remove(rider)

    # PLAYER MOVE
    keys = pygame.key.get_pressed()
    moving = False

    if keys[pygame.K_LEFT]:
        player.x -= 5
        moving = True
    if keys[pygame.K_RIGHT]:
        player.x += 5
        moving = True

    # JUMP
    if keys[pygame.K_UP] and on_ground:
        vel_y = jump_power

    vel_y += gravity
    player.y += vel_y
    on_ground = False

    # PLATFORM
    if player.colliderect(platform) and vel_y >= 0:
        player.bottom = platform.top
        vel_y = 0
        on_ground = True

    pygame.draw.rect(screen, (80,150,255), platform)

    # DRAW RIDERS (animated effect)
    for rider in riders:
        pygame.draw.rect(screen, rider["color"], rider["rect"])

    # PLAYER ANIMATION
    if moving:
        frame_index += 0.2
        if frame_index >= len(run_frames):
            frame_index = 0
        player_img = run_frames[int(frame_index)]
    else:
        player_img = idle_img

    screen.blit(player_img, (player.x, player.y))

    # UI
    text = font.render(f"Score: {score}", True, (255,255,255))
    screen.blit(text, (10,10))

    pygame.display.update()

pygame.quit()