import pygame
from pygame.locals import *
import sys
import random
import math

# Initialize Pygame
pygame.init()

# Screen setup
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("⚡ Neon Pong ⚡")

# Colors - Vibrant neon palette
BLACK = (10, 10, 20)
WHITE = (255, 255, 255)
NEON_BLUE = (0, 255, 255)
NEON_PINK = (255, 20, 147)
NEON_GREEN = (57, 255, 20)
NEON_PURPLE = (191, 64, 191)
NEON_ORANGE = (255, 140, 0)
NEON_YELLOW = (255, 255, 0)

# Fonts
try:
    font_large = pygame.font.Font(None, 74)
    font_medium = pygame.font.Font(None, 48)
    font_small = pygame.font.Font(None, 36)
    font_tiny = pygame.font.Font(None, 24)
except:
    font_large = pygame.font.SysFont('arial', 74)
    font_medium = pygame.font.SysFont('arial', 48)
    font_small = pygame.font.SysFont('arial', 36)
    font_tiny = pygame.font.SysFont('arial', 24)


class Particle:
    """Particle effect for visual flair"""
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.vx = random.uniform(-3, 3)
        self.vy = random.uniform(-3, 3)
        self.life = 30
        self.max_life = 30
        self.size = random.randint(2, 5)
    
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1
        self.vy += 0.1  # Gravity
    
    def draw(self, surface):
        alpha = int(255 * (self.life / self.max_life))
        s = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        color_with_alpha = (*self.color, alpha)
        pygame.draw.circle(s, color_with_alpha, (self.size, self.size), self.size)
        surface.blit(s, (int(self.x - self.size), int(self.y - self.size)))


class Trail:
    """Trail effect for ball"""
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.life = 20
        self.max_life = 20
        self.radius = 8
    
    def update(self):
        self.life -= 1
    
    def draw(self, surface):
        alpha = int(200 * (self.life / self.max_life))
        s = pygame.Surface((self.radius * 4, self.radius * 4), pygame.SRCALPHA)
        color_with_alpha = (*self.color, alpha)
        pygame.draw.circle(s, color_with_alpha, (self.radius * 2, self.radius * 2), self.radius)
        surface.blit(s, (int(self.x - self.radius * 2), int(self.y - self.radius * 2)))


class Paddle:
    def __init__(self, x, y, screen_width, screen_height, is_player=True):
        self.width = 20
        self.height = 120
        self.x = x
        self.y = y
        self.speed = 7
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.is_player = is_player
        self.ai_speed = 5.5
        self.color = NEON_PINK if is_player else NEON_BLUE
        self.glow_intensity = 0
        self.glow_direction = 1
        self.enlarged = False
        self.enlarge_timer = 0
        
    def update(self):
        """Update player paddle based on keyboard input"""
        if self.is_player:
            keys = pygame.key.get_pressed()
            if keys[K_w] or keys[K_UP]:
                self.y -= self.speed
            if keys[K_s] or keys[K_DOWN]:
                self.y += self.speed
            
            self.y = max(0, min(self.y, self.screen_height - self.height))
        
        # Update glow animation
        self.glow_intensity += self.glow_direction * 2
        if self.glow_intensity >= 30 or self.glow_intensity <= 0:
            self.glow_direction *= -1

        # Handle enlargement timeout
        if self.enlarged:
            self.enlarge_timer -= 1
            if self.enlarge_timer <= 0:
                self.y += 30  # Adjust back to original position
                self.height = 120
                self.enlarged = False
    
    def update_ai(self, ball):
        """AI that follows the ball"""
        paddle_center = self.y + self.height // 2
        ball_center = ball.y
        
        if ball.dx > 0:
            target_y = ball_center
        else:
            target_y = self.screen_height // 2
        
        if paddle_center < target_y - 10:
            self.y += self.ai_speed
        elif paddle_center > target_y + 10:
            self.y -= self.ai_speed
        
        self.y = max(0, min(self.y, self.screen_height - self.height))
    
    def draw(self, surface):
        """Draw paddle with glow effect"""
        # Outer glow
        for i in range(3):
            glow_color = tuple(max(0, min(255, c + self.glow_intensity - i * 10)) for c in self.color)
            s = pygame.Surface((self.width + (3-i)*8, self.height + (3-i)*8), pygame.SRCALPHA)
            alpha = 50 - i * 15
            pygame.draw.rect(s, (*glow_color, alpha), s.get_rect(), border_radius=10)
            surface.blit(s, (self.x - (3-i)*4, self.y - (3-i)*4))
        
        # Main paddle
        pygame.draw.rect(surface, self.color, (self.x, self.y, self.width, self.height), border_radius=8)
        
        # Inner highlight
        highlight_color = tuple(min(255, c + 50) for c in self.color)
        pygame.draw.rect(surface, highlight_color, 
                        (self.x + 4, self.y + 4, self.width - 8, self.height // 3), 
                        border_radius=4)
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def enlarge(self):
        if not self.enlarged:
            self.y -= 30  # Adjust position to keep center
            self.height = 180
            self.enlarged = True
            self.enlarge_timer = 300  # 5 seconds at 60 FPS


class Ball:
    def __init__(self, x, y, screen_width, screen_height):
        self.initial_x = x
        self.initial_y = y
        self.x = x
        self.y = y
        self.radius = 10
        self.base_speed = 6
        self.dx = self.base_speed
        self.dy = self.base_speed
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.max_speed = 14
        self.color = NEON_GREEN
        self.trails = []
        self.pulse = 0
        self.power_up_active = False
        self.power_up_timer = 0
        
    def update(self, player_paddle, ai_paddle, scoreboard, particles):
        """Update ball position and handle collisions"""
        self.x += self.dx
        self.y += self.dy
        
        # Add trail
        if random.random() < 0.5:
            self.trails.append(Trail(self.x, self.y, self.color))
        
        # Update trails
        self.trails = [t for t in self.trails if t.life > 0]
        for trail in self.trails:
            trail.update()
        
        # Update pulse animation
        self.pulse = (self.pulse + 0.2) % (2 * math.pi)
        
        # Top and bottom wall collision
        if self.y - self.radius <= 0 or self.y + self.radius >= self.screen_height:
            self.dy = -self.dy
            self.y = max(self.radius, min(self.y, self.screen_height - self.radius))
            self.create_particles(particles, NEON_PURPLE)
        
        ball_rect = pygame.Rect(self.x - self.radius, self.y - self.radius, 
                                self.radius * 2, self.radius * 2)
        
        # Player paddle collision
        if ball_rect.colliderect(player_paddle.get_rect()) and self.dx < 0:
            self.dx = -self.dx
            relative_intersect = (player_paddle.y + player_paddle.height / 2) - self.y
            self.dy = -relative_intersect / (player_paddle.height / 2) * self.base_speed
            self.increase_speed()
            self.x = player_paddle.x + player_paddle.width + self.radius
            self.color = NEON_PINK
            self.create_particles(particles, NEON_PINK)
            self.maybe_apply_power_up(player_paddle, ai_paddle, particles)
        
        # AI paddle collision
        if ball_rect.colliderect(ai_paddle.get_rect()) and self.dx > 0:
            self.dx = -self.dx
            relative_intersect = (ai_paddle.y + ai_paddle.height / 2) - self.y
            self.dy = -relative_intersect / (ai_paddle.height / 2) * self.base_speed
            self.increase_speed()
            self.x = ai_paddle.x - self.radius
            self.color = NEON_BLUE
            self.create_particles(particles, NEON_BLUE)
            self.maybe_apply_power_up(player_paddle, ai_paddle, particles)
        
        # Score detection
        if self.x - self.radius <= 0:
            scoreboard.ai_score += 1
            self.reset()
            self.create_explosion(particles, NEON_PINK)
        elif self.x + self.radius >= self.screen_width:
            scoreboard.player_score += 1
            self.reset()
            self.create_explosion(particles, NEON_BLUE)

        # Power-up logic (speed boost)
        if self.power_up_active:
            self.power_up_timer -= 1
            if self.power_up_timer <= 0:
                self.dx /= 1.5
                self.dy /= 1.5
                self.power_up_active = False
                self.color = NEON_GREEN  # Reset color after power-up
    
    def create_particles(self, particles, color):
        """Create particle effect"""
        for _ in range(8):
            particles.append(Particle(self.x, self.y, color))
    
    def create_explosion(self, particles, color):
        """Create explosion effect"""
        for _ in range(20):
            particles.append(Particle(self.x, self.y, color))
    
    def increase_speed(self):
        speed_increase = 1.08
        if abs(self.dx) < self.max_speed:
            self.dx *= speed_increase
        if abs(self.dy) < self.max_speed:
            self.dy *= speed_increase
    
    def reset(self):
        self.x = self.initial_x
        self.y = self.initial_y
        self.dx = self.base_speed if self.dx > 0 else -self.base_speed
        self.dy = self.base_speed if self.dy > 0 else -self.base_speed
        self.color = NEON_GREEN
        self.trails = []
        self.power_up_active = False
        self.power_up_timer = 0
        
    def draw(self, surface):
        """Draw trails and ball"""
        # Draw trails
        for trail in self.trails:
            trail.draw(surface)
        
        # Draw glow layers
        pulse_size = int(3 + math.sin(self.pulse) * 2)
        for i in range(4):
            glow_radius = self.radius + pulse_size + (4-i) * 5
            s = pygame.Surface((glow_radius * 4, glow_radius * 4), pygame.SRCALPHA)
            alpha = 40 - i * 10
            pygame.draw.circle(s, (*self.color, alpha), (glow_radius * 2, glow_radius * 2), glow_radius)
            surface.blit(s, (int(self.x - glow_radius * 2), int(self.y - glow_radius * 2)))
        
        # Main ball
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)
        
        # Inner highlight
        highlight_color = tuple(min(255, c + 80) for c in self.color)
        pygame.draw.circle(surface, highlight_color, (int(self.x - 3), int(self.y - 3)), self.radius // 2)

    def maybe_apply_power_up(self, player_paddle, ai_paddle, particles):
        if random.random() < 0.2:  # 20% chance for more engagement
            power_up_type = random.choice(['enlarge', 'speed', 'slow', 'multi_ball'])  # Added more types for engagement
            if power_up_type == 'enlarge':
                paddle = random.choice([player_paddle, ai_paddle])
                paddle.enlarge()
                # Particles for power-up
                for _ in range(15):
                    particles.append(Particle(paddle.x + paddle.width // 2, paddle.y + paddle.height // 2, NEON_ORANGE))
            elif power_up_type == 'speed':
                self.dx *= 1.5
                self.dy *= 1.5
                self.power_up_active = True
                self.power_up_timer = 180
                self.color = NEON_YELLOW  # Change color for visual feedback
                self.create_particles(particles, NEON_YELLOW)
            elif power_up_type == 'slow':
                self.dx /= 1.5
                self.dy /= 1.5
                self.power_up_active = True
                self.power_up_timer = 180
                self.color = NEON_PURPLE  # Change color for visual feedback
                self.create_particles(particles, NEON_PURPLE)
            elif power_up_type == 'multi_ball':
                # For simplicity, increase speed slightly and add particles (simulate multi by visuals)
                self.dx *= 1.2
                self.dy *= 1.2
                for _ in range(10):
                    particles.append(Particle(self.x, self.y, NEON_GREEN))


class Scoreboard:
    def __init__(self, screen_width, screen_height):
        self.player_score = 0
        self.ai_score = 0
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.winning_score = 10
        self.winner = None
        self.score_flash = 0
        
    def update(self):
        if self.player_score >= self.winning_score:
            self.winner = "PLAYER"
        elif self.ai_score >= self.winning_score:
            self.winner = "AI"
        
        if self.score_flash > 0:
            self.score_flash -= 1
    
    def check_win(self):
        return self.winner is not None
    
    def reset_scores(self):
        self.player_score = 0
        self.ai_score = 0
        self.winner = None
    
    def draw(self, surface):
        """Draw scores with glow"""
        player_color = NEON_PINK if self.score_flash == 0 else NEON_YELLOW
        ai_color = NEON_BLUE if self.score_flash == 0 else NEON_YELLOW
        
        player_text = font_large.render(str(self.player_score), True, player_color)
        ai_text = font_large.render(str(self.ai_score), True, ai_color)
        
        # Draw score glows
        for i in range(3):
            alpha = 50 - i * 15
            # Player score glow
            s1 = font_large.render(str(self.player_score), True, player_color)
            s1.set_alpha(alpha)
            surface.blit(s1, (self.screen_width // 4 - player_text.get_width() // 2 - i, 30 - i))
            
            # AI score glow
            s2 = font_large.render(str(self.ai_score), True, ai_color)
            s2.set_alpha(alpha)
            surface.blit(s2, (3 * self.screen_width // 4 - ai_text.get_width() // 2 - i, 30 - i))
        
        surface.blit(player_text, (self.screen_width // 4 - player_text.get_width() // 2, 30))
        surface.blit(ai_text, (3 * self.screen_width // 4 - ai_text.get_width() // 2, 30))
        
        if self.winner:
            # Animated win text
            colors = [NEON_PINK, NEON_BLUE, NEON_GREEN, NEON_PURPLE, NEON_ORANGE]
            win_color = colors[pygame.time.get_ticks() // 200 % len(colors)]
            
            win_text = font_large.render(f"{self.winner} WINS!", True, win_color)
            restart_text = font_small.render("Press SPACE to restart", True, NEON_YELLOW)
            
            # Draw with glow
            for i in range(3):
                alpha = 60 - i * 20
                glow = font_large.render(f"{self.winner} WINS!", True, win_color)
                glow.set_alpha(alpha)
                surface.blit(glow, (self.screen_width // 2 - win_text.get_width() // 2 - i, 
                                   self.screen_height // 2 - 50 - i))
            
            surface.blit(win_text, (self.screen_width // 2 - win_text.get_width() // 2, 
                                   self.screen_height // 2 - 50))
            surface.blit(restart_text, (self.screen_width // 2 - restart_text.get_width() // 2, 
                                       self.screen_height // 2 + 30))


class Game:
    def __init__(self):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.running = True
        self.paused = False
        self.particles = []
        
        self.player_paddle = Paddle(20, SCREEN_HEIGHT // 2 - 60, 
                                     SCREEN_WIDTH, SCREEN_HEIGHT, is_player=True)
        self.ai_paddle = Paddle(SCREEN_WIDTH - 40, SCREEN_HEIGHT // 2 - 60, 
                                SCREEN_WIDTH, SCREEN_HEIGHT, is_player=False)
        self.ball = Ball(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, 
                         SCREEN_WIDTH, SCREEN_HEIGHT)
        self.scoreboard = Scoreboard(SCREEN_WIDTH, SCREEN_HEIGHT)
        
        # Background stars
        self.stars = [(random.randint(0, SCREEN_WIDTH), 
                      random.randint(0, SCREEN_HEIGHT),
                      random.choice([NEON_BLUE, NEON_PINK, NEON_PURPLE, NEON_GREEN])) 
                      for _ in range(50)]
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                self.running = False
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    self.running = False
                elif event.key == K_SPACE:
                    if self.scoreboard.check_win():
                        self.ball.reset()
                        self.scoreboard.reset_scores()
                    else:
                        self.paused = not self.paused
                elif event.key == K_r:
                    self.reset_game()
    
    def reset_game(self):
        self.ball.reset()
        self.scoreboard.reset_scores()
        self.paused = False
        self.particles = []
    
    def update(self):
        if not self.paused and not self.scoreboard.check_win():
            self.player_paddle.update()
            self.ai_paddle.update()
            self.ai_paddle.update_ai(self.ball)
            self.ball.update(self.player_paddle, self.ai_paddle, self.scoreboard, self.particles)
            self.scoreboard.update()
        
        # Always update particles
        self.particles = [p for p in self.particles if p.life > 0]
        for particle in self.particles:
            particle.update()
    
    def draw(self):
        # Dark background
        self.screen.fill(BLACK)
        
        # Draw animated stars
        for i, (x, y, color) in enumerate(self.stars):
            alpha = int(100 + 100 * math.sin(pygame.time.get_ticks() / 1000 + i))
            s = pygame.Surface((4, 4), pygame.SRCALPHA)
            pygame.draw.circle(s, (*color, alpha), (2, 2), 2)
            self.screen.blit(s, (x, y))
        
        # Draw center line with glow
        line_color = NEON_PURPLE
        for i in range(0, SCREEN_HEIGHT, 30):
            s = pygame.Surface((12, 20), pygame.SRCALPHA)
            pygame.draw.rect(s, (*line_color, 100), (0, 0, 12, 20), border_radius=3)
            self.screen.blit(s, (SCREEN_WIDTH // 2 - 6, i))
            pygame.draw.rect(self.screen, line_color, 
                           (SCREEN_WIDTH // 2 - 3, i + 2, 6, 16), border_radius=2)
        
        # Draw particles
        for particle in self.particles:
            particle.draw(self.screen)
        
        # Draw game objects
        self.player_paddle.draw(self.screen)
        self.ai_paddle.draw(self.screen)
        self.ball.draw(self.screen)
        self.scoreboard.draw(self.screen)
        
        # Draw pause message
        if self.paused:
            pause_text = font_large.render("PAUSED", True, NEON_ORANGE)
            for i in range(3):
                alpha = 60 - i * 20
                glow = font_large.render("PAUSED", True, NEON_ORANGE)
                glow.set_alpha(alpha)
                self.screen.blit(glow, (SCREEN_WIDTH // 2 - pause_text.get_width() // 2 - i, 
                                       SCREEN_HEIGHT // 2 - 30 - i))
            self.screen.blit(pause_text, (SCREEN_WIDTH // 2 - pause_text.get_width() // 2, 
                                         SCREEN_HEIGHT // 2 - 30))
        
        # Draw instructions
        if not self.scoreboard.check_win():
            instructions = font_tiny.render("W/S or Arrows | SPACE to pause | R to reset | ESC to quit", 
                                           True, NEON_GREEN)
            instructions.set_alpha(150)
            self.screen.blit(instructions, (SCREEN_WIDTH // 2 - instructions.get_width() // 2, 
                                           SCREEN_HEIGHT - 30))
        
        pygame.display.flip()
    
    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run()