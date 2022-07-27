"""
this is the main project for computer science
submitters:
Sisyphus
Daniel M
Roey ben dor
TODO Add MoonBase text to speech
"""
import sys
from typing import Dict

import pygame

import client
import loader
import player
from Utils.events import event, post_event, create_event
from Utils.Pygame.Events import check_events
from Utils.Pygame.texting import start_typing, pause_typing
import leveler
import menu

# window settings
WIDTH = 1200
HEIGHT = 900

pygame.init()
fps = 60
fps_clock = pygame.time.Clock()
levels = leveler.build_levels()

world = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE | pygame.SCALED)
pygame.display.set_caption("Game")
back_drop_box = world.get_rect()
back_drop = levels[0].image

gui_widgets = menu.gui_widgets

events = ("player_start_move",)

for event_ in events:
    create_event(event_)


@event("quit")  # pycharm yelled at me for calling the function quit
def exit_all():
    """
    SHUTS
    """
    global running
    pygame.quit()
    print("exit")
    try:
        sys.exit()
    finally:
        running = False


@event
def letter_typed(_letter, full_msg):
    """
    runs when someone presses a button to type
    :param full_msg: the whole message
    :param _letter: the letter that was just typed
    """
    print(f"\rtyping: {full_msg} ", end="")


@event("submit_text")
def submit_text_(message):
    """
    sends the message to the other clients
    :param message:
    """
    print(f"\nmsg: {message!r}")


@event
def key_down(normal, _special_keys, key):
    """
    when user starts pressing a button
    :param normal: char representing the key
    :param _special_keys: shift, ctrl, etc
    :param key: value of the key by pycharm
    """
    if key == pygame.K_F11:
        pygame.display.toggle_fullscreen()
    if in_menu:
        return
    if key == 27:
        main_menu()
    if key == pygame.K_RETURN:
        start_typing(((pygame.K_RETURN, ("submit",)), (pygame.K_ESCAPE, ("pause",))))
    if normal == ' ':
        main_player.jump()
    if normal == 'd':
        main_player.moving = 1
    if normal == 'a':
        main_player.moving = -1


@event
def key_up(normal, _special_keys, _key):
    """
    when user starts pressing a button
    :param normal: char representing the key
    :param _special_keys: shift, ctrl, etc
    :param _key: value of the key by pygame
    """
    if normal == 'd' and main_player.moving == 1:
        main_player.moving = 0
    if normal == 'a' and main_player.moving == -1:
        main_player.moving = 0


@event
def start_game():
    """
    called when someone clicks the start game button in the main menu
    """
    global in_menu
    pause_typing()
    gui_widgets.empty()
    in_menu = False


@event
def on_login_attempt(name, password):
    """
    when user clicks the login button
    """
    print(f"trying to log in as {name} with password: {password}")
    use_protocol("Login", name, password)


@event
def on_login(_url, client_id, user_name):
    """
    prints if logged in
    :param _url: later add url to skins
    :param client_id: id of the client that logged in, 0 if login failed
    :param user_name: user name of the person, message of fail if login failed
    """
    if not client_id:
        print("login failed", user_name + _url)
        return
    elif client_id == user_data["ID"]:
        print(f"successfully logged in as {user_name}")
        user_data["user_name"] = user_name
    else:
        print(f"client with id({client_id}) logged in as {user_name}")


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
    # pygame.draw.rect(world, (0, 255, 0), main_player.rect)
    if time_passage:
        main_player.update()
    gui_widgets.draw(world)
    player_list.draw(world)  # draw player
    pygame.display.flip()
    try:
        fps_clock.tick(fps)
    except KeyboardInterrupt:
        post_event("quit")


def use_protocol(protocol_name, *args, **kwargs):
    """
    uses a protocol from the server_protocols
    :param protocol_name: the name
    :param args: ...
    :param kwargs: ...
    """
    protocol = server_protocols.data["protocols"][protocol_name]
    main_client.send(protocol, protocol.format_message(*args, **kwargs))


server_protocols = loader.Load("protocols/server_protocol", "protocols/server_protocols")
server_protocols.load_modules()

main_client = client.Client()
user_data: Dict[str, any] = main_client.data

player_list = pygame.sprite.Group()
main_player = player.Player(levels[0], 250, 400)
main_menu()

player_list.add(main_player)
running = True
while running:
    check_events(pygame.event.get())
    load_window()
