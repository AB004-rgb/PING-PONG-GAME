import pygame
import random
from pygame.locals import *

class Ball:
    def __init__(self, x, y, screen_width, screen_height):
        self.rect = pygame.Rect(x, y, 15, 15)
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.speed_x = random.choice([-4, 4])
        self.speed_y = random.choice([-4, 4])
        self.speed_increase = 0.1
        self.power_up_timer = 0
        self.power_up_active = False

    def update(self, player_paddle, ai_paddle, scoreboard):
        self.rect.move_ip(self.speed_x, self.speed_y)

        # Wall collisions
        if self.rect.top <= 0 or self.rect.bottom >= self.screen_height:
            self.speed_y = -self.speed_y

        # Paddle collisions
        if self.rect.colliderect(player_paddle.rect):
            self.speed_x = -self.speed_x
            self.speed_x += self.speed_increase if self.speed_x > 0 else -self.speed_increase
            self.speed_y += self.speed_increase if random.random() > 0.5 else -self.speed_increase
            self._spawn_power_up(player_paddle, ai_paddle)

        if self.rect.colliderect(ai_paddle.rect):
            self.speed_x = -self.speed_x
            self.speed_x += self.speed_increase if self.speed_x > 0 else -self.speed_increase
            self.speed_y += self.speed_increase if random.random() > 0.5 else -self.speed_increase
            self._spawn_power_up(player_paddle, ai_paddle)

        # Scoring
        if self.rect.left <= 0:
            scoreboard.ai_score += 1
            self.reset()
        if self.rect.right >= self.screen_width:
            scoreboard.player_score += 1
            self.reset()

        # Power-up logic (speed boost example)
        if self.power_up_active:
            self.power_up_timer -= 1
            if self.power_up_timer <= 0:
                self.speed_x /= 1.5
                self.speed_y /= 1.5
                self.power_up_active = False

    def _spawn_power_up(self, player_paddle, ai_paddle):
        if random.random() < 0.1:  # 10% chance
            power_up_type = random.choice(['enlarge', 'speed'])
            if power_up_type == 'enlarge':
                random.choice([player_paddle, ai_paddle]).enlarge()
            elif power_up_type == 'speed':
                self.speed_x *= 1.5
                self.speed_y *= 1.5
                self.power_up_active = True
                self.power_up_timer = 180  # 3 seconds

    def reset(self):
        self.rect.center = (self.screen_width // 2, self.screen_height // 2)
        self.speed_x = random.choice([-4, 4])
        self.speed_y = random.choice([-4, 4])

    def draw(self, screen):
        pygame.draw.ellipse(screen, (255, 255, 255), self.rect)