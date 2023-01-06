"""
Main, but better
"""
import pygame
from camera import CameraGroup
import json

from Game import Game

with open("settings.json") as f:
    settings = json.load(f)


class Main:
    """
    for global variables and stuff
    """

    def __init__(self, ):
        super().__init__()
        pygame.init()
        cam_shape = tuple(settings["Screen"]["Size"])
        pygame.display.set_mode(cam_shape)
        self.display_surface = pygame.display.get_surface()
        self.clock = pygame.time.Clock()

        self.game = Game()

    def run(self):
        """
        runs the main loop.
        """
        while True:
            dt = self.clock.tick(60) / 100
            self.game.run(dt)
            pygame.display.update()


if __name__ == "__main__":
    main = Main()
    try:
        main.run()
    except KeyboardInterrupt:
        print("Good bye")
