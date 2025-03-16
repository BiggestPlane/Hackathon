import pygame
import random
import math
import asyncio
import os
import sys
from PIL import Image, ImageSequence  # Add PIL import for GIF handling

# Initialize Pygame with browser-friendly settings
pygame.init()
pygame.mixer.init()  # Initialize the sound mixer

# Set up the display
flags = pygame.SCALED
if 'pyodide' in sys.modules:
    import platform
    if platform.system() == "Emscripten":
        flags = 0x7FFFFFFF  # Special flag for web version

screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), flags)
pygame.display.set_caption("Skibidi Shrek Swamp Showdown")

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60

# Asset paths
ASSET_DIR = os.path.join(os.path.dirname(__file__), 'assets')
IMAGE_DIR = os.path.join(ASSET_DIR, 'images')
SOUND_DIR = os.path.join(ASSET_DIR, 'sounds')

# Load sound effects
try:
    PUNCH_SOUND = pygame.mixer.Sound(os.path.join(SOUND_DIR, 'punch.wav'))
    KICK_SOUND = pygame.mixer.Sound(os.path.join(SOUND_DIR, 'kick.wav'))
    FART_SOUND = pygame.mixer.Sound(os.path.join(SOUND_DIR, 'fart.wav'))
    # Set volume for sounds
    PUNCH_SOUND.set_volume(0.4)
    KICK_SOUND.set_volume(0.4)
    FART_SOUND.set_volume(0.3)
except Exception as e:
    print(f"Error loading sound effects: {e}")
    PUNCH_SOUND = None
    KICK_SOUND = None
    FART_SOUND = None

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (34, 139, 34)
RED = (255, 0, 0)
BROWN = (139, 69, 19)
DARK_BROWN = (101, 67, 33)  # Darker brown for poop
LIGHT_BROWN = (185, 122, 87)  # Lighter brown for poop highlights
PURPLE = (128, 0, 128)  # For portal effects
GOLD = (255, 215, 0)    # For golden onions
LIGHT_BLUE = (135, 206, 250)  # For blue onions

# Game states
TITLE_SCREEN = 0
PLAYING = 1
WAVE_ANNOUNCEMENT = 2
BOSS_INTRO = 3
GAME_OVER = 4
PAUSED = 5  # New pause state
VICTORY = 6  # New victory state

# Create the game window
flags = 0
if 'pyodide' in sys.modules:
    flags = FULLSCREEN
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), flags)
pygame.display.set_caption("Skibidi Shrek Swamp Showdown")

# Create a class to handle GIF animations
class AnimatedSprite:
    def __init__(self, gif_path, scale=1.0):
        self.frames = []
        self.current_frame = 0
        self.frame_delay = 0
        self.frame_timer = 0
        
        try:
            gif = Image.open(gif_path)
            self.frame_delay = gif.info.get('duration', 100)  # Default to 100ms if not specified
            
            for frame in ImageSequence.Iterator(gif):
                # Convert PIL image to Pygame surface
                frame_rgb = frame.convert('RGBA')
                frame_bytes = frame_rgb.tobytes()
                size = frame_rgb.size
                pygame_frame = pygame.image.fromstring(frame_bytes, size, 'RGBA')
                
                # Scale if needed
                if scale != 1.0:
                    new_width = int(size[0] * scale)
                    new_height = int(size[1] * scale)
                    pygame_frame = pygame.transform.scale(pygame_frame, (new_width, new_height))
                
                self.frames.append(pygame_frame)
            
            print(f"Loaded {len(self.frames)} frames from {gif_path}")
        except Exception as e:
            print(f"Error loading GIF {gif_path}: {e}")
            self.frames = None
    
    def get_current_frame(self):
        if not self.frames:
            return None
        return self.frames[self.current_frame]
    
    def update(self, dt):
        if not self.frames:
            return None
        
        self.frame_timer += dt
        if self.frame_timer >= self.frame_delay:
            self.frame_timer = 0
            self.current_frame = (self.current_frame + 1) % len(self.frames)
        
        return self.get_current_frame()

# Load images
def load_image(filename, scale=1.0):
    try:
        path = os.path.join(IMAGE_DIR, filename)
        print(f"Attempting to load image from: {path}")
        if not os.path.exists(path):
            print(f"File not found: {path}")
            return None
            
        image = pygame.image.load(path)
        # Convert the image with alpha for proper transparency
        if filename.endswith('.gif'):
            # For GIF files, we need to handle them differently
            image = image.convert_alpha()
        else:
            # For PNG files, regular convert_alpha is fine
            image = image.convert_alpha()
            
        if scale != 1.0:
            new_width = int(image.get_width() * scale)
            new_height = int(image.get_height() * scale)
            image = pygame.transform.scale(image, (new_width, new_height))
        return image
    except Exception as e:
        print(f"Error loading image {filename}: {e}")
        return None

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
    print("Loading sprites...")
    SHREK_ANIMATION = AnimatedSprite(os.path.join(IMAGE_DIR, 'Bigblackshrek.gif'), 2.5)
    SHREK_RIGHT = SHREK_ANIMATION.get_current_frame() if SHREK_ANIMATION.frames else create_shrek_sprite()
    
    TOILET_ANIMATION = AnimatedSprite(os.path.join(IMAGE_DIR, 'Skibidi toilets.gif'), 2.0)
    TOILET_SPRITE = TOILET_ANIMATION.get_current_frame() if TOILET_ANIMATION.frames else create_toilet_sprite()
    
    ONION_SPRITE = load_image('pixel_onion.png', 0.2)
    if ONION_SPRITE:
        print("Onion sprite loaded successfully")
    
    BACKGROUND_IMAGE = load_image('Grass Background.png')
    if BACKGROUND_IMAGE:
        print("Background loaded successfully")
    
    SWAMP_BACKGROUND = load_image('Swamp.jpg')
    if SWAMP_BACKGROUND:
        print("Swamp background loaded successfully")
        SWAMP_BACKGROUND = pygame.transform.scale(SWAMP_BACKGROUND, (WINDOW_WIDTH, WINDOW_HEIGHT))
    
    # Create fallback sprites if loading fails
    if not SHREK_RIGHT:
        print("Failed to load Shrek sprite, using fallback")
        SHREK_RIGHT = create_shrek_sprite()
    if not TOILET_SPRITE:
        print("Failed to load toilet sprite, using fallback")
        TOILET_SPRITE = create_toilet_sprite()
    if not BACKGROUND_IMAGE:
        print("Failed to load background, using fallback")
        BACKGROUND_IMAGE = create_jungle_background()
    if not SWAMP_BACKGROUND:
        print("Failed to load swamp background, using fallback")
        SWAMP_BACKGROUND = create_jungle_background()
    
    # Create left-facing Shrek sprite
    SHREK_LEFT = pygame.transform.flip(SHREK_RIGHT, True, False)
    
    # Scale background to window size if loaded successfully
    if BACKGROUND_IMAGE:
        BACKGROUND_IMAGE = pygame.transform.scale(BACKGROUND_IMAGE, (WINDOW_WIDTH, WINDOW_HEIGHT))

except Exception as e:
    print(f"Error loading sprites: {e}")
    SHREK_RIGHT = create_shrek_sprite()
    SHREK_LEFT = pygame.transform.flip(SHREK_RIGHT, True, False)
    TOILET_SPRITE = create_toilet_sprite()
    BACKGROUND_IMAGE = create_jungle_background()

# Set the background
BACKGROUND = BACKGROUND_IMAGE

class AttackAnimation:
    def __init__(self, x, y, attack_type, facing_right):
        self.x = x
        self.y = y
        self.attack_type = attack_type  # 'punch', 'kick'
        self.frame = 0
        self.max_frames = 10
        self.facing_right = facing_right
        self.width = 30 if attack_type == 'punch' else 40
        self.height = 20 if attack_type == 'punch' else 15

    def update(self):
        self.frame += 1
        return self.frame < self.max_frames

    def draw(self, screen):
        progress = self.frame / self.max_frames
        alpha = int(255 * (1 - progress))
        
        if self.attack_type == 'punch':
            # Draw fist with darker green
            fist_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            # Base of fist (wrist) - Darker green
            pygame.draw.rect(fist_surface, (20, 100, 20, alpha), (0, 5, 15, 10))
            # Knuckles - Darker green
            pygame.draw.circle(fist_surface, (20, 100, 20, alpha), (20, 10), 10)
            
            extend = int(80 * (1 - progress))
            x_offset = extend if self.facing_right else -extend
            screen.blit(fist_surface if self.facing_right else pygame.transform.flip(fist_surface, True, False),
                       (self.x + x_offset, self.y + 30))
            
        else:  # kick
            # Draw leg with darker red
            leg_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            # Leg shape - Darker red
            pygame.draw.rect(leg_surface, (180, 0, 0, alpha), (0, 0, self.width, self.height))
            pygame.draw.circle(leg_surface, (180, 0, 0, alpha), (self.width - 8, self.height//2), 8)
            
            extend = int(100 * (1 - progress))
            x_offset = extend if self.facing_right else -extend
            angle = 20 if self.facing_right else -20
            
            rotated_leg = pygame.transform.rotate(leg_surface, angle)
            screen.blit(rotated_leg, (self.x + x_offset, self.y + 50))

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
        self.color = (255, 255, 255)  # Pure white for normal toilets
        self.animation = TOILET_ANIMATION

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
        self.x = max(-self.width, min(WINDOW_WIDTH, self.x + self.velocity_x))
        self.y = max(-self.height, min(WINDOW_HEIGHT, self.y + self.velocity_y))

        if self.hit_flash > 0:
            self.hit_flash -= 1

    def draw(self, screen):
        # Update animation frame if available
        if self.animation and self.animation.frames:
            self.sprite = self.animation.update(1000/FPS)  # Convert FPS to milliseconds
            
        # Create a colored version of the sprite
        colored_sprite = self.sprite.copy()
        # Apply color tint more strongly
        color_surface = pygame.Surface(colored_sprite.get_size(), pygame.SRCALPHA)
        color_surface.fill((*self.color, 255))
        colored_sprite.blit(color_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        
        if self.hit_flash > 0 and self.hit_flash % 2 == 0:
            # Create a white flash effect when hit
            white_sprite = colored_sprite.copy()
            white_sprite.fill((255, 255, 255, 128), special_flags=pygame.BLEND_RGBA_MULT)
            screen.blit(white_sprite, (self.x, self.y))
        else:
            screen.blit(colored_sprite, (self.x, self.y))
        
        # Draw health bar above toilet
        if self.health < 30:  # Only show health bar if damaged
            bar_width = 40
            bar_height = 5
            health_percent = self.health / 30
            pygame.draw.rect(screen, BLACK, (self.x + 4, self.y - 11, bar_width + 2, bar_height + 2))
            pygame.draw.rect(screen, RED, (self.x + 5, self.y - 10, bar_width, bar_height))
            pygame.draw.rect(screen, GREEN, (self.x + 5, self.y - 10, bar_width * health_percent, bar_height))

class FastSkibidi(SkibidiToilet):
    def __init__(self):
        self.health = 20  # Set health before parent init
        super().__init__()
        self.base_speed = random.uniform(6, 7)  # Increased from 4-5 to 6-7
        self.color = (0, 0, 255)  # Pure blue for fast toilets
        self.knockback_resistance = 0.95  # More resistant to knockback

class GunnerSkibidi(SkibidiToilet):
    def __init__(self):
        super().__init__()
        self.base_speed = random.uniform(1.5, 2)  # Slower
        self.health = 40  # More health
        self.color = (255, 128, 128)  # Light red for gunner toilets
        self.shoot_cooldown = 0
        self.reload_time = 150  # Increased from 90 to 150 (2.5 seconds between shots)
        self.projectiles = []

    def draw_poop_emoji(self, screen, x, y, size):
        # Draw main poop shape
        pygame.draw.circle(screen, DARK_BROWN, (int(x), int(y)), size)
        # Add highlights
        pygame.draw.circle(screen, LIGHT_BROWN, (int(x - size/3), int(y - size/3)), size//3)
        pygame.draw.circle(screen, LIGHT_BROWN, (int(x + size/3), int(y - size/3)), size//4)
        # Add eyes (small white circles with black dots)
        eye_size = max(2, size//3)
        pygame.draw.circle(screen, WHITE, (int(x - size/4), int(y - size/6)), eye_size)
        pygame.draw.circle(screen, WHITE, (int(x + size/4), int(y - size/6)), eye_size)
        pygame.draw.circle(screen, BLACK, (int(x - size/4), int(y - size/6)), max(1, eye_size//2))
        pygame.draw.circle(screen, BLACK, (int(x + size/4), int(y - size/6)), max(1, eye_size//2))
        # Add smile
        smile_points = [
            (int(x - size/3), int(y + size/4)),
            (int(x), int(y + size/2)),
            (int(x + size/3), int(y + size/4))
        ]
        pygame.draw.lines(screen, BLACK, False, smile_points, max(1, size//4))

    def move(self):
        super().move()
        if self.target_player and self.shoot_cooldown <= 0:
            # Shoot at player
            dx = self.target_player.x - self.x
            dy = self.target_player.y - self.y
            dist = math.sqrt(dx * dx + dy * dy)
            if dist > 0 and dist < 400:  # Only shoot if within range
                self.projectiles.append({
                    'x': self.x + self.width/2,
                    'y': self.y + self.height/2,
                    'dx': dx/dist * 3.5,
                    'dy': dy/dist * 3.5,
                    'lifetime': 120,
                    'size': 10
                })
                self.shoot_cooldown = self.reload_time  # Use the new reload_time
        
        self.shoot_cooldown = max(0, self.shoot_cooldown - 1)
        
        # Update projectiles
        for proj in self.projectiles[:]:
            proj['x'] += proj['dx']
            proj['y'] += proj['dy']
            proj['lifetime'] -= 1
            
            # Check collision with player if not riding Donkey
            if self.target_player and not self.target_player.donkey:
                dx = proj['x'] - (self.target_player.x + self.target_player.width/2)
                dy = proj['y'] - (self.target_player.y + self.height/2)
                dist = math.sqrt(dx * dx + dy * dy)
                if dist < 30:  # Hit radius
                    self.target_player.health -= 10  # Damage amount
                    self.target_player.poop_stain_timer = 120  # 2 seconds at 60 FPS
                    # Apply knockback
                    knockback_force = 8
                    self.target_player.apply_knockback(dx/dist * knockback_force, dy/dist * knockback_force)
                    self.projectiles.remove(proj)
                    continue
            
            if proj['lifetime'] <= 0:
                self.projectiles.remove(proj)

    def draw(self, screen):
        super().draw(screen)
        # Draw projectiles as poop emojis
        for proj in self.projectiles:
            self.draw_poop_emoji(screen, proj['x'], proj['y'], proj['size'])

class SkibidiBoss(SkibidiToilet):
    def __init__(self):
        super().__init__()
        self.width = 200  # Increased from 150 to 200
        self.height = 240  # Increased from 180 to 240
        self.health = 200
        self.max_health = 200
        self.base_speed = 1.5
        self.attack_cooldown = 0
        self.attack_pattern = 0
        self.sprite = pygame.transform.scale(TOILET_SPRITE, (200, 240))  # Match new dimensions
        self.color = (255, 50, 50)  # More intense red for first boss
        self.knockback_resistance = 0.95  # Added higher knockback resistance
        self.name = "Evil Toilet"  # Added boss name
        # Update crown points for larger size
        self.crown_points = [
            (self.width//2 - 40, -25),  # Left point
            (self.width//2 - 30, -40),  # Left peak
            (self.width//2, -25),      # Middle valley
            (self.width//2 + 30, -40),  # Right peak
            (self.width//2 + 40, -25)   # Right point
        ]

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
        # Draw crown on top
        crown_surface = pygame.Surface((self.width, 40), pygame.SRCALPHA)
        pygame.draw.polygon(crown_surface, (255, 215, 0), self.crown_points)  # Gold crown
        screen.blit(crown_surface, (self.x, self.y))
        
        # Draw boss health bar at the bottom of the screen
        bar_width = 400
        bar_height = 20
        health_percent = self.health / self.max_health
        
        # Draw boss name above health bar
        name_font = pygame.font.Font(None, 48)  # Larger font for boss name
        name_text = name_font.render(self.name, True, WHITE)
        name_shadow = name_font.render(self.name, True, BLACK)
        
        # Draw name with shadow effect
        screen.blit(name_shadow, (WINDOW_WIDTH//2 - name_text.get_width()//2 + 2, WINDOW_HEIGHT - 62))
        screen.blit(name_text, (WINDOW_WIDTH//2 - name_text.get_width()//2, WINDOW_HEIGHT - 64))
        
        # Draw health bar
        pygame.draw.rect(screen, BLACK, (WINDOW_WIDTH//2 - bar_width//2 - 2, WINDOW_HEIGHT - 30 - 2, 
                                       bar_width + 4, bar_height + 4))
        pygame.draw.rect(screen, RED, (WINDOW_WIDTH//2 - bar_width//2, WINDOW_HEIGHT - 30, 
                                     bar_width, bar_height))
        pygame.draw.rect(screen, GREEN, (WINDOW_WIDTH//2 - bar_width//2, WINDOW_HEIGHT - 30, 
                                       int(bar_width * health_percent), bar_height))

class SuperSkibidiBoss(SkibidiBoss):
    def __init__(self):
        super().__init__()
        self.width = 300  # Increased from 200 to 300
        self.height = 360  # Increased from 240 to 360
        self.health = 400
        self.max_health = 400
        self.base_speed = 2.0
        self.sprite = pygame.transform.scale(TOILET_SPRITE, (300, 360))  # Match new dimensions
        self.color = (200, 50, 255)  # More intense purple color
        self.missiles = []
        self.missile_cooldown = 0
        self.max_fragments = 32
        self.knockback_resistance = 0.97
        self.name = "Skibidi Sigma Toilet"  # Added boss name
        # Update crown points for larger size
        self.crown_points = [
            (self.width//2 - 60, -35),  # Left point
            (self.width//2 - 45, -55),  # Left peak
            (self.width//2, -35),      # Middle valley
            (self.width//2 + 45, -55),  # Right peak
            (self.width//2 + 60, -35)   # Right point
        ]

    def draw(self, screen):
        super().draw(screen)  # Draw the main boss and crown
        
        # Draw boss health bar at the bottom of the screen
        bar_width = 400
        bar_height = 20
        health_percent = self.health / self.max_health
        
        # Draw boss name above health bar
        name_font = pygame.font.Font(None, 48)  # Larger font for boss name
        name_text = name_font.render(self.name, True, WHITE)
        name_shadow = name_font.render(self.name, True, BLACK)
        
        # Draw name with shadow effect
        screen.blit(name_shadow, (WINDOW_WIDTH//2 - name_text.get_width()//2 + 2, WINDOW_HEIGHT - 62))
        screen.blit(name_text, (WINDOW_WIDTH//2 - name_text.get_width()//2, WINDOW_HEIGHT - 64))
        
        # Draw health bar
        pygame.draw.rect(screen, BLACK, (WINDOW_WIDTH//2 - bar_width//2 - 2, WINDOW_HEIGHT - 30 - 2, 
                                       bar_width + 4, bar_height + 4))
        pygame.draw.rect(screen, RED, (WINDOW_WIDTH//2 - bar_width//2, WINDOW_HEIGHT - 30, 
                                     bar_width, bar_height))
        pygame.draw.rect(screen, GREEN, (WINDOW_WIDTH//2 - bar_width//2, WINDOW_HEIGHT - 30, 
                                       int(bar_width * health_percent), bar_height))

class Donkey:
    def __init__(self, x, y):
        self.width = 100
        self.height = 80
        self.x = x
        self.y = y
        self.speed = 30  # Increased from 20 to 30
        self.lifetime = 20 * FPS
        self.damage = 25
        self.damage_cooldown = 0
        self.facing_right = True
        self.velocity_x = 0
        self.velocity_y = 0

    def move(self, target_x, target_y):
        # Calculate direction to target
        dx = target_x - self.x
        dy = target_y - self.y
        dist = math.sqrt(dx * dx + dy * dy)
        
        if dist > 0:
            # Smoothly update velocity (lerp) with faster response
            target_vel_x = (dx / dist) * self.speed
            target_vel_y = (dy / dist) * self.speed
            
            self.velocity_x = self.velocity_x * 0.6 + target_vel_x * 0.4  # Changed from 0.8/0.2 to 0.6/0.4
            self.velocity_y = self.velocity_y * 0.6 + target_vel_y * 0.4
            
            # Update position
            self.x += self.velocity_x
            self.y += self.velocity_y

    def draw(self, screen, shrek_sprite_right, shrek_sprite_left):
        # Simple donkey shape
        donkey_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        # Body - Made larger
        pygame.draw.ellipse(donkey_surface, BROWN, (20, 25, 60, 40))
        # Head - Adjusted position
        pygame.draw.ellipse(donkey_surface, BROWN, (5, 20, 25, 25))
        # Ears - Adjusted position
        pygame.draw.ellipse(donkey_surface, BROWN, (10, 10, 10, 20))
        pygame.draw.ellipse(donkey_surface, BROWN, (20, 10, 10, 20))
        # Legs - Adjusted positions
        for i in range(4):
            x = 25 + i * 18
            pygame.draw.rect(donkey_surface, BROWN, (x, 60, 6, 20))

        # Draw Donkey
        screen.blit(donkey_surface if self.facing_right else pygame.transform.flip(donkey_surface, True, False), 
                   (self.x, self.y))
        
        # Draw Shrek on top of Donkey with adjusted position
        shrek_x = self.x + (20 if self.facing_right else 40)  # Adjusted horizontal position
        shrek_y = self.y - 40  # Lowered Shrek's position
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

class Onion:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 20
        self.height = 20
        self.rarity = random.choices(['white', 'blue', 'gold'], weights=[70, 25, 5])[0]
        if self.rarity == 'white':
            self.heal_amount = 20  # Increased from 10 to 20
            self.color = WHITE
        elif self.rarity == 'blue':
            self.heal_amount = 40  # Increased from 25 to 40
            self.color = LIGHT_BLUE
        else:  # gold
            self.heal_amount = 80  # Increased from 50 to 80
            self.color = GOLD
        self.pulse_timer = 0
        self.collected = False
        # Use the loaded onion sprite if available
        self.sprite = ONION_SPRITE if 'ONION_SPRITE' in globals() else None

    def draw(self, screen):
        if self.sprite:
            # Create colored version of the sprite based on rarity
            colored_sprite = self.sprite.copy()
            if self.rarity == 'blue':
                colored_sprite.fill((*LIGHT_BLUE, 128), special_flags=pygame.BLEND_RGBA_MULT)
            elif self.rarity == 'gold':
                colored_sprite.fill((*GOLD, 128), special_flags=pygame.BLEND_RGBA_MULT)
            
            # Apply pulsing effect
            self.pulse_timer = (self.pulse_timer + 1) % 60
            pulse = abs(math.sin(self.pulse_timer * 0.1)) * 0.3 + 0.7
            size = int(self.width * pulse)
            
            # Scale sprite with pulse
            pulsed_sprite = pygame.transform.scale(colored_sprite, (size * 2, size * 2))
            screen.blit(pulsed_sprite, (self.x + self.width//2 - size, self.y + self.height//2 - size))
        else:
            # Fallback to original drawing code
            # Create pulsing effect
            self.pulse_timer = (self.pulse_timer + 1) % 60
            pulse = abs(math.sin(self.pulse_timer * 0.1)) * 0.3 + 0.7
            size = int(self.width * pulse)
            
            # Draw onion layers
            pygame.draw.circle(screen, self.color, (self.x + self.width//2, self.y + self.height//2), size)
            pygame.draw.circle(screen, (*self.color, 128), (self.x + self.width//2, self.y + self.height//2), size + 2)
            
            # Draw small stem
            stem_color = (0, 100, 0)
            pygame.draw.rect(screen, stem_color, (self.x + self.width//2 - 2, self.y + self.height//2 - size, 4, 6))

class Shrek:
    def __init__(self):
        self.width = 60
        self.height = 80
        self.x = WINDOW_WIDTH // 4
        self.y = WINDOW_HEIGHT // 2
        self.speed = 6.5  # Increased from 5 to 6.5
        self.velocity_x = 0
        self.velocity_y = 0
        self.knockback_resistance = 0.8
        self.health = 80
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
        self.victory_x = WINDOW_WIDTH // 2  # For victory animation
        self.victory_y = WINDOW_HEIGHT // 2
        self.home_x = WINDOW_WIDTH * 0.85  # Updated to match house in background
        self.home_y = WINDOW_HEIGHT * 0.45  # Updated to match house in background
        self.poop_stain_timer = 0  # Add timer for poop stain effect

    def apply_knockback(self, force_x, force_y):
        self.velocity_x += force_x
        self.velocity_y += force_y

    def move(self, keys):
        # Handle movement with momentum
        target_speed_x = 0
        target_speed_y = 0

        # Double speed if riding Donkey
        current_speed = self.speed * 2 if self.donkey else self.speed

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            target_speed_x = -current_speed
            self.facing_right = False
            self.current_sprite = self.sprite_left
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            target_speed_x = current_speed
            self.facing_right = True
            self.current_sprite = self.sprite_right
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            target_speed_y = -current_speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            target_speed_y = current_speed

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
        
        # Draw poop stain overlay if active
        if self.poop_stain_timer > 0:
            stain_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            alpha = int((self.poop_stain_timer / 120) * 128)  # Fade out over 2 seconds
            stain_surface.fill((DARK_BROWN[0], DARK_BROWN[1], DARK_BROWN[2], alpha))
            screen.blit(stain_surface, (0, 0))
            self.poop_stain_timer -= 1
        
        # Draw health bar with border and background
        pygame.draw.rect(screen, BLACK, (8, 8, 164, 24))  # Reduced from 204 to 164 (80 * 2 + 4 for border)
        pygame.draw.rect(screen, (60, 60, 60), (10, 10, 160, 20))  # Reduced from 200 to 160 (80 * 2)
        pygame.draw.rect(screen, GREEN, (10, 10, self.health * 2, 20))  # Keep multiplier at 2 to maintain same visual size

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
                    damage_dealt += 15
                    enemy.hit_flash = 10
                    dx = enemy.x - self.x
                    dy = enemy.y - self.y
                    dist = math.sqrt(dx * dx + dy * dy) or 1
                    # Reduce knockback, especially for bosses
                    knockback_force = 10 if isinstance(enemy, (SkibidiBoss, SuperSkibidiBoss)) else 15
                    enemy.apply_knockback(dx/dist * knockback_force, dy/dist * knockback_force)
                    if enemy.health <= 0:
                        enemies.remove(enemy)
                        damage_dealt += 25
                        return 100
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
                    damage_dealt += 20
                    enemy.hit_flash = 10
                    dx = enemy.x - self.x
                    dy = enemy.y - self.y
                    dist = math.sqrt(dx * dx + dy * dy) or 1
                    # Reduce knockback, especially for bosses
                    knockback_force = 12 if isinstance(enemy, (SkibidiBoss, SuperSkibidiBoss)) else 20
                    enemy.apply_knockback(dx/dist * knockback_force, dy/dist * knockback_force)
                    if enemy.health <= 0:
                        enemies.remove(enemy)
                        damage_dealt += 25
                        return 100
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

    def move_towards_home(self):
        # Move Shrek towards his swamp home during victory cutscene
        dx = self.home_x - self.victory_x
        dy = self.home_y - self.victory_y
        dist = math.sqrt(dx * dx + dy * dy)
        if dist > 2:  # Keep moving if not very close to home
            self.victory_x += dx * 0.02  # Slow, smooth movement
            self.victory_y += dy * 0.02
            return False
        return True  # Reached home

class VictoryPortal(Portal):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.color = (255, 165, 0)  # Orange color for victory portal
        self.particles = []
        self.max_radius = 60  # Smaller than boss portal

    def draw(self, screen):
        # Draw portal with orange glow
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, (*self.color, 128), (int(self.x), int(self.y)), self.radius + 5)

        # Draw particles
        for particle in self.particles:
            alpha = int(255 * (particle['life'] / 30))
            pygame.draw.circle(screen, (*self.color, alpha), 
                             (int(particle['x']), int(particle['y'])), 2)

async def main():
    clock = pygame.time.Clock()
    shrek = Shrek()
    enemies = []
    fart_clouds = []
    onions = []  # Add onions list
    onion_spawn_timer = 0  # Add spawn timer
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
    
    # Create fonts
    try:
        title_font = pygame.font.Font("freesansbold.ttf", 72)  # Larger size for title
        menu_font = pygame.font.Font("freesansbold.ttf", 36)   # Regular size for menu items
    except:
        title_font = pygame.font.Font(None, 72)  # Fallback if freesansbold isn't available
        menu_font = pygame.font.Font(None, 36)
    
    # Create pause button surface and rect for click detection
    pause_button = pygame.Surface((40, 40))
    pause_button.fill((60, 60, 60))
    pygame.draw.rect(pause_button, WHITE, (12, 8, 6, 24))
    pygame.draw.rect(pause_button, WHITE, (24, 8, 6, 24))
    pause_button_rect = pygame.Rect(WINDOW_WIDTH - 50, 10, 40, 40)
    
    # Add victory animation timer
    victory_timer = 0
    victory_stage = 0  # 0: initial message, 1: walking home, 2: final message
    
    def start_wave(wave_number):
        nonlocal wave_enemies_remaining, enemy_spawn_timer, game_state, portal, boss
        if wave_number != 5 and wave_number != 10:
            wave_enemies_remaining = wave_number * 4  # Reduced from 5 to 4 enemies per wave level
            enemy_spawn_timer = 0
        else:
            wave_enemies_remaining = 0
            enemy_spawn_timer = 0
            portal = Portal(WINDOW_WIDTH//2, WINDOW_HEIGHT//2)
            game_state = BOSS_INTRO
            boss = None

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
                elif (game_state == GAME_OVER or game_state == VICTORY) and event.key == pygame.K_SPACE:
                    # Reset game
                    shrek = Shrek()
                    enemies = []
                    fart_clouds = []
                    onions = []
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
            # Draw title screen with brown text and red outlines
            def draw_outlined_text(surface, text, font, pos_x, pos_y):
                # Draw black outline first for better contrast
                outline_color = BLACK
                text_color = WHITE  # Changed to white for better readability
                outline_surface = font.render(text, True, outline_color)
                text_surface = font.render(text, True, text_color)
                
                # Draw thicker outline by using more offset positions
                outline_positions = [
                    (-3,0), (3,0), (0,-3), (0,3),  # Cardinal directions
                    (-3,-3), (-3,3), (3,-3), (3,3),  # Diagonals
                    (-2,-2), (-2,2), (2,-2), (2,2),  # Inner diagonals
                    (-2,0), (2,0), (0,-2), (0,2)     # Inner cardinal
                ]
                
                # Draw outline
                for dx, dy in outline_positions:
                    surface.blit(outline_surface, (pos_x + dx, pos_y + dy))
                
                # Draw main text
                surface.blit(text_surface, (pos_x, pos_y))
            
            # Calculate positions for center alignment
            title_x = WINDOW_WIDTH//2 - title_font.size("Skibidi Shrek")[0]//2
            subtitle_x = WINDOW_WIDTH//2 - title_font.size("Swamp Showdown")[0]//2
            start_x = WINDOW_WIDTH//2 - menu_font.size("Press SPACE to Start")[0]//2
            controls1_x = WINDOW_WIDTH//2 - menu_font.size("Movement: WASD or Arrow Keys")[0]//2
            controls2_x = WINDOW_WIDTH//2 - menu_font.size("SPACE: Summon Donkey when Meter Full")[0]//2
            attacks_x = WINDOW_WIDTH//2 - menu_font.size("Q: Punch  R: Kick  E: Fart  P: Pause")[0]//2
            
            # Draw all menu text with outlines
            draw_outlined_text(screen, "Skibidi Shrek", title_font, title_x, WINDOW_HEIGHT//4)
            draw_outlined_text(screen, "Swamp Showdown", title_font, subtitle_x, WINDOW_HEIGHT//4 + 80)
            draw_outlined_text(screen, "Press SPACE to Start", menu_font, start_x, WINDOW_HEIGHT//2 + 50)
            draw_outlined_text(screen, "Movement: WASD or Arrow Keys", menu_font, controls1_x, WINDOW_HEIGHT//2 + 100)
            draw_outlined_text(screen, "SPACE: Summon Donkey when Meter Full", menu_font, controls2_x, WINDOW_HEIGHT//2 + 140)
            draw_outlined_text(screen, "Q: Punch  R: Kick  E: Fart  P: Pause", menu_font, attacks_x, WINDOW_HEIGHT//2 + 180)
        
        elif game_state == WAVE_ANNOUNCEMENT:
            wave_announcement_timer += 1
            # Create larger font for wave announcement
            wave_font = pygame.font.Font(None, 96)  # Increased from default 36 to 96
            
            # Show wave announcement with larger text
            wave_text = wave_font.render(f"Wave {current_wave}", True, WHITE)
            
            # Add outline effect for better visibility
            outline_color = BLACK
            outline_text = wave_font.render(f"Wave {current_wave}", True, outline_color)
            
            # Draw outline
            for dx, dy in [(-2,0), (2,0), (0,-2), (0,2), (-2,-2), (-2,2), (2,-2), (2,2)]:
                screen.blit(outline_text, 
                          (WINDOW_WIDTH//2 - wave_text.get_width()//2 + dx, 
                           WINDOW_HEIGHT//2 - wave_text.get_height()//2 + dy))
            
            # Draw main text
            screen.blit(wave_text, 
                      (WINDOW_WIDTH//2 - wave_text.get_width()//2, 
                       WINDOW_HEIGHT//2 - wave_text.get_height()//2))
            
            if wave_announcement_timer > 120:  # 2 seconds at 60 FPS
                game_state = PLAYING
                wave_announcement_timer = 0

        elif game_state == BOSS_INTRO:
            if portal:
                portal.update()
                portal.draw(screen)
                if portal.radius >= portal.max_radius and not boss:
                    if current_wave == 10:
                        boss = SuperSkibidiBoss()
                    else:
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

            # Spawn onions
            onion_spawn_timer += 1
            if onion_spawn_timer >= 600:  # Changed from 1200 to 600 (every 10 seconds instead of 20)
                if len(onions) < 5 and shrek.health < 80:  # Only spawn if Shrek is damaged
                    x = random.randint(50, WINDOW_WIDTH - 50)
                    y = random.randint(50, WINDOW_HEIGHT - 50)
                    onions.append(Onion(x, y))
                onion_spawn_timer = 0

            # Check onion collection
            for onion in onions[:]:
                if (abs(onion.x + onion.width/2 - (shrek.x + shrek.width/2)) < 30 and 
                    abs(onion.y + onion.height/2 - (shrek.y + shrek.height/2)) < 30):
                    old_health = shrek.health
                    shrek.health = min(80, shrek.health + onion.heal_amount)  # Cap at max health
                    actual_heal = shrek.health - old_health  # Calculate actual amount healed
                    # Create healing number popup
                    if actual_heal > 0:  # Only show popup if actually healed
                        healing_text = font.render(f"+{actual_heal}", True, onion.color)
                        screen.blit(healing_text, (shrek.x + 30, shrek.y - 20))
                    onions.remove(onion)

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
                # Get keyboard state and handle punch
                if keys[pygame.K_q] and shrek.punch_cooldown <= 0:
                    # Play punch sound
                    if 'PUNCH_SOUND' in globals() and PUNCH_SOUND:
                        PUNCH_SOUND.play()
                    # Allow hitting both boss and minions
                    if boss:
                        # First check boss
                        boss_hit = False
                        if abs(boss.x - shrek.x) < 120 and abs(boss.y - shrek.y) < 100:
                            x = shrek.x + (shrek.width if shrek.facing_right else 0)
                            shrek.attack_animations.append(AttackAnimation(x, shrek.y, 'punch', shrek.facing_right))
                            boss.health -= 15
                            boss.hit_flash = 10
                            dx = boss.x - shrek.x
                            dy = boss.y - shrek.y
                            dist = math.sqrt(dx * dx + dy * dy) or 1
                            boss.apply_knockback(dx/dist * 5, dy/dist * 5)  # Reduced from 20 to 5
                            if boss.health <= 0:
                                boss = None
                                score += 1000
                                boss_hit = True
                            shrek.punch_cooldown = 20
                        # Then check minions
                        if not boss_hit:  # Only add score for one type of hit
                            score += shrek.punch(enemies)
                    else:  # No boss, just minions
                        score += shrek.punch(enemies)
                if keys[pygame.K_r] and shrek.kick_cooldown <= 0:
                    # Play kick sound
                    if 'KICK_SOUND' in globals() and KICK_SOUND:
                        KICK_SOUND.play()
                    if boss:
                        # First check boss
                        boss_hit = False
                        if abs(boss.x - shrek.x) < 150 and abs(boss.y - shrek.y) < 100:
                            boss.health -= 20
                            boss.hit_flash = 10
                            dx = boss.x - shrek.x
                            dy = boss.y - shrek.y
                            dist = math.sqrt(dx * dx + dy * dy) or 1
                            boss.apply_knockback(dx/dist * 6, dy/dist * 6)  # Reduced from 25 to 6
                            if boss.health <= 0:
                                boss = None
                                score += 1000
                                boss_hit = True
                        # Then check minions
                        if not boss_hit:  # Only add score for one type of hit
                            score += shrek.kick(enemies)
                    else:
                        score += shrek.kick(enemies)
                if keys[pygame.K_e] and shrek.fart_cooldown <= 0:
                    # Play fart sound
                    if 'FART_SOUND' in globals() and FART_SOUND:
                        FART_SOUND.play()
                    fart_clouds.append(FartCloud(shrek.x + shrek.width/2, shrek.y + shrek.height/2))
                    shrek.fart_cooldown = 45  # Reduced from 60 to 45

            # Spawn enemies for normal waves
            if current_wave != 5 and current_wave != 10 and wave_enemies_remaining > 0:
                enemy_spawn_timer += 1
                # Calculate spawn interval based on wave number (gets shorter in later waves)
                spawn_interval = max(30, 120 - (current_wave * 10))  # Starts at 120, decreases by 10 each wave, minimum 30
                if enemy_spawn_timer >= spawn_interval:
                    # Choose enemy type based on wave and random chance
                    enemy_roll = random.random()
                    if current_wave >= 7:  # More gunners in later waves
                        if enemy_roll < 0.25 and current_wave >= 3:  # Reduced from 0.4 to 0.25
                            new_enemy = GunnerSkibidi()
                        elif enemy_roll < 0.7:  # Increased fast toilet chance
                            new_enemy = FastSkibidi()
                        else:
                            new_enemy = SkibidiToilet()
                    elif current_wave >= 3:  # Waves 3-6
                        if enemy_roll < 0.2:  # Reduced from 0.3 to 0.2
                            new_enemy = GunnerSkibidi()
                        elif enemy_roll < 0.6:
                            new_enemy = FastSkibidi()
                        else:
                            new_enemy = SkibidiToilet()
                    else:  # Waves 1-2: no gunners
                        if enemy_roll < 0.6:
                            new_enemy = FastSkibidi()
                        else:
                            new_enemy = SkibidiToilet()
                    
                    # Spawn multiple enemies at once in later waves
                    enemies_per_spawn = min(3, 1 + current_wave // 4)  # Spawn more enemies at once in later waves
                    for _ in range(enemies_per_spawn):
                        if wave_enemies_remaining > 0:
                            # Adjust enemy type probabilities for multiple spawns as well
                            enemy_roll = random.random()  # New roll for each spawn
                            if current_wave >= 7 and current_wave >= 3:
                                new_enemy = (GunnerSkibidi() if enemy_roll < 0.25 else 
                                          (FastSkibidi() if enemy_roll < 0.7 else SkibidiToilet()))
                            elif current_wave >= 3:
                                new_enemy = (GunnerSkibidi() if enemy_roll < 0.2 else 
                                          (FastSkibidi() if enemy_roll < 0.6 else SkibidiToilet()))
                            else:
                                new_enemy = FastSkibidi() if enemy_roll < 0.6 else SkibidiToilet()
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
                    shrek.health -= 30  # Increased from 20 to 30 damage for missing an enemy
                    # Knockback player when taking damage from missed enemy
                    dx = shrek.x - enemy.x
                    dy = shrek.y - enemy.y
                    dist = math.sqrt(dx * dx + dy * dy) or 1
                    shrek.apply_knockback(dx/dist * 8, dy/dist * 8)

                # Collision with Shrek (only if not riding Donkey)
                if not shrek.donkey and (abs(enemy.x - shrek.x) < 40 and 
                    abs(enemy.y - shrek.y) < 40):
                    shrek.health -= 5  # Increased from 3 to 5 damage per collision
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

                # Check boss collision with Shrek (only if not riding Donkey)
                if not shrek.donkey and (abs(boss.x - shrek.x) < 60 and 
                    abs(boss.y - shrek.y) < 60):
                    shrek.health -= 8  # Increased from 5 to 8 damage for boss collision
                    # Knockback both player and boss
                    dx = shrek.x - boss.x
                    dy = shrek.y - boss.y
                    dist = math.sqrt(dx * dx + dy * dy) or 1
                    knockback_force = 15
                    shrek.apply_knockback(dx/dist * knockback_force, dy/dist * knockback_force)
                    boss.apply_knockback(-dx/dist * knockback_force * 0.5, -dy/dist * knockback_force * 0.5)

            # Update fart clouds
            for cloud in fart_clouds[:]:
                cloud.update()
                if cloud.lifetime <= 0:
                    fart_clouds.remove(cloud)
                else:
                    # Check boss damage from fart and block missiles
                    if boss:
                        # Check boss missiles
                        if isinstance(boss, SuperSkibidiBoss):
                            for missile in boss.missiles[:]:
                                dx = missile['x'] - cloud.x
                                dy = missile['y'] - cloud.y
                                distance = math.sqrt(dx*dx + dy*dy)
                                if distance < cloud.radius:
                                    boss.missiles.remove(missile)  # Destroy missile
                                    continue

                        # Normal boss damage
                        dx = boss.x + boss.width/2 - cloud.x
                        dy = boss.y + boss.height/2 - cloud.y
                        distance = math.sqrt(dx*dx + dy*dy)
                        if distance < cloud.radius:
                            boss.health -= 1
                            boss.hit_flash = 10
                            knockback_force = 15
                            boss.apply_knockback(dx/distance * knockback_force * 0.2, dy/distance * knockback_force * 0.2)
                            if boss.health <= 0:
                                boss = None
                                score += 1000
                    
                    # Check minion damage from fart and block projectiles
                    for enemy in enemies[:]:
                        # Check gunner projectiles
                        if isinstance(enemy, GunnerSkibidi):
                            for proj in enemy.projectiles[:]:
                                dx = proj['x'] - cloud.x
                                dy = proj['y'] - cloud.y
                                distance = math.sqrt(dx*dx + dy*dy)
                                if distance < cloud.radius:
                                    enemy.projectiles.remove(proj)  # Destroy projectile
                                    continue

                        # Normal enemy damage
                        dx = enemy.x + enemy.width/2 - cloud.x
                        dy = enemy.y + enemy.height/2 - cloud.y
                        distance = math.sqrt(dx*dx + dy*dy)
                        if distance < cloud.radius:
                            enemy.health -= 1
                            enemy.hit_flash = 10
                            knockback_force = 15
                            enemy.apply_knockback(dx/distance * knockback_force * 0.2, dy/distance * knockback_force * 0.2)
                            if enemy.health <= 0:
                                enemies.remove(enemy)
                                score += 100

            # Check wave completion and victory
            if current_wave < 10 and wave_enemies_remaining == 0 and len(enemies) == 0:
                if current_wave == 5:
                    if not boss:  # First boss defeated
                        current_wave += 1
                        score += 1000  # First boss defeat bonus
                        game_state = WAVE_ANNOUNCEMENT
                        start_wave(current_wave)
                elif current_wave != 5:
                    current_wave += 1
                    game_state = WAVE_ANNOUNCEMENT
                    start_wave(current_wave)
            elif current_wave == 10:  # Final boss wave
                if boss and boss.health <= 0:  # Boss just defeated
                    boss = None
                    score += 2000  # Super boss defeat bonus
                elif not boss and len(enemies) == 0:  # Boss is dead and all enemies cleared
                    game_state = VICTORY
                    victory_timer = 0
                    victory_stage = 0
                    # Initialize victory animation
                    shrek.victory_x = shrek.x
                    shrek.victory_y = shrek.y

            # Draw everything
            shrek.draw(screen)
            for enemy in enemies:
                enemy.draw(screen)
            if boss:
                boss.draw(screen)
            if portal:  # Make sure portal is always drawn if it exists
                portal.update()
                portal.draw(screen)
            for cloud in fart_clouds:
                cloud.draw(screen)
            for onion in onions:  # Draw onions
                onion.draw(screen)

            # Draw wave number and score below health and donkey meter
            wave_text = font.render(f"Wave {current_wave}", True, WHITE)
            if current_wave == 5:
                boss_text = font.render("BOSS FIGHT", True, RED)
                screen.blit(wave_text, (10, 70))
                screen.blit(boss_text, (10, 100))  # Display boss text below wave number
                score_text = f"Score: {score}"
                shadow = font.render(score_text, True, BLACK)
                text = font.render(score_text, True, WHITE)
                screen.blit(shadow, (12, 122))     # Moved score down to accommodate boss text
                screen.blit(text, (10, 120))
            else:
                screen.blit(wave_text, (10, 70))
                score_text = f"Score: {score}"
                shadow = font.render(score_text, True, BLACK)
                text = font.render(score_text, True, WHITE)
                screen.blit(shadow, (12, 92))
                screen.blit(text, (10, 90))

            # Draw controls help (update text to show Q instead of Left Click)
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
            donkey_text = font.render("SPACE - Summon Donkey when Meter Full", True, WHITE)

            # Center and position all text elements
            center_x = WINDOW_WIDTH // 2
            screen.blit(pause_title, (center_x - pause_title.get_width()//2, WINDOW_HEIGHT//3))
            screen.blit(resume_text, (center_x - resume_text.get_width()//2, WINDOW_HEIGHT//3 + 50))
            screen.blit(controls_reminder, (center_x - controls_reminder.get_width()//2, WINDOW_HEIGHT//3 + 100))
            screen.blit(move_text, (center_x - move_text.get_width()//2, WINDOW_HEIGHT//3 + 130))
            screen.blit(attack_text, (center_x - attack_text.get_width()//2, WINDOW_HEIGHT//3 + 160))
            screen.blit(donkey_text, (center_x - donkey_text.get_width()//2, WINDOW_HEIGHT//3 + 190))

        elif game_state == VICTORY:
            # Draw swamp background for victory scene
            screen.blit(SWAMP_BACKGROUND, (0, 0))
            
            # Draw score
            score_text = font.render(f"Final Score: {score}", True, WHITE)
            screen.blit(score_text, (10, 10))

            if victory_stage == 0:
                # Initial victory message
                victory_text = font.render("YOU WIN!", True, WHITE)
                subtitle = font.render("Time to go home...", True, WHITE)
                screen.blit(victory_text, (WINDOW_WIDTH//2 - victory_text.get_width()//2, WINDOW_HEIGHT//3))
                screen.blit(subtitle, (WINDOW_WIDTH//2 - subtitle.get_width()//2, WINDOW_HEIGHT//3 + 50))
                
                victory_timer += 1
                if victory_timer > 180:  # Show message for 3 seconds
                    victory_stage = 1
                    victory_timer = 0

            elif victory_stage == 1:
                # Move Shrek towards home
                if shrek.move_towards_home():
                    victory_stage = 2
                    victory_timer = 0

                # Draw Shrek at current position
                screen.blit(shrek.sprite_right if shrek.home_x > shrek.victory_x else shrek.sprite_left,
                          (shrek.victory_x, shrek.victory_y))

            else:  # victory_stage == 2
                # Draw Shrek at final position
                screen.blit(shrek.sprite_right, (shrek.home_x - 30, shrek.home_y - 40))

                # Final message with shadow for better visibility
                final_text = font.render("Back in my swamp!", True, WHITE)
                restart_text = font.render("Press SPACE to Play Again", True, WHITE)
                
                # Draw text shadows
                shadow_text = font.render("Back in my swamp!", True, BLACK)
                shadow_restart = font.render("Press SPACE to Play Again", True, BLACK)
                
                # Draw shadows slightly offset
                screen.blit(shadow_text, (WINDOW_WIDTH//2 - final_text.get_width()//2 + 2, WINDOW_HEIGHT//3 + 2))
                screen.blit(shadow_restart, (WINDOW_WIDTH//2 - restart_text.get_width()//2 + 2, WINDOW_HEIGHT//3 + 52))
                
                # Draw main text
                screen.blit(final_text, (WINDOW_WIDTH//2 - final_text.get_width()//2, WINDOW_HEIGHT//3))
                screen.blit(restart_text, (WINDOW_WIDTH//2 - restart_text.get_width()//2, WINDOW_HEIGHT//3 + 50))

        pygame.display.flip()
        clock.tick(FPS)
        await asyncio.sleep(0)

asyncio.run(main()) 