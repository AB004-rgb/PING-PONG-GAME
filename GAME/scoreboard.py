import pygame

class Scoreboard:
    def __init__(self, screen_width, screen_height):
        self.player_score = 0
        self.ai_score = 0
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.font = pygame.font.Font(None, 74)
        self.win_condition = 3  # Best of 3

    def update(self):
        pass  # Scores updated in ball class

    def check_win(self):
        return self.player_score >= self.win_condition or self.ai_score >= self.win_condition

    def reset_scores(self):
        self.player_score = 0
        self.ai_score = 0

    def draw(self, screen):
        player_text = self.font.render(str(self.player_score), True, (255, 255, 255))
        ai_text = self.font.render(str(self.ai_score), True, (255, 255, 255))
        screen.blit(player_text, (self.screen_width // 4, 20))
        screen.blit(ai_text, (self.screen_width * 3 // 4, 20))