"""
this is the main project for computer science
submitters:
Sisyphus
Daniel M
Roey ben dor
"""
"""
This is for a player
"""

import pygame
import sys
from pygame.math import Vector2
from leveler import build_levels


WIDTH = 1200
HEIGHT = 900
ACC = 0.3
FRIC = -0.10


class Background(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.bgimage = pygame.image.load("level_images/1.png")
        self.bgY = 0
        self.bgX = 0

    def render(self):
        world.blit(self.bgimage, (self.bgX, self.bgY))


class Ground(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((WIDTH, HEIGHT//100*10), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(350, HEIGHT/100*96))

    def render(self):
        world.blit(self.image, (self.rect.x, self.rect.y))


class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()


class Player(pygame.sprite.Sprite):
    """
    Spawn a player
    """

    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("sprites/base_player.png")
        self.rect = self.image.get_rect()

        # Position and direction
        self.vx = 0
        self.pos = Vector2((340, 240))
        self.vel = Vector2(0, 0)
        self.direction = "RIGHT"
        self.acc = Vector2(0, 0)
        self.jumping = False

    def move(self):
        # Keep a constant acceleration of 0.5 in the downwards direction (gravity)
        self.acc = Vector2(0, 0.5)
        hits = pygame.sprite.spritecollide(player, blocks, False)
        if hits:
            for hit in hits:
                if self.pos.y < hit.rect.bottom:
                    pass

        # Will set running to False if the player has slowed down to a certain extent
        if abs(self.vel.x) > 0.3:
            self.running = True
        else:
            self.running = False

        # Returns the current key presses
        pressed_keys = pygame.key.get_pressed()

        # Accelerates the player in the direction of the key press
        if pressed_keys[pygame.K_LEFT]:
            self.acc.x = -ACC
        if pressed_keys[pygame.K_RIGHT]:
            self.acc.x = ACC

        # Formulas to calculate velocity while accounting for friction
        self.acc.x += self.vel.x * FRIC
        self.vel += self.acc
        self.pos += self.vel + 0.5 * self.acc  # Updates Position with new values

        # This causes character warping from one point of the screen to the other
        if self.pos.x > WIDTH:
            self.pos.x = WIDTH
        if self.pos.x < 0:
            self.pos.x = 0

        self.rect.midbottom = self.pos

    def gravity_check(self):
        hits = pygame.sprite.spritecollide(player, blocks, False)
        if self.vel.y > 0:
            if hits:
                lowest = hits[0]
                if self.pos.y < lowest.rect.bottom:
                    self.pos.y = lowest.rect.top + 1
                    self.vel.y = 0
                    self.jumping = False

    def jump(self):
        self.rect.x += 1

        # Check to see if payer is in contact with the ground
        hits = pygame.sprite.spritecollide(self, blocks, False)

        self.rect.x -= 1

        # If touching the ground, and not currently jumping, cause the player to jump.
        if hits and not self.jumping:
            self.jumping = True
            self.vel.y = -12


pygame.init()
fps = 60
fps_clock = pygame.time.Clock()
levels = build_levels()

world = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Game")
back_drop_box = world.get_rect()
back_drop = levels[0].get_image()
blocks: pygame.sprite.Group = levels[0].get_line_group()

background = Background()
ground = Ground()
ground_group = pygame.sprite.Group()
ground_group.add(ground)

player = Player()  # spawn player
player.rect.x = 0  # go to x
player.rect.y = 0  # go to y
player_list = pygame.sprite.Group()
player_list.add(player)

running = True
while running:
    player.gravity_check()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            try:
                sys.exit()
            finally:
                running = False
        if event.type == pygame.KEYDOWN:
            if event.key == ord('q'):
                pygame.quit()
                try:
                    sys.exit()
                finally:
                    running = False
            if event.key == pygame.K_SPACE:
                player.jump()

    world.blit(back_drop, back_drop_box)
    player_list.draw(world)  # draw player
    player.move()
    pygame.display.flip()
    fps_clock.tick(fps)
