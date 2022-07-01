"""
this is the main project for computer science
submitters:
Sisyphus
Daniel M
Roey ben dor
"""

import pygame
import sys
import leveler
import player

# window settings
WIDTH = 1200
HEIGHT = 900

pygame.init()
fps = 60
fps_clock = pygame.time.Clock()
levels = leveler.build_levels()

world = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Game")
back_drop_box = world.get_rect()
back_drop = levels[0].image

player_list = pygame.sprite.Group()
player = player.Player(levels[0])
player_list.add(player)

running = True
while running:
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
    player.update()
    player_list.draw(world)  # draw player
    pygame.display.flip()
    fps_clock.tick(fps)
