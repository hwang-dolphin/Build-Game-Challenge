import pygame
import random
import sys
import os

# Initialize pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
ORANGE = (255, 165, 0)

# Create the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Space Shooter")

# Clock for controlling the frame rate
clock = pygame.time.Clock()

# Load images
def load_image(name, colorkey=None, scale=1):
    # Use PNG files for player and enemy ships, create simple colored rectangles for others
    if name == "player":
        try:
            fullname = os.path.join("spaceship_user.png")
            surf = pygame.image.load(fullname)
            # Scale the image to 100x100 as requested
            surf = pygame.transform.scale(surf, (100, 100))
        except pygame.error as e:
            print(f"Cannot load player image: {e}")
            # Fallback to the original polygon if image loading fails
            surf = pygame.Surface((50, 30))
            surf.fill(BLUE)
            pygame.draw.polygon(surf, WHITE, [(0, 15), (50, 0), (50, 30)])
    elif name == "enemy":
        # Load the PNG file for enemy ship
        try:
            fullname = os.path.join("spaceship.png")
            surf = pygame.image.load(fullname)
            # Scale the image to double the original size (80x80 instead of 40x40)
            surf = pygame.transform.scale(surf, (80, 80))
        except pygame.error as e:
            print(f"Cannot load enemy image: {e}")
            # Fallback to the original polygon if image loading fails, but at double size
            surf = pygame.Surface((80, 80))
            surf.fill(RED)
            pygame.draw.polygon(surf, WHITE, [(0, 0), (80, 40), (0, 80)])
    elif name == "laser":
        try:
            fullname = os.path.join("missile.png")
            surf = pygame.image.load(fullname)
            # Scale the missile image to approximately 50x50
            surf = pygame.transform.scale(surf, (50, 20))
        except pygame.error as e:
            print(f"Cannot load missile image: {e}")
            # Fallback to the original rectangle if image loading fails
            surf = pygame.Surface((10, 5))
            surf.fill(GREEN)
    
    if colorkey is not None:
        if colorkey == -1:
            colorkey = surf.get_at((0, 0))
        surf.set_colorkey(colorkey)
    
    if scale != 1:
        surf = pygame.transform.scale(surf, (int(surf.get_width() * scale), int(surf.get_height() * scale)))
    
    return surf

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = load_image("player")
        self.rect = self.image.get_rect()
        self.rect.x = 50
        self.rect.y = SCREEN_HEIGHT // 2
        self.speed = 5
        self.cooldown = 0
        self.health = 100
    
    def update(self):
        # Get pressed keys
        keys = pygame.key.get_pressed()
        
        # Move up and down
        if keys[pygame.K_UP] and self.rect.y > 0:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN] and self.rect.y < SCREEN_HEIGHT - self.rect.height:
            self.rect.y += self.speed
        
        # Decrease cooldown
        if self.cooldown > 0:
            self.cooldown -= 1
    
    def shoot(self):
        if self.cooldown == 0:
            laser = Laser(self.rect.right, self.rect.centery)
            all_sprites.add(laser)
            lasers.add(laser)
            self.cooldown = 15  # Set cooldown to prevent rapid firing

# Enemy class
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = load_image("enemy")
        self.rect = self.image.get_rect()
        self.rect.x = SCREEN_WIDTH
        self.rect.y = random.randint(0, SCREEN_HEIGHT - self.rect.height)
        self.speed = random.randint(3, 7)
    
    def update(self):
        self.rect.x -= self.speed
        
        # Remove if off screen
        if self.rect.right < 0:
            self.kill()
            global score
            score -= 5  # Penalty for missing an enemy

# Laser class
class Laser(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = load_image("laser")
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y - self.rect.height // 2  # Center the missile vertically
        self.speed = 10
    
    def update(self):
        self.rect.x += self.speed
        
        # Remove if off screen
        if self.rect.left > SCREEN_WIDTH:
            self.kill()

# Create sprite groups
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
lasers = pygame.sprite.Group()

# Create player
player = Player()
all_sprites.add(player)

# Game variables
score = 0
enemy_spawn_rate = 60  # Frames between enemy spawns
enemy_timer = 0
game_over = False
font = pygame.font.Font(None, 36)

# Game loop
running = True
while running:
    # Process events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.shoot()
            elif event.key == pygame.K_r and game_over:
                # Restart game
                all_sprites = pygame.sprite.Group()
                enemies = pygame.sprite.Group()
                lasers = pygame.sprite.Group()
                player = Player()
                all_sprites.add(player)
                score = 0
                enemy_spawn_rate = 60
                game_over = False
    
    if not game_over:
        # Spawn enemies
        enemy_timer += 1
        if enemy_timer >= enemy_spawn_rate:
            enemy = Enemy()
            all_sprites.add(enemy)
            enemies.add(enemy)
            enemy_timer = 0
        
        # Update sprites
        all_sprites.update()
        
        # Check for laser hits on enemies
        hits = pygame.sprite.groupcollide(enemies, lasers, True, True)
        for hit in hits:
            score += 10
            # Increase difficulty over time
            if score % 100 == 0 and enemy_spawn_rate > 20:
                enemy_spawn_rate -= 5
        
        # Check for enemy collisions with player
        hits = pygame.sprite.spritecollide(player, enemies, True)
        for hit in hits:
            player.health -= 20
            if player.health <= 0:
                game_over = True
    
    # Draw everything
    screen.fill(BLACK)
    
    # Draw stars in the background
    for i in range(100):
        x = random.randint(0, SCREEN_WIDTH)
        y = random.randint(0, SCREEN_HEIGHT)
        pygame.draw.circle(screen, WHITE, (x, y), 1)
    
    all_sprites.draw(screen)
    
    # Display score and health
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))
    
    health_text = font.render(f"Health: {player.health}", True, WHITE)
    screen.blit(health_text, (10, 50))
    
    # Game over screen
    if game_over:
        game_over_text = font.render("GAME OVER", True, RED)
        restart_text = font.render("Press R to restart", True, WHITE)
        screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, 
                                    SCREEN_HEIGHT // 2 - game_over_text.get_height() // 2))
        screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, 
                                  SCREEN_HEIGHT // 2 + 50))
    
    # Update the display
    pygame.display.flip()
    
    # Cap the frame rate
    clock.tick(60)

# Quit pygame
pygame.quit()
sys.exit()
