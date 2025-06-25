import pygame
import math
import random

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
PLAYER_SPEED = 2
ENEMY_SPEED = 1.5
PURSUIT_SPEED = 2.5
DETECTION_RANGE = 150
PURSUIT_RANGE = 250
WALL_COLOR = (150, 150, 150)
FOV = 90  # Field of View

# Create screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Hunter Assassin Clone")

# Clock
clock = pygame.time.Clock()

# Player class
class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 20, 20)
        self.speed = PLAYER_SPEED

    def move(self, keys, walls):
        dx, dy = 0, 0
        if keys[pygame.K_LEFT]:
            dx = -self.speed
        if keys[pygame.K_RIGHT]:
            dx = self.speed
        if keys[pygame.K_UP]:
            dy = -self.speed
        if keys[pygame.K_DOWN]:
            dy = self.speed

        new_rect = self.rect.move(dx, dy)
        if not any(new_rect.colliderect(wall) for wall in walls):
            self.rect = new_rect

    def draw(self):
        pygame.draw.rect(screen, BLUE, self.rect)

# Enemy class
class Enemy:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 20, 20)
        self.speed = ENEMY_SPEED
        self.pursuing = False
        self.patrol_target = self.get_new_patrol_target()
        self.pursuit_timer = 0
        self.angle = random.randint(0, 360)  # Facing direction
        self.look_angle = self.angle  # Independent head rotation

    def get_new_patrol_target(self):
        return pygame.Rect(random.randint(0, WIDTH-20), random.randint(0, HEIGHT-20), 20, 20)

    def patrol(self, walls):
        direction = pygame.Vector2(self.patrol_target.x - self.rect.x, self.patrol_target.y - self.rect.y)
        if direction.length() > 0:
            direction = direction.normalize()

        new_rect = self.rect.move(int(direction.x * self.speed), int(direction.y * self.speed))

        if not any(new_rect.colliderect(wall) for wall in walls):
            self.rect = new_rect
        else:
            self.patrol_target = self.get_new_patrol_target()

        # Update facing direction
        self.angle = math.degrees(math.atan2(direction.y, direction.x))

        # Dynamic head rotation
        self.look_angle += random.choice([-2, 2])  # Look around while moving
        self.look_angle = (self.look_angle + 360) % 360  # Keep in range

    def pursue(self, player, walls):
        direction = pygame.Vector2(player.rect.x - self.rect.x, player.rect.y - self.rect.y)
        if direction.length() > 0:
            direction = direction.normalize()

        new_rect = self.rect.move(int(direction.x * PURSUIT_SPEED), int(direction.y * PURSUIT_SPEED))

        if not any(new_rect.colliderect(wall) for wall in walls):
            self.rect = new_rect
        else:
            self.pursuing = False

        # Face the player
        self.angle = math.degrees(math.atan2(direction.y, direction.x))
        self.look_angle = self.angle  # Lock head to pursuit direction

    def check_sight(self, player, walls):
        direction_to_player = pygame.Vector2(player.rect.center) - pygame.Vector2(self.rect.center)
        distance = direction_to_player.length()

        if distance < DETECTION_RANGE:
            angle_to_player = math.degrees(math.atan2(direction_to_player.y, direction_to_player.x))
            angle_difference = (angle_to_player - self.look_angle + 180) % 360 - 180

            if abs(angle_difference) < FOV / 2:
                blocked = False
                for wall in walls:
                    if wall.clipline(self.rect.center, player.rect.center):
                        blocked = True
                        break

                if not blocked:
                    self.pursuing = True
                    self.pursuit_timer = 300
                    return True

        return False

    def update(self, player, walls):
        if self.pursuing:
            self.pursue(player, walls)
            self.pursuit_timer -= 1
            if self.pursuit_timer <= 0:
                self.pursuing = False
        else:
            if not self.check_sight(player, walls):
                self.patrol(walls)  # Ensure enemies never stop moving

    def draw(self):
        pygame.draw.rect(screen, RED, self.rect)

        # Draw vision cone
        start_angle = math.radians(self.look_angle - FOV / 2)
        end_angle = math.radians(self.look_angle + FOV / 2)
        num_points = 20
        points = [self.rect.center]

        for i in range(num_points + 1):
            angle = start_angle + (end_angle - start_angle) * (i / num_points)
            ray_length = DETECTION_RANGE
            end_pos = (self.rect.centerx + ray_length * math.cos(angle),
                       self.rect.centery + ray_length * math.sin(angle))

            for wall in walls:
                if wall.clipline(self.rect.center, end_pos):
                    end_pos = wall.clipline(self.rect.center, end_pos)[0]

            points.append(end_pos)

        pygame.draw.polygon(screen, RED, points, 1)  # Change radar color to RED

# Walls
walls = [
    pygame.Rect(200, 100, 50, 300),
    pygame.Rect(400, 200, 50, 200),
    pygame.Rect(600, 100, 50, 300)
]

# Game objects
player = Player(100, 100)
enemies = [Enemy(500, 500), Enemy(300, 300)]

# Game loop
running = True
while running:
    screen.fill(WHITE)
    keys = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update game objects
    player.move(keys, walls)
    for enemy in enemies:
        enemy.update(player, walls)

    # Draw everything
    for wall in walls:
        pygame.draw.rect(screen, WALL_COLOR, wall)

    player.draw()
    for enemy in enemies:
        enemy.draw()

    pygame.display.flip()
    clock.tick(30)

pygame.quit()
