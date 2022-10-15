"""
Sisyphus's game
TODO Add MoonBase text to speech
"""
from typing import Dict, Optional
import socket

import pygame

from Good_looking.Particles import ParticleEmitter
from Good_looking.Particles.falling import RainParticle
from Utils.events import event, create_event  # , post_event
from Utils.Pygame.texting import start_typing
from Utils.timing import dt, Timer
from leveler import build_levels, join_levels
from Utils.Pygame.Events import check_events
from camera import CameraGroup
from Utils.Pygame import Gui
from Utils import timing
from Utils.discord import status
import client
import loader
import player
import menu

# window settings
WIDTH = 1200
HEIGHT = 700

pygame.init()
fps = 60
levels = build_levels()
level = join_levels(levels)

pygame.display.set_mode((WIDTH, HEIGHT), pygame.SCALED)
pygame.display.set_caption("Sisyphus' game")
icon = pygame.image.load("sprites/icon.png")

pygame.display.set_icon(icon)

back_drop = level.image

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
def on_message(message, _color, user_id):
    """
    called when user sends a message
    """
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
    elif key in (pygame.K_d, pygame.K_RIGHT):
        if double_click:
            main_player.dash(1)
        main_player.moving = 1
    elif key in (pygame.K_a, pygame.K_LEFT):
        if double_click:
            main_player.dash(-1)
        main_player.moving = -1
    elif key in (pygame.K_MINUS, pygame.K_UNDERSCORE):
        camera_group.zoom /= 1.5
    elif key in (pygame.K_PLUS, pygame.K_EQUALS):
        camera_group.zoom *= 1.5
    double_click_timer.reset(normal)


@event
def key_up(_normal, _special_keys, key):
    """
    when user starts pressing a button
    :param _normal: char representing the key
    :param _special_keys: shift, ctrl, etc
    :param key: value of the key by pygame
    """
    if key in (pygame.K_d, pygame.K_RIGHT) and main_player.moving == 1:
        main_player.moving = 0
    if key in (pygame.K_a, pygame.K_LEFT) and main_player.moving == -1:
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


window = menu.GuiWindow()


def load_window(time_passage=True):
    """
    just loads the window, if True passes time
    """
    display = pygame.display.get_surface()
    pygame.draw.rect(display, (0, 255, 0), main_player.rect)
    if time_passage:
        level.step(dt[0])
    camera_group.update()
    camera_group.draw()  # draw player
    generic_gui.draw(display)
    window.screen.draw(display)
    if not discord_timer.check():
        update_discord()
        discord_timer.reset()

    pygame.display.flip()
    timing.tick(fps)


def use_protocol(protocol_name, *args, **kwargs):
    """
    uses a protocol from the server_protocols
    :param protocol_name: the name
    :param args: ...
    :param kwargs: ...
    """
    protocol = server_protocols.data["protocols"][protocol_name]
    main_client.send(protocol, protocol.format_message(*args, **kwargs))


def update_discord():
    """
    sets the discord status
    """
    status(True, round((level.shape[1] - main_player.rect.centery)/900, 2))


discord_timer = Timer(3000, True)

# multi_player things
server_protocols = loader.Load("protocols/server_protocol", "protocols/server_protocols")
server_protocols.load_modules()

main_client: Optional[client.Client] = None
user_data: Dict[str, any] = {}

# gui
generic_gui = pygame.sprite.Group()

chat = Gui.ScrollableText((100, 400), (200, 300))
# chat.add(Gui.Text("HELLO world", (255, 0, 0)))
generic_gui.add(chat)

# camera and main player
camera_group = CameraGroup(back_drop, (WIDTH, HEIGHT))
main_player = player.Player(level, (600, level.shape[1] - 120), looking=camera_group.mouse_rect)
camera_group.add(main_player)
camera_group.target = main_player
raining_effect = ParticleEmitter(RainParticle, camera_group, Timer(10), camera_group, True, 3)
camera_group.add(raining_effect)
# main_player.coolify()

window.screen = "main_menu"
load_window()

running = True
while running:
    check_events(pygame.event.get())
    load_window(not window.in_menu)
