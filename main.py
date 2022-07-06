"""
this is the main project for computer science
submitters:
Sisyphus
Daniel M
Roey ben dor
"""
import sys

import pygame
import leveler
import player
from Utils.events import event, post_event, create_event
from Utils.Pygame.Events import check_events
import menu

# window settings
WIDTH = 1200
HEIGHT = 900

pygame.init()
fps = 60
fps_clock = pygame.time.Clock()
levels = leveler.build_levels(True)

world = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Game")
back_drop_box = world.get_rect()
back_drop = levels[0].image

buttons_list = menu.buttons_group

create_event("player_start_move")


@event("quit")  # pycharm yelled at me for calling the function quit
def exit_all():
    """
    SHUTS
    """
    global running
    pygame.quit()
    try:
        sys.exit()
    finally:
        running = False


@event
def key_down(key):
    """
    when user starts pressing a button
    :param key: ascii value of the key
    """
    if key == 100:
        main_player.moving = 1
    if key == 97:
        main_player.moving = -1
    if key == 32:
        main_player.jump()
    if key == 27:
        main_menu()


@event
def key_up(key):
    """
    when user stops pressing a button
    :param key: ascii value of the key
    """
    if key == 100 and main_player.moving == 1:
        main_player.moving = 0
    if key == 97 and main_player.moving == -1:
        main_player.moving = 0


@event
def start_game():
    """
    called when someone clicks the start game button in the main menu
    """
    global in_menu
    buttons_list.empty()
    in_menu = False


in_menu = True


def main_menu():
    """
    to start the main menu
    """
    global in_menu
    in_menu = True
    menu.start_screen((WIDTH, HEIGHT))
    while in_menu:
        check_events(pygame.event.get())

        load_window(False)


def load_window(time_passage=True):
    """
    just loads the window, if True passes time
    """
    world.blit(back_drop, back_drop_box)
    pygame.draw.rect(world, (0, 255, 0), main_player.rect)
    if time_passage:
        main_player.update()
    buttons_list.draw(world)
    player_list.draw(world)  # draw player
    pygame.display.flip()
    try:
        fps_clock.tick(fps)
    except KeyboardInterrupt:
        post_event("quit")


player_list = pygame.sprite.Group()
main_player = player.Player(levels[0], 250, 400)
main_menu()

player_list.add(main_player)
running = True
while running:
    check_events(pygame.event.get())

    load_window()
