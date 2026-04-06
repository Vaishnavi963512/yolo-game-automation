import pygame, random, numpy as np, cv2
from ultralytics import YOLO

pygame.init()
pygame.mixer.init()

screen = pygame.display.set_mode((800, 400))
clock = pygame.time.Clock()

# 🔊 SOUND
def load_sound(path):
    try:
        return pygame.mixer.Sound(path)
    except:
        return None

jump_sound = load_sound("assets/jump.wav")
correct_sound = load_sound("assets/correct.wav")
wrong_sound = load_sound("assets/wrong.wav")

# 🤖 YOLO MODEL
model = YOLO("best.pt")

def detect_screen(surface):
    img = pygame.surfarray.array3d(surface)
    img = np.transpose(img, (1, 0, 2))
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

    results = model(img, verbose=False)

    detections = []
    for r in results:
        for box in r.boxes:
            cls = int(box.cls[0])
            label = model.names[cls]
            conf = float(box.conf[0])
            x1, y1, x2, y2 = box.xyxy[0]

            detections.append({
                "label": label,
                "conf": round(conf, 2),
                "rect": pygame.Rect(int(x1), int(y1), int(x2-x1), int(y2-y1))
            })

    return detections


# Load images
run1 = pygame.image.load("assets/run/run1.png").convert_alpha()
run2 = pygame.image.load("assets/run/run2.png").convert_alpha()
idle = pygame.image.load("assets/idle.png").convert_alpha()

helmet_img = pygame.image.load("assets/helmet.png").convert_alpha()
nohelmet_img = pygame.image.load("assets/no_helmet.png").convert_alpha()
bg = pygame.image.load("assets/bg.png").convert()

# Resize
run1 = pygame.transform.scale(run1,(80,80))
run2 = pygame.transform.scale(run2,(80,80))
idle = pygame.transform.scale(idle,(80,80))
helmet_img = pygame.transform.scale(helmet_img,(80,80))
nohelmet_img = pygame.transform.scale(nohelmet_img,(80,80))
bg = pygame.transform.scale(bg,(800,400))

font = pygame.font.SysFont(None, 26)
big_font = pygame.font.SysFont(None, 40)

# Player
player = idle.get_rect(topleft=(200,280))
velocity_y = 0
jump = False
direction = "left"

riders = []
frame = 0
bg_x = 0

yolo_timer = 0
detections = []

# 💬 MESSAGE
message = ""
msg_timer = 0

run=True
while run:
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            run=False

    # Background
    bg_x -= 4
    if bg_x <= -800:
        bg_x = 0

    screen.blit(bg,(bg_x,0))
    screen.blit(bg,(bg_x+800,0))

    # Spawn riders
    if random.randint(1,50)==1:
        img = random.choice([helmet_img, nohelmet_img])
        rect = img.get_rect(topleft=(800,280))
        riders.append([img, rect, "unknown"])

    # Draw riders
    for r in riders:
        screen.blit(r[0], r[1])

    # YOLO DETECTION
    if pygame.time.get_ticks() - yolo_timer > 800:
        detections = detect_screen(screen)
        yolo_timer = pygame.time.get_ticks()

    # Matching
    for r in riders:
        best_label = "unknown"
        best_dist = 9999

        rx, ry = r[1].center

        for d in detections:
            if d["conf"] < 0.5:
                continue

            dx, dy = d["rect"].center
            dist = ((rx - dx)**2 + (ry - dy)**2) ** 0.5

            if dist < best_dist:
                best_dist = dist
                best_label = d["label"]

        if best_dist < 120:
            r[2] = best_label

    # Move + AI
    for r in riders[:]:
        r[1].x -= 6

        # Show label
        if r[2] != "unknown":
            color = (0,255,0) if r[2]=="helmet" else (255,0,0)
            screen.blit(font.render(r[2],True,color),(r[1].x,r[1].y-20))

        distance = r[1].x - player.x
        direction = "right" if distance > 0 else "left"

        # 🤖 AI DECISION + SOUND + MESSAGE
        if r[2] != "unknown" and 0 < distance < 80:

            if r[2] == "no_helmet":
                message = "FINE ₹100 ✅"
                if correct_sound: correct_sound.play()
                msg_timer = pygame.time.get_ticks()
                riders.remove(r)

            elif r[2] == "helmet":
                message = "GOOD 👍"
                if not jump:
                    velocity_y = -15
                    jump = True
                    if jump_sound: jump_sound.play()
                msg_timer = pygame.time.get_ticks()

    # Jump physics
    velocity_y += 1
    player.y += velocity_y

    if player.y >= 280:
        player.y = 280
        jump = False

    # Animation
    frame += 0.2
    if frame >= 2:
        frame = 0

    player_img = run1 if int(frame)==0 else run2

    if direction == "right":
        player_img = pygame.transform.flip(player_img, True, False)

    screen.blit(player_img, player)

    # 💬 SHOW MESSAGE
    if pygame.time.get_ticks() - msg_timer < 1500:
        screen.blit(big_font.render(message, True, (255,0,0)), (250,150))

    # Draw YOLO boxes
    for d in detections:
        color = (0,255,0) if d["label"]=="helmet" else (255,0,0)
        pygame.draw.rect(screen, color, d["rect"], 2)

    pygame.display.update()
    clock.tick(60)

pygame.quit()