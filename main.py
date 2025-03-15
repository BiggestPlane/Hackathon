import pygame
import random
import math
import asyncio
import os
import sys

# Initialize Pygame with browser-friendly settings
pygame.init()
if 'pyodide' in sys.modules:
    import platform
    from pygame.display import set_mode
    from pygame import FULLSCREEN
    if platform.system() == "Emscripten":
        FULLSCREEN = 0x7FFFFFFF

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (34, 139, 34)
RED = (255, 0, 0)
BROWN = (139, 69, 19)
PURPLE = (128, 0, 128)  # For portal effects

# Game states
TITLE_SCREEN = 0
PLAYING = 1
WAVE_ANNOUNCEMENT = 2
BOSS_INTRO = 3
GAME_OVER = 4
PAUSED = 5  # New pause state

# Create the game window
flags = 0
if 'pyodide' in sys.modules:
    flags = FULLSCREEN
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), flags)
pygame.display.set_caption("Skibidi Shrek Swamp Showdown")

# Create a simple jungle background
def create_jungle_background():
    surf = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
    
    # Create a darker gradient background with deeper greens
    for y in range(WINDOW_HEIGHT):
        # Create a darker, more jungle-like gradient
        shade = int(10 + (y / WINDOW_HEIGHT) * 25)  # Reduced brightness
        color = (0, min(40 + shade, 80), 0)  # Much darker green
        pygame.draw.line(surf, color, (0, y), (WINDOW_WIDTH, y))
    
    # Add large background trees (darker shapes)
    for _ in range(15):
        x = random.randint(0, WINDOW_WIDTH)
        height = random.randint(100, 300)
        width = random.randint(40, 80)
        y = random.randint(0, WINDOW_HEIGHT - height)
        tree_color = (0, random.randint(20, 35), 0)  # Darker trees
        pygame.draw.rect(surf, tree_color, (x, y, width, height))
        # Add tree canopy
        canopy_color = (0, random.randint(25, 45), 0)  # Darker canopy
        pygame.draw.circle(surf, canopy_color, (x + width//2, y), width//1.5)
    
    # Add dense vegetation layers (mid-ground)
    for _ in range(200):
        x = random.randint(0, WINDOW_WIDTH)
        y = random.randint(0, WINDOW_HEIGHT)
        size = random.randint(10, 30)
        shade = random.randint(30, 70)  # Darker vegetation
        pygame.draw.circle(surf, (0, shade, 0), (x, y), size)
    
    # Add vines with more natural curves
    for _ in range(25):
        start_x = random.randint(0, WINDOW_WIDTH)
        points = [(start_x, 0)]
        current_x = start_x
        
        for y in range(50, WINDOW_HEIGHT, 20):
            current_x += random.randint(-15, 15)
            points.append((current_x, y))
        
        vine_color = (0, random.randint(35, 55), 0)  # Darker vines
        pygame.draw.lines(surf, vine_color, False, points, random.randint(2, 4))
        
        # Add small leaves along the vine
        for point in points[::2]:
            leaf_size = random.randint(4, 8)
            leaf_color = (0, random.randint(40, 80), 0)  # Darker leaves
            pygame.draw.circle(surf, leaf_color, (point[0], point[1]), leaf_size)
    
    # Add some atmospheric shadows
    shadow_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
    for _ in range(30):
        x = random.randint(0, WINDOW_WIDTH)
        y = random.randint(0, WINDOW_HEIGHT)
        size = random.randint(50, 150)
        pygame.draw.circle(shadow_surface, (0, 0, 0, 10), (x, y), size)
    surf.blit(shadow_surface, (0, 0))
    
    return surf

# Create default sprites
def create_shrek_sprite():
    surf = pygame.Surface((60, 80), pygame.SRCALPHA)
    # Body
    pygame.draw.ellipse(surf, GREEN, (10, 20, 40, 50))
    # Head
    pygame.draw.circle(surf, GREEN, (30, 25), 15)
    # Eyes
    pygame.draw.circle(surf, WHITE, (25, 20), 5)
    pygame.draw.circle(surf, WHITE, (35, 20), 5)
    pygame.draw.circle(surf, BLACK, (25, 20), 2)
    pygame.draw.circle(surf, BLACK, (35, 20), 2)
    # Ears
    pygame.draw.ellipse(surf, GREEN, (10, 15, 10, 15))
    pygame.draw.ellipse(surf, GREEN, (40, 15, 10, 15))
    return surf

def create_toilet_sprite():
    surf = pygame.Surface((50, 60), pygame.SRCALPHA)
    # Base
    pygame.draw.rect(surf, WHITE, (5, 30, 40, 30))
    # Bowl
    pygame.draw.ellipse(surf, WHITE, (0, 10, 50, 30))
    # Seat
    pygame.draw.rect(surf, WHITE, (5, 5, 40, 10))
    # Eyes
    pygame.draw.circle(surf, BLACK, (15, 25), 5)
    pygame.draw.circle(surf, BLACK, (35, 25), 5)
    return surf

# Load and scale sprites
try:
    SHREK_RIGHT = load_sprite('shrek.png', 0.15)
except:
    SHREK_RIGHT = create_shrek_sprite()
SHREK_LEFT = pygame.transform.flip(SHREK_RIGHT, True, False)

try:
    TOILET_SPRITE = load_sprite('toilet.png', 0.12)
except:
    TOILET_SPRITE = create_toilet_sprite()

# Create background
BACKGROUND = create_jungle_background()

class AttackAnimation:
    def __init__(self, x, y, attack_type, facing_right):
        self.x = x
        self.y = y
        self.attack_type = attack_type  # 'punch', 'kick'
        self.frame = 0
        self.max_frames = 10
        self.facing_right = facing_right
        self.width = 30 if attack_type == 'punch' else 40  # Smaller width for more focused attacks
        self.height = 20 if attack_type == 'punch' else 15  # Height adjusted for each attack type

    def update(self):
        self.frame += 1
        return self.frame < self.max_frames

    def draw(self, screen):
        progress = self.frame / self.max_frames
        alpha = int(255 * (1 - progress))
        
        if self.attack_type == 'punch':
            # Draw fist
            fist_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            # Base of fist (wrist)
            pygame.draw.rect(fist_surface, (*GREEN, alpha), (0, 5, 15, 10))
            # Knuckles
            pygame.draw.circle(fist_surface, (*GREEN, alpha), (20, 10), 10)
            
            # Calculate position based on animation progress
            extend = int(80 * (1 - progress))  # How far the fist extends
            x_offset = extend if self.facing_right else -extend
            
            # Draw at body height (adjusted from head height)
            screen.blit(fist_surface if self.facing_right else pygame.transform.flip(fist_surface, True, False),
                       (self.x + x_offset, self.y + 30))  # +30 to move from head to body height
            
        else:  # kick
            # Draw leg
            leg_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            # Leg shape
            pygame.draw.rect(leg_surface, (*RED, alpha), (0, 0, self.width, self.height))
            pygame.draw.circle(leg_surface, (*RED, alpha), (self.width - 8, self.height//2), 8)  # Foot
            
            # Calculate position based on animation progress
            extend = int(100 * (1 - progress))  # How far the leg extends
            x_offset = extend if self.facing_right else -extend
            angle = 20 if self.facing_right else -20  # Angle for kick
            
            # Rotate the leg
            rotated_leg = pygame.transform.rotate(leg_surface, angle)
            
            # Draw at lower body height
            screen.blit(rotated_leg, (self.x + x_offset, self.y + 50))  # +50 to move to leg height

class Portal:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 0
        self.max_radius = 100
        self.growing = True
        self.particles = []

    def update(self):
        if self.growing:
            self.radius = min(self.radius + 2, self.max_radius)
        else:
            self.radius = max(self.radius - 2, 0)

        # Add particles
        if random.random() < 0.3:
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1, 3)
            self.particles.append({
                'x': self.x + math.cos(angle) * self.radius,
                'y': self.y + math.sin(angle) * self.radius,
                'dx': math.cos(angle) * speed,
                'dy': math.sin(angle) * speed,
                'life': 30
            })

        # Update particles
        for particle in self.particles[:]:
            particle['x'] += particle['dx']
            particle['y'] += particle['dy']
            particle['life'] -= 1
            if particle['life'] <= 0:
                self.particles.remove(particle)

    def draw(self, screen):
        # Draw portal
        pygame.draw.circle(screen, PURPLE, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, (*PURPLE, 128), (int(self.x), int(self.y)), self.radius + 10)

        # Draw particles
        for particle in self.particles:
            alpha = int(255 * (particle['life'] / 30))
            pygame.draw.circle(screen, (*PURPLE, alpha), 
                             (int(particle['x']), int(particle['y'])), 3)

class SkibidiToilet:
    def __init__(self):
        self.width = 50
        self.height = 60
        # Randomly choose spawn side (0: right, 1: top, 2: left, 3: bottom)
        spawn_side = random.randint(0, 3)
        if spawn_side == 0:  # Right side
            self.x = WINDOW_WIDTH
            self.y = random.randint(0, WINDOW_HEIGHT - self.height)
            self.velocity_x = -random.uniform(2, 3)
            self.velocity_y = 0
        elif spawn_side == 1:  # Top side
            self.x = random.randint(0, WINDOW_WIDTH - self.width)
            self.y = -self.height
            self.velocity_x = 0
            self.velocity_y = random.uniform(2, 3)
        elif spawn_side == 2:  # Left side
            self.x = -self.width
            self.y = random.randint(0, WINDOW_HEIGHT - self.height)
            self.velocity_x = random.uniform(2, 3)
            self.velocity_y = 0
        else:  # Bottom side
            self.x = random.randint(0, WINDOW_WIDTH - self.width)
            self.y = WINDOW_HEIGHT
            self.velocity_x = 0
            self.velocity_y = -random.uniform(2, 3)
        
        self.base_speed = random.uniform(2, 3)
        self.knockback_resistance = 0.90
        self.health = 30
        self.sprite = TOILET_SPRITE
        self.hit_flash = 0
        self.target_player = None

    def apply_knockback(self, force_x, force_y):
        self.velocity_x += force_x
        self.velocity_y += force_y

    def move(self):
        if self.target_player:
            # Move towards player with slight tracking
            dx = self.target_player.x - self.x
            dy = self.target_player.y - self.y
            dist = math.sqrt(dx * dx + dy * dy)
            if dist > 0:
                self.velocity_x = self.velocity_x * 0.95 + (dx / dist * self.base_speed) * 0.05
                self.velocity_y = self.velocity_y * 0.95 + (dy / dist * self.base_speed) * 0.05

        # Apply knockback resistance
        self.velocity_x *= self.knockback_resistance
        self.velocity_y *= self.knockback_resistance

        # Update position with boundaries
        self.x = max(0, min(WINDOW_WIDTH - self.width, self.x + self.velocity_x))
        self.y = max(0, min(WINDOW_HEIGHT - self.height, self.y + self.velocity_y))

        if self.hit_flash > 0:
            self.hit_flash -= 1

    def draw(self, screen):
        if self.hit_flash > 0 and self.hit_flash % 2 == 0:
            # Create a white flash effect when hit
            white_sprite = self.sprite.copy()
            white_sprite.fill((255, 255, 255, 128), special_flags=pygame.BLEND_RGBA_MULT)
            screen.blit(white_sprite, (self.x, self.y))
        else:
            screen.blit(self.sprite, (self.x, self.y))
        
        # Draw health bar above toilet
        if self.health < 30:  # Only show health bar if damaged
            bar_width = 40
            bar_height = 5
            health_percent = self.health / 30
            pygame.draw.rect(screen, BLACK, (self.x + 4, self.y - 11, bar_width + 2, bar_height + 2))
            pygame.draw.rect(screen, RED, (self.x + 5, self.y - 10, bar_width, bar_height))
            pygame.draw.rect(screen, GREEN, (self.x + 5, self.y - 10, bar_width * health_percent, bar_height))

class SkibidiBoss(SkibidiToilet):
    def __init__(self):
        super().__init__()
        self.width = 100
        self.height = 120
        self.health = 200
        self.max_health = 200
        self.base_speed = 1.5
        self.attack_cooldown = 0
        self.attack_pattern = 0
        self.sprite = pygame.transform.scale(TOILET_SPRITE, (100, 120))

    def update(self, player):
        super().move()
        self.attack_cooldown = max(0, self.attack_cooldown - 1)
        
        if self.attack_cooldown <= 0:
            self.attack_pattern = (self.attack_pattern + 1) % 3
            if self.attack_pattern == 0:
                # Charge attack
                dx = player.x - self.x
                dy = player.y - self.y
                dist = math.sqrt(dx * dx + dy * dy) or 1
                self.velocity_x = dx/dist * 8
                self.velocity_y = dy/dist * 8
            elif self.attack_pattern == 1:
                # Spawn minions
                return ['spawn_minions']
            else:
                # Projectile attack
                return ['projectile']
            self.attack_cooldown = 120

        return []

    def draw(self, screen):
        super().draw(screen)
        # Draw boss health bar at the bottom of the screen
        bar_width = 400
        bar_height = 20
        health_percent = self.health / self.max_health
        pygame.draw.rect(screen, BLACK, (WINDOW_WIDTH//2 - bar_width//2 - 2, WINDOW_HEIGHT - 30 - 2, 
                                       bar_width + 4, bar_height + 4))
        pygame.draw.rect(screen, RED, (WINDOW_WIDTH//2 - bar_width//2, WINDOW_HEIGHT - 30, 
                                     bar_width, bar_height))
        pygame.draw.rect(screen, GREEN, (WINDOW_WIDTH//2 - bar_width//2, WINDOW_HEIGHT - 30, 
                                       int(bar_width * health_percent), bar_height))

class Donkey:
    def __init__(self, x, y):
        self.width = 70
        self.height = 60
        self.x = x
        self.y = y
        self.speed = 8  # Faster than Shrek
        self.lifetime = 20 * FPS  # 20 seconds at 60 FPS
        self.damage = 25
        self.damage_cooldown = 0
        self.facing_right = True  # Add facing direction for Donkey

    def move(self, target_x, target_y):
        dx = target_x - self.x
        dy = target_y - self.y
        dist = math.sqrt(dx * dx + dy * dy)
        if dist > 0:
            self.x += (dx / dist) * self.speed
            self.y += (dy / dist) * self.speed
        # Update facing direction
        if dx > 0:
            self.facing_right = True
        elif dx < 0:
            self.facing_right = False

    def draw(self, screen, shrek_sprite_right, shrek_sprite_left):
        # Simple donkey shape
        donkey_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        # Body
        pygame.draw.ellipse(donkey_surface, BROWN, (10, 20, 50, 30))
        # Head
        pygame.draw.ellipse(donkey_surface, BROWN, (0, 15, 20, 20))
        # Ears
        pygame.draw.ellipse(donkey_surface, BROWN, (5, 5, 8, 15))
        pygame.draw.ellipse(donkey_surface, BROWN, (15, 5, 8, 15))
        # Legs
        for i in range(4):
            x = 15 + i * 15
            pygame.draw.rect(donkey_surface, BROWN, (x, 45, 5, 15))

        # Draw Donkey
        screen.blit(donkey_surface if self.facing_right else pygame.transform.flip(donkey_surface, True, False), 
                   (self.x, self.y))
        
        # Draw Shrek on top of Donkey
        shrek_x = self.x + 5
        shrek_y = self.y - 20  # Position Shrek slightly above Donkey
        screen.blit(shrek_sprite_right if self.facing_right else shrek_sprite_left, 
                   (shrek_x, shrek_y))

class FartCloud:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 10  # Increased starting radius
        self.lifetime = 45  # Increased lifetime
        self.damage = 20
        self.alpha = 180
        self.max_radius = 120  # Increased maximum radius

    def update(self):
        self.radius = min(self.radius + 4, self.max_radius)  # Faster expansion
        self.lifetime -= 1
        self.alpha = int((self.lifetime / 45) * 180)

    def draw(self, screen):
        cloud_surface = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(cloud_surface, (*BROWN, self.alpha), (self.radius, self.radius), self.radius)
        screen.blit(cloud_surface, (self.x - self.radius, self.y - self.radius))

class Shrek:
    def __init__(self):
        self.width = 60
        self.height = 80
        self.x = WINDOW_WIDTH // 4
        self.y = WINDOW_HEIGHT // 2
        self.speed = 5
        self.velocity_x = 0
        self.velocity_y = 0
        self.knockback_resistance = 0.8
        self.health = 100
        self.punch_cooldown = 0
        self.kick_cooldown = 0
        self.fart_cooldown = 0
        self.facing_right = True
        self.sprite_right = SHREK_RIGHT
        self.sprite_left = SHREK_LEFT
        self.current_sprite = self.sprite_right
        self.attack_animations = []
        # Modified Donkey-related attributes
        self.donkey = None
        self.donkey_charge = 0
        self.max_donkey_charge = 100
        self.donkey_ready_flash = 0  # New attribute for flashing effect

    def apply_knockback(self, force_x, force_y):
        self.velocity_x += force_x
        self.velocity_y += force_y

    def move(self, keys):
        # Handle movement with momentum
        target_speed_x = 0
        target_speed_y = 0

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            target_speed_x = -self.speed
            self.facing_right = False
            self.current_sprite = self.sprite_left
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            target_speed_x = self.speed
            self.facing_right = True
            self.current_sprite = self.sprite_right
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            target_speed_y = -self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            target_speed_y = self.speed

        # Apply smooth movement
        self.velocity_x = self.velocity_x * 0.9 + target_speed_x * 0.1
        self.velocity_y = self.velocity_y * 0.9 + target_speed_y * 0.1

        # Apply knockback resistance
        self.velocity_x *= self.knockback_resistance
        self.velocity_y *= self.knockback_resistance

        # Update position with boundaries
        self.x = max(0, min(WINDOW_WIDTH - self.width, self.x + self.velocity_x))
        self.y = max(0, min(WINDOW_HEIGHT - self.height, self.y + self.velocity_y))

    def draw(self, screen):
        if not self.donkey:
            # Draw Shrek sprite only if not riding Donkey
            screen.blit(self.current_sprite, (self.x, self.y))
        
        # Draw health bar with border and background
        pygame.draw.rect(screen, BLACK, (8, 8, 204, 24))
        pygame.draw.rect(screen, (60, 60, 60), (10, 10, 200, 20))
        pygame.draw.rect(screen, GREEN, (10, 10, self.health * 2, 20))

        # Draw Donkey charge meter with improved visuals
        if not self.donkey:
            charge_width = 100
            charge_height = 20
            # Draw meter background and border
            pygame.draw.rect(screen, BLACK, (8, 38, charge_width + 4, charge_height + 4))
            pygame.draw.rect(screen, (60, 60, 60), (10, 40, charge_width, charge_height))
            
            # Draw charge amount
            charge_amount = (self.donkey_charge / self.max_donkey_charge) * charge_width
            if charge_amount > 0:
                if self.donkey_charge >= self.max_donkey_charge:
                    # Flash effect when fully charged
                    if self.donkey_ready_flash // 15 % 2 == 0:
                        pygame.draw.rect(screen, (200, 150, 50), (10, 40, charge_width, charge_height))
                    else:
                        pygame.draw.rect(screen, BROWN, (10, 40, charge_width, charge_height))
                    # Draw "READY!" text and button prompt
                    ready_font = pygame.font.Font(None, 20)
                    ready_text = ready_font.render("READY! (SPACE)", True, WHITE)
                    screen.blit(ready_text, (12, 42))
                else:
                    pygame.draw.rect(screen, BROWN, (10, 40, charge_amount, charge_height))

        # Draw Donkey if active
        if self.donkey:
            self.donkey.draw(screen, self.sprite_right, self.sprite_left)

    def punch(self, enemies):
        if self.punch_cooldown <= 0:
            x = self.x + (self.width if self.facing_right else 0)
            self.attack_animations.append(AttackAnimation(x, self.y, 'punch', self.facing_right))
            damage_dealt = 0
            for enemy in enemies[:]:
                if abs(enemy.x - self.x) < 120 and abs(enemy.y - self.y) < 100:
                    enemy.health -= 15
                    damage_dealt += 15  # Track damage dealt
                    enemy.hit_flash = 10
                    dx = enemy.x - self.x
                    dy = enemy.y - self.y
                    dist = math.sqrt(dx * dx + dy * dy) or 1
                    enemy.apply_knockback(dx/dist * 40, dy/dist * 40)
                    if enemy.health <= 0:
                        enemies.remove(enemy)
                        damage_dealt += 25  # Bonus charge for kills
                        return 100
            # Charge Donkey meter based on damage dealt
            if not self.donkey:
                self.donkey_charge = min(self.max_donkey_charge, self.donkey_charge + damage_dealt * 0.5)
            self.punch_cooldown = 20
        return 0

    def kick(self, enemies):
        if self.kick_cooldown <= 0:
            x = self.x + (self.width if self.facing_right else 0)
            self.attack_animations.append(AttackAnimation(x, self.y, 'kick', self.facing_right))
            damage_dealt = 0
            for enemy in enemies[:]:
                if abs(enemy.x - self.x) < 150 and abs(enemy.y - self.y) < 100:
                    enemy.health -= 20
                    damage_dealt += 20  # Track damage dealt
                    enemy.hit_flash = 10
                    dx = enemy.x - self.x
                    dy = enemy.y - self.y
                    dist = math.sqrt(dx * dx + dy * dy) or 1
                    enemy.apply_knockback(dx/dist * 50, dy/dist * 50)
                    if enemy.health <= 0:
                        enemies.remove(enemy)
                        damage_dealt += 25  # Bonus charge for kills
                        return 100
            # Charge Donkey meter based on damage dealt
            if not self.donkey:
                self.donkey_charge = min(self.max_donkey_charge, self.donkey_charge + damage_dealt * 0.5)
            self.kick_cooldown = 30
        return 0

    def update_donkey(self, keys, enemies):
        # Update ready flash effect
        if self.donkey_charge >= self.max_donkey_charge:
            self.donkey_ready_flash += 1
        
        # Summon Donkey when space is pressed and meter is full
        if keys[pygame.K_SPACE] and not self.donkey and self.donkey_charge >= self.max_donkey_charge:
            self.donkey = Donkey(self.x, self.y)
            self.donkey_charge = 0
            self.donkey_ready_flash = 0

        # Update existing Donkey
        if self.donkey:
            self.donkey.lifetime -= 1
            if self.donkey.lifetime <= 0:
                self.donkey = None
            else:
                self.donkey.move(self.x, self.y)
                # Check for enemy collision
                if self.donkey.damage_cooldown > 0:
                    self.donkey.damage_cooldown -= 1
                for enemy in enemies[:]:
                    if (abs(enemy.x - self.donkey.x) < 50 and 
                        abs(enemy.y - self.donkey.y) < 40 and 
                        self.donkey.damage_cooldown <= 0):
                        enemy.health -= self.donkey.damage
                        enemy.hit_flash = 10
                        if enemy.health <= 0:
                            enemies.remove(enemy)
                        self.donkey.damage_cooldown = 20

async def main():
    clock = pygame.time.Clock()
    shrek = Shrek()
    enemies = []
    fart_clouds = []
    score = 0
    font = pygame.font.Font(None, 36)
    enemy_spawn_timer = 0
    running = True
    
    # Wave system
    current_wave = 1
    wave_enemies_remaining = 0
    game_state = TITLE_SCREEN
    wave_announcement_timer = 0
    boss = None
    portal = None
    
    # Create pause overlay surface
    pause_overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
    pygame.draw.rect(pause_overlay, (0, 0, 0, 128), pause_overlay.get_rect())
    
    # Create pause button surface and rect for click detection
    pause_button = pygame.Surface((40, 40))
    pause_button.fill((60, 60, 60))
    pygame.draw.rect(pause_button, WHITE, (12, 8, 6, 24))
    pygame.draw.rect(pause_button, WHITE, (24, 8, 6, 24))
    pause_button_rect = pygame.Rect(WINDOW_WIDTH - 50, 10, 40, 40)
    
    def start_wave(wave_number):
        nonlocal wave_enemies_remaining, enemy_spawn_timer
        if wave_number < 5:
            wave_enemies_remaining = wave_number * 3
            enemy_spawn_timer = 0
        else:
            nonlocal portal, boss
            portal = Portal(WINDOW_WIDTH//2, WINDOW_HEIGHT//2)
            game_state = BOSS_INTRO

    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p and game_state == PLAYING:
                    game_state = PAUSED
                elif event.key == pygame.K_p and game_state == PAUSED:
                    game_state = PLAYING
                elif game_state == TITLE_SCREEN and event.key == pygame.K_SPACE:
                    game_state = WAVE_ANNOUNCEMENT
                    start_wave(current_wave)
                elif game_state == GAME_OVER and event.key == pygame.K_SPACE:
                    # Reset game
                    shrek = Shrek()
                    enemies = []
                    fart_clouds = []
                    score = 0
                    current_wave = 1
                    boss = None
                    game_state = WAVE_ANNOUNCEMENT
                    start_wave(current_wave)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    mouse_pos = pygame.mouse.get_pos()
                    if pause_button_rect.collidepoint(mouse_pos):
                        if game_state == PLAYING:
                            game_state = PAUSED
                        elif game_state == PAUSED:
                            game_state = PLAYING

        # Draw background
        screen.blit(BACKGROUND, (0, 0))

        if game_state == TITLE_SCREEN:
            # Draw title screen
            title = font.render("Skibidi Shrek Swamp Showdown", True, WHITE)
            start_text = font.render("Press SPACE to Start", True, WHITE)
            controls1 = font.render("Movement: WASD or Arrow Keys", True, WHITE)
            controls2 = font.render("SPACE: Use Donkey when Ready", True, WHITE)
            attacks = font.render("Q: Punch  R: Kick  E: Fart  P: Pause", True, WHITE)
            
            screen.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, WINDOW_HEIGHT//3))
            screen.blit(start_text, (WINDOW_WIDTH//2 - start_text.get_width()//2, WINDOW_HEIGHT//2))
            screen.blit(controls1, (WINDOW_WIDTH//2 - controls1.get_width()//2, WINDOW_HEIGHT//2 + 50))
            screen.blit(controls2, (WINDOW_WIDTH//2 - controls2.get_width()//2, WINDOW_HEIGHT//2 + 90))
            screen.blit(attacks, (WINDOW_WIDTH//2 - attacks.get_width()//2, WINDOW_HEIGHT//2 + 130))
        
        elif game_state == WAVE_ANNOUNCEMENT:
            wave_announcement_timer += 1
            # Show wave announcement for 2 seconds
            wave_text = font.render(f"Wave {current_wave}", True, WHITE)
            screen.blit(wave_text, (WINDOW_WIDTH//2 - wave_text.get_width()//2, WINDOW_HEIGHT//2))
            
            if wave_announcement_timer > 120:  # 2 seconds at 60 FPS
                game_state = PLAYING
                wave_announcement_timer = 0

        elif game_state == BOSS_INTRO:
            if portal:
                portal.update()
                portal.draw(screen)
                if portal.radius >= portal.max_radius and not boss:
                    boss = SkibidiBoss()
                    boss.x = portal.x - boss.width//2
                    boss.y = portal.y - boss.height//2
                    boss.target_player = shrek
                    portal.growing = False
                elif portal.radius <= 0:
                    portal = None
                    game_state = PLAYING

            if boss:
                boss.draw(screen)

            if not portal and boss:
                game_state = PLAYING

        elif game_state == PLAYING:
            # Update game state
            keys = pygame.key.get_pressed()
            shrek.move(keys)

            # Update cooldowns
            shrek.punch_cooldown = max(0, shrek.punch_cooldown - 1)
            shrek.kick_cooldown = max(0, shrek.kick_cooldown - 1)
            shrek.fart_cooldown = max(0, shrek.fart_cooldown - 1)

            # Update Donkey mechanics
            shrek.update_donkey(keys, enemies if not boss else [boss])

            # Update attack animations
            shrek.attack_animations = [anim for anim in shrek.attack_animations if anim.update()]
            for anim in shrek.attack_animations:
                anim.draw(screen)

            # Handle attacks (only if not riding Donkey)
            if not shrek.donkey:
                if keys[pygame.K_q] and shrek.punch_cooldown <= 0:
                    score += shrek.punch(enemies if not boss else [boss])
                if keys[pygame.K_r] and shrek.kick_cooldown <= 0:
                    score += shrek.kick(enemies if not boss else [boss])
                if keys[pygame.K_e] and shrek.fart_cooldown <= 0:
                    fart_clouds.append(FartCloud(shrek.x + shrek.width/2, shrek.y + shrek.height/2))
                    shrek.fart_cooldown = 60

            # Spawn enemies for normal waves
            if current_wave < 5 and wave_enemies_remaining > 0:
                enemy_spawn_timer += 1
                if enemy_spawn_timer >= 180:  # Spawn enemy every 3 seconds
                    new_enemy = SkibidiToilet()
                    new_enemy.target_player = shrek
                    enemies.append(new_enemy)
                    wave_enemies_remaining -= 1
                    enemy_spawn_timer = 0

            # Update enemies
            for enemy in enemies[:]:
                enemy.move()
                # Check if enemy has gone off screen on any side
                if (enemy.x < -enemy.width or 
                    enemy.x > WINDOW_WIDTH or 
                    enemy.y < -enemy.height or 
                    enemy.y > WINDOW_HEIGHT):
                    enemies.remove(enemy)
                    shrek.health -= 20
                    # Knockback player when taking damage from missed enemy
                    dx = shrek.x - enemy.x
                    dy = shrek.y - enemy.y
                    dist = math.sqrt(dx * dx + dy * dy) or 1
                    shrek.apply_knockback(dx/dist * 8, dy/dist * 8)

                # Collision with Shrek
                if (abs(enemy.x - shrek.x) < 40 and 
                    abs(enemy.y - shrek.y) < 40):
                    shrek.health -= 3
                    # Knockback both player and enemy
                    dx = shrek.x - enemy.x
                    dy = shrek.y - enemy.y
                    dist = math.sqrt(dx * dx + dy * dy) or 1
                    knockback_force = 12
                    shrek.apply_knockback(dx/dist * knockback_force, dy/dist * knockback_force)
                    enemy.apply_knockback(-dx/dist * knockback_force * 0.8, -dy/dist * knockback_force * 0.8)

            # Update boss
            if boss:
                actions = boss.update(shrek)
                for action in actions:
                    if action == 'spawn_minions':
                        for _ in range(2):
                            minion = SkibidiToilet()
                            minion.x = boss.x
                            minion.y = boss.y
                            minion.target_player = shrek
                            enemies.append(minion)
                    elif action == 'projectile':
                        # Add projectile logic here if desired
                        pass

            # Update fart clouds
            for cloud in fart_clouds[:]:
                cloud.update()
                if cloud.lifetime <= 0:
                    fart_clouds.remove(cloud)
                else:
                    for enemy in enemies[:]:
                        dx = enemy.x + enemy.width/2 - cloud.x
                        dy = enemy.y + enemy.height/2 - cloud.y
                        distance = math.sqrt(dx*dx + dy*dy)
                        if distance < cloud.radius:
                            enemy.health -= 1  # Reduced damage per tick
                            enemy.hit_flash = 10
                            knockback_force = 15
                            enemy.apply_knockback(dx/distance * knockback_force * 0.2, dy/distance * knockback_force * 0.2)
                            if enemy.health <= 0:
                                enemies.remove(enemy)
                                score += 100

            # Check wave completion
            if current_wave < 5 and wave_enemies_remaining == 0 and len(enemies) == 0:
                current_wave += 1
                game_state = WAVE_ANNOUNCEMENT
                start_wave(current_wave)
            elif current_wave == 5 and boss and boss.health <= 0:
                score += 1000  # Boss defeat bonus
                game_state = GAME_OVER

            # Draw everything
            shrek.draw(screen)
            for enemy in enemies:
                enemy.draw(screen)
            if boss:
                boss.draw(screen)
            for cloud in fart_clouds:
                cloud.draw(screen)

            # Draw wave number and score below health and donkey meter
            wave_text = font.render(f"Wave {current_wave}", True, WHITE)
            score_text = f"Score: {score}"
            shadow = font.render(score_text, True, BLACK)
            text = font.render(score_text, True, WHITE)
            
            # Position them below the Donkey charge meter (which ends at y=60)
            screen.blit(wave_text, (10, 70))  # Wave number below meters
            screen.blit(shadow, (12, 92))     # Score below wave number
            screen.blit(text, (10, 90))       # Score text

            # Draw controls help
            controls_text = font.render("Q: Punch  R: Kick  E: Fart", True, WHITE)
            screen.blit(controls_text, (10, WINDOW_HEIGHT - 30))

            # Draw pause button in top right corner
            if game_state != PAUSED:
                # Draw button background with hover effect
                mouse_pos = pygame.mouse.get_pos()
                if pause_button_rect.collidepoint(mouse_pos):
                    # Lighter color when hovering
                    hover_button = pause_button.copy()
                    hover_button.fill((80, 80, 80))
                    pygame.draw.rect(hover_button, WHITE, (12, 8, 6, 24))
                    pygame.draw.rect(hover_button, WHITE, (24, 8, 6, 24))
                    screen.blit(hover_button, (WINDOW_WIDTH - 50, 10))
                else:
                    screen.blit(pause_button, (WINDOW_WIDTH - 50, 10))
                # Draw button label
                pause_label = font.render("P", True, WHITE)
                screen.blit(pause_label, (WINDOW_WIDTH - 35, 45))

            if shrek.health <= 0:
                game_state = GAME_OVER

        elif game_state == GAME_OVER:
            game_over_text = font.render(f"Game Over! Final Score: {score}", True, WHITE)
            restart_text = font.render("Press SPACE to Restart", True, WHITE)
            screen.blit(game_over_text, (WINDOW_WIDTH//2 - game_over_text.get_width()//2, WINDOW_HEIGHT//2))
            screen.blit(restart_text, (WINDOW_WIDTH//2 - restart_text.get_width()//2, WINDOW_HEIGHT//2 + 50))

        elif game_state == PAUSED:
            # Draw the game state as it was
            shrek.draw(screen)
            for enemy in enemies:
                enemy.draw(screen)
            if boss:
                boss.draw(screen)
            for cloud in fart_clouds:
                cloud.draw(screen)

            # Draw wave number and score as they were
            wave_text = font.render(f"Wave {current_wave}", True, WHITE)
            screen.blit(wave_text, (10, 40))
            score_text = f"Score: {score}"
            shadow = font.render(score_text, True, BLACK)
            text = font.render(score_text, True, WHITE)
            screen.blit(shadow, (12, 12))
            screen.blit(text, (10, 10))

            # Add semi-transparent overlay
            screen.blit(pause_overlay, (0, 0))

            # Draw pause menu
            pause_title = font.render("PAUSED", True, WHITE)
            resume_text = font.render("Press P to Resume", True, WHITE)
            controls_reminder = font.render("Controls:", True, WHITE)
            move_text = font.render("WASD/Arrows - Move", True, WHITE)
            attack_text = font.render("Q - Punch  R - Kick  E - Fart", True, WHITE)
            donkey_text = font.render("Hold SPACE - Charge Donkey", True, WHITE)

            # Center and position all text elements
            center_x = WINDOW_WIDTH // 2
            screen.blit(pause_title, (center_x - pause_title.get_width()//2, WINDOW_HEIGHT//3))
            screen.blit(resume_text, (center_x - resume_text.get_width()//2, WINDOW_HEIGHT//3 + 50))
            screen.blit(controls_reminder, (center_x - controls_reminder.get_width()//2, WINDOW_HEIGHT//3 + 100))
            screen.blit(move_text, (center_x - move_text.get_width()//2, WINDOW_HEIGHT//3 + 130))
            screen.blit(attack_text, (center_x - attack_text.get_width()//2, WINDOW_HEIGHT//3 + 160))
            screen.blit(donkey_text, (center_x - donkey_text.get_width()//2, WINDOW_HEIGHT//3 + 190))

        pygame.display.flip()
        clock.tick(FPS)
        await asyncio.sleep(0)

asyncio.run(main()) 