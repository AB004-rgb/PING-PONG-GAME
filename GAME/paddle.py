import pygame
from pygame.locals import *

class Paddle:
    def __init__(self, x, y, screen_width, screen_height, is_player=True):
        self.rect = pygame.Rect(x, y, 20, 120)
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.speed = 5
        self.is_player = is_player
        self.enlarged = False
        self.enlarge_timer = 0

    def update(self):
        if self.is_player:
            keys = pygame.key.get_pressed()
            if keys[K_UP] and self.rect.top > 0:
                self.rect.move_ip(0, -self.speed)
            if keys[K_DOWN] and self.rect.bottom < self.screen_height:
                self.rect.move_ip(0, self.speed)

        # Handle enlargement timeout
        if self.enlarged:
            self.enlarge_timer -= 1
            if self.enlarge_timer <= 0:
                self.rect.height = 120
                self.enlarged = False

    def update_ai(self, ball):
        if not self.is_player:
            if ball.rect.centery < self.rect.centery and self.rect.top > 0:
                self.rect.move_ip(0, -self.speed)
            elif ball.rect.centery > self.rect.centery and self.rect.bottom < self.screen_height:
                self.rect.move_ip(0, self.speed)

    def enlarge(self):
        if not self.enlarged:
            self.rect.height = 180
            self.enlarged = True
            self.enlarge_timer = 300  # 5 seconds at 60 FPS

    def draw(self, screen):
        pygame.draw.rect(screen, (255, 255, 255), self.rect)