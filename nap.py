import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

class Ball:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 10
        self.speed_x = 5 * random.choice([-1, 1])
        self.speed_y = -5
        self.color = RED
        
    def move(self):
        self.x += self.speed_x
        self.y += self.speed_y
        
        # Bounce off walls
        if self.x <= self.radius or self.x >= SCREEN_WIDTH - self.radius:
            self.speed_x *= -1
            
        # Bounce off ceiling
        if self.y <= self.radius:
            self.speed_y *= -1
            
    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        
    def reset(self):
        self.x = SCREEN_WIDTH // 2
        self.y = SCREEN_HEIGHT // 2
        self.speed_x = 5 * random.choice([-1, 1])
        self.speed_y = -5

class Paddle:
    def __init__(self):
        self.width = 100
        self.height = 15
        self.x = SCREEN_WIDTH // 2 - self.width // 2
        self.y = SCREEN_HEIGHT - 50
        self.speed = 8
        self.color = BLUE
        
    def move(self, direction):
        if direction == "left" and self.x > 0:
            self.x -= self.speed
        if direction == "right" and self.x < SCREEN_WIDTH - self.width:
            self.x += self.speed
            
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

class Brick:
    def __init__(self, x, y, color=GREEN):
        self.width = 70
        self.height = 20
        self.x = x
        self.y = y
        self.color = color
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.visible = True
        
    def draw(self, screen):
        if self.visible:
            pygame.draw.rect(screen, self.color, self.rect)
            pygame.draw.rect(screen, BLACK, self.rect, 2)  # Border

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Bouncing Ball Game")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        self.reset_game()
        
    def reset_game(self):
        self.ball = Ball(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.paddle = Paddle()
        self.bricks = []
        self.score = 0
        self.lives = 3
        self.game_over = False
        self.win = False
        self.create_bricks()
        
    def create_bricks(self):
        # Create rows of bricks
        rows = 5
        cols = 10
        brick_width = 70
        brick_height = 20
        spacing = 5
        
        start_x = (SCREEN_WIDTH - (cols * (brick_width + spacing))) // 2
        start_y = 50
        
        colors = [RED, YELLOW, GREEN, BLUE, (255, 165, 0)]  # Orange for last row
        
        for row in range(rows):
            for col in range(cols):
                x = start_x + col * (brick_width + spacing)
                y = start_y + row * (brick_height + spacing)
                color = colors[row % len(colors)]
                self.bricks.append(Brick(x, y, color))
                
    def handle_collisions(self):
        # Ball and paddle collision
        paddle_rect = self.paddle.get_rect()
        ball_rect = pygame.Rect(
            self.ball.x - self.ball.radius,
            self.ball.y - self.ball.radius,
            self.ball.radius * 2,
            self.ball.radius * 2
        )
        
        if ball_rect.colliderect(paddle_rect) and self.ball.speed_y > 0:
            self.ball.speed_y *= -1
            # Add some angle variation based on where the ball hits the paddle
            relative_hit = (self.ball.x - paddle_rect.centerx) / (paddle_rect.width / 2)
            self.ball.speed_x = relative_hit * 7
            
        # Ball and bricks collision
        for brick in self.bricks[:]:  # Use slice copy to safely modify during iteration
            if brick.visible and ball_rect.colliderect(brick.rect):
                brick.visible = False
                self.bricks.remove(brick)
                self.score += 10
                self.ball.speed_y *= -1
                break  # Only handle one collision per frame
                
        # Ball below paddle (lost life)
        if self.ball.y > SCREEN_HEIGHT:
            self.lives -= 1
            if self.lives > 0:
                self.ball.reset()
            else:
                self.game_over = True
                
        # Check win condition
        if len(self.bricks) == 0:
            self.win = True
            
    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and (self.game_over or self.win):
                        self.reset_game()
                    if event.key == pygame.K_ESCAPE:
                        running = False
                        
            if not self.game_over and not self.win:
                # Handle keyboard input
                keys = pygame.key.get_pressed()
                if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                    self.paddle.move("left")
                if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                    self.paddle.move("right")
                    
                # Update game objects
                self.ball.move()
                self.handle_collisions()
                
            # Draw everything
            self.screen.fill(BLACK)
            
            # Draw game objects
            self.ball.draw(self.screen)
            self.paddle.draw(self.screen)
            for brick in self.bricks:
                brick.draw(self.screen)
                
            # Draw UI
            score_text = self.font.render(f"Score: {self.score}", True, WHITE)
            lives_text = self.font.render(f"Lives: {self.lives}", True, WHITE)
            self.screen.blit(score_text, (10, 10))
            self.screen.blit(lives_text, (SCREEN_WIDTH - 150, 10))
            
            # Draw game over or win message
            if self.game_over:
                game_over_text = self.font.render("GAME OVER!", True, RED)
                restart_text = self.small_font.render("Press SPACE to restart or ESC to quit", True, WHITE)
                text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 30))
                restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 20))
                self.screen.blit(game_over_text, text_rect)
                self.screen.blit(restart_text, restart_rect)
                
            elif self.win:
                win_text = self.font.render("YOU WIN!", True, GREEN)
                score_text_win = self.font.render(f"Final Score: {self.score}", True, WHITE)
                restart_text = self.small_font.render("Press SPACE to play again or ESC to quit", True, WHITE)
                
                win_rect = win_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50))
                score_rect = score_text_win.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
                restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 50))
                
                self.screen.blit(win_text, win_rect)
                self.screen.blit(score_text_win, score_rect)
                self.screen.blit(restart_text, restart_rect)
                
            pygame.display.flip()
            self.clock.tick(FPS)
            
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()