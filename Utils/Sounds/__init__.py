"""
Sisyphus' python template.
EGG
"""
import time
import os
import random
from typing import Generator, Iterator

import pygame
from pygame import mixer

mixer.init()

mixer.music.set_volume(0.1)

background_tracks = os.listdir('data/sounds/music')


def music_gen(min_stops) -> Iterator[str]:
    """
    gives you a random music track
    """
    last_tracks = [None]
    got = None
    if len(background_tracks) < min_stops:
        min_stops = len(background_tracks) - 1
    while True:
        while got in last_tracks:
            got = random.choice(background_tracks)
        yield got
        last_tracks.append(got)
        if len(last_tracks) > min_stops:
            last_tracks.pop(0)


music_generator = music_gen(2)


def set_back_ground(track: str):
    """
    sets the background music and removes the last one if there is one
    :param track:
    """
    # if mixer.music.get_busy():
    #     mixer.music.fadeout(2000)
    track += ".mp3" if '.' not in track else ''
    print(mixer.music.get_busy())
    if mixer.music.get_busy():
        mixer.music.queue(f"data/sounds/music/{track}")
    else:
        mixer.music.load(f"data/sounds/music/{track}")
        mixer.music.play()


def main():
    """
    main function
    """
    set_back_ground(next(music_generator))
    set_back_ground(next(music_generator))
    set_back_ground(next(music_generator))
    set_back_ground(next(music_generator))

    while True:
        pass


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass

mixer.quit()
