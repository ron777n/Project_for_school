"""
for texts
"""
from typing import List, Tuple

import pygame

from Utils.events import create_event, event, post_event

events = ("start_typing", "letter_typed", "submit_text", "pause_text")

for event_ in events:
    create_event(event_)

typing_ = False
typing_text = ""

_focus: any = None  # change this from the import in case you wanna do focus shit


def delete_letter(text, _letter):
    """
    deletes the last letter of the string
    :param text: the current text
    :param _letter: for the function to work, not used
    """
    return text[:-1]


def add_letter(text, letter):
    """
    adds a letter to the text
    :param text: the current text
    :param letter: the letter to add
    """
    return text + letter


def delete_word(text, _letter):
    """
    deletes the last word
    :param text: the text
    :param _letter: the letter
    """
    if text[-1:] == ' ':
        return text[:text[:-1].rfind(' ') + 1]
    return text[:text.rfind(' ') + 1]


key_data: List[Tuple[int, Tuple[int, callable]]] = [(0x08, (64, delete_word)), (0x08, (0, delete_letter))]


def start_typing(key_data_=None, start_text=None, focus_=None):
    """
    enables the texting
    """
    pygame.key.set_repeat(500, 50)
    if key_data_ is not None:
        key_data.extend(key_data_)
    global typing_, typing_text, _focus
    if start_text is not None:
        typing_text = start_text
    typing_ = True
    _focus = focus_


def get_text_focus():
    """
    gets the focus
    :return:
    """
    return _focus


def get_func(target_key, target_mods):
    """
    gets what function to get from the set of keys
    :param target_key: key pressed
    :param target_mods: any spacial keys pressed in that time
    """
    for key, (*mods, func) in key_data:
        if key == target_key:
            if mods:
                if not mods[0]:  # if you picked it would work without mods
                    # if not target_mods:
                    break
                else:
                    for mod in mods:
                        if not target_mods & mod:
                            break
                    else:
                        break  # shit code like this may break my bones but criticism could never hurt me
                continue
            else:
                break
    else:
        return add_letter
    return func


def pause_typing(reset=False):
    """
    pauses the typing mode
    """
    pygame.key.set_repeat(0)
    global typing_, typing_text
    key_data.clear()
    key_data.extend([(0x08, (0, delete_letter)), (0x08, (64, delete_word))])
    if reset:
        typing_text = ""
    typing_ = False


def submit_text():
    """
    calls the submit text and resets the texting values
    """
    global typing_text, typing_
    key_data.clear()
    key_data.extend([(0x08, (0, delete_letter)), (0x08, (64, delete_word))])
    post_event("submit_text", typing_text)
    pygame.key.set_repeat(0)
    typing_ = False
    typing_text = ""


@event
def base_key_down(press_down, key, mods, unicode):
    """
    gets the basic key press and types/sends it to the movement.
    :param press_down: whether it is key press or key release, True for down
    :param key: the key press id by pygame
    :param mods: special keys by pygame
    :param unicode: the key as an actual character
    :return:
    """
    global typing_text, typing_

    if press_down:
        if typing_:
            func = get_func(key, mods)
            if func == "submit":
                submit_text()
            elif func == "pause":
                pause_typing()
            elif callable(func):
                typing_text = func(typing_text, unicode)
                post_event("letter_typed", unicode, typing_text)
        else:
            post_event("key_down", unicode, mods, key)
    else:
        post_event("key_up", unicode, mods, key)


__all__ = ["start_typing", "pause_typing", "submit_text", "get_text_focus"]
