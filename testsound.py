import pygame
pygame.init()
pygame.mixer.init()

sound = pygame.mixer.Sound("assets/jump.wav")
sound.play()

input("Press Enter...")