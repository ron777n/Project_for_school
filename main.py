"""
Sisyphus's game
TODO Add MoonBase text to speech
"""
import socket
from typing import Dict

import pygame

import client
import loader
import player
from Utils import timing
from Utils.events import event, post_event, create_event
from Utils.Pygame import Gui
from Utils.Pygame.Events import check_events
from Utils.Pygame.texting import start_typing
import leveler
import menu

# window settings
WIDTH = 1200
HEIGHT = 900

pygame.init()
fps = 60
fps_clock = pygame.time.Clock()
levels = leveler.build_levels()

world = pygame.display.set_mode((WIDTH, HEIGHT), pygame.SCALED)
pygame.display.set_caption("Sisyphus' game")
icon = pygame.image.load("sprites/icon.png")
pygame.display.set_icon(icon)
back_drop_box = world.get_rect()
back_drop = levels[0].image

events = ("player_start_move",)

for event_ in events:
    create_event(event_)


@event
def letter_typed(_letter, full_msg):
    """
    runs when someone presses a button to type
    :param full_msg: the whole message
    :param _letter: the letter that was just typed
    """
    print(f"\rtyping: {full_msg!r} ", end="")


@event("submit_text")
def submit_text_(message):
    """
    sends the message to the other clients
    :param message:
    """
    print(f"\nmsg: {message!r}")
    if not message:
        return
    # chat.add(Gui.Text(message, (255, 0, 0)))
    if main_client is not None:
        protocol = client.protocols["ChatCommand"]
        main_client.send(protocol, protocol.format_message(message, (0, 0, 0)))
    else:
        chat.add(Gui.Text(f"<{'you'}>: {message}", (255, 0, 0)))


@event
def on_message(message, color, user_id):
    user = users_data[user_id] if user_id in users_data else user_id
    msg = f"<{user}>: {message}"
    chat.add(Gui.Text(msg, (255, 0, 0)))


double_click_timer = timing.Timer(200)


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
    if window.in_menu:
        return
    if key == 27:
        window.screen = "main_menu"
    if key == pygame.K_RETURN:
        start_typing(((pygame.K_RETURN, ("submit",)), (pygame.K_ESCAPE, ("pause",))))
    double_click = double_click_timer.check(normal)
    if normal == ' ':
        main_player.jump()
    if normal == 'd':
        if double_click:
            main_player.dash(1)
        main_player.moving = 1
    if normal == 'a':
        if double_click:
            main_player.dash(-1)
        main_player.moving = -1
    double_click_timer.reset(normal)


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
def on_login_attempt(name, password):
    """
    when user clicks the login button
    """
    global main_client, user_data
    print(f"trying to log in as {name} with password: {password}")
    try:
        if main_client is None:
            main_client = client.Client()
    except socket.error:
        print("Error logging in to server server")
        return
    user_data = main_client.data
    use_protocol("Login", name, password)


users_data = {}


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
    users_data[client_id] = user_name


window = menu.GuiWindow(pygame.display.get_window_size())


def load_window(time_passage=True):
    """
    just loads the window, if True passes time
    """
    world.blit(back_drop, back_drop_box)
    # pygame.draw.rect(world, (0, 255, 0), main_player.rect)
    if time_passage:
        main_player.update()
    window.screen.draw(world)
    player_list.draw(world)  # draw player
    generic_gui.draw(world)

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


chat_box = None


server_protocols = loader.Load("protocols/server_protocol", "protocols/server_protocols")
server_protocols.load_modules()

main_client: client.Client | None = None
user_data: Dict[str, any] = {}

generic_gui = pygame.sprite.Group()

chat = Gui.ScrollableText((100, 400), (200, 300))
chat.add(Gui.Text("HELLO world", (255, 0, 0)))
generic_gui.add(chat)

player_list = pygame.sprite.Group()
main_player = player.Player(levels[0], 600, 850)
player_list.add(main_player)

# window.screen = "main_menu"
load_window(True)


running = True
while running:
    check_events(pygame.event.get())
    load_window(not window.in_menu)
