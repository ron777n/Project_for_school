"""
the class that runs the actual game or level
"""
import pygame


class Game:
    """
    the class that runs the player movement ans stuff
    """
    def __init__(self, ):
        self.display_surface = pygame.display.get_surface()

    def event_loop(self, delta_time):
        """
        handles the Game loop
        :return:
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                raise KeyboardInterrupt

    def run(self, dt):
        """
        starts the game loop
        """
        self.display_surface.fill("red")
        self.event_loop(dt)
