"""
For the objects
"""
import math

import pygame
from pygame.math import Vector2, Vector3
from typing import Optional
from Utils.Pygame.Gui import Text
import pymunk
import pymunk.pygame_util

from Utils.timing import tick, dt


class BaseObject(pygame.sprite.Sprite, pymunk.Body):
    """
    cancer
    """
    _image: Optional[pygame.Surface] = None
    emission: Optional[Vector3]
    reflectivity: Optional[float]
    temperature: Optional[float]
    melting_point: Optional[float]

    def __init__(self, **kwargs):
        super().__init__()
        pymunk.Body.__init__(self, **kwargs)
        self.rect: pygame.rect.Rect


class Solid(BaseObject):
    """
    for solids
    """
    mass: Optional[float] = None
    elasticity: Optional[float] = None
    strength: Optional[float] = None
    hardness: Optional[float] = None
    friction: Optional[float] = None
    density: Optional[float] = None
    color: Optional[tuple[int, int, int, int]] = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def update(self):
        """
        sets the image to the physical body of the object
        """
        self.image = pygame.transform.rotate(self._image, -self.rotation_vector.angle_degrees)
        if self.rect.size != (img_rect_size := self.image.get_rect().size):
            self.rect.size = Vector2(Vector2(img_rect_size) + Vector2(self.rect.size)) // 2
        self.rect.center = self.position

    @classmethod
    def create_shape(cls, shape, rect: Optional[pygame.Rect] = None):
        """
        creates a basic shape for the class.
        :param shape:
        :param rect:
        """
        if cls.color is not None:
            shape.color = cls.color
        if cls.elasticity is not None:
            shape.elasticity = cls.elasticity
        if cls.friction is not None:
            shape.friction = cls.friction
        if cls.mass is not None:
            shape.mass = cls.mass
        elif rect is not None and cls.density:
            shape.mass = Vector2(rect.size).length() * cls.density
        else:
            shape.mass = 10
        return shape


class Block(Solid):
    """
    simple Block bro
    """
    elasticity = 0.6
    strength = 1.0
    hardness = 1.0
    friction = 0.3
    density = 0.3
    _image: Optional[pygame.Surface] = pygame.image.load('sprites/objects/block.png')
    emission: Optional[Vector3] = None
    reflectivity: Optional[float] = None
    temperature: float = 10.0
    melting_point: float = 30.0
    opacity: float = 1.0

    def __init__(self, space, rect, body_type=pymunk.Body.DYNAMIC):
        super().__init__(body_type=body_type)
        self.shape = pymunk.Poly.create_box(self, size=rect.size)
        self.create_shape(self.shape, rect)
        self._image = pygame.transform.scale(self._image, rect.size)
        self.image = self._image.copy()
        self.position = rect.center
        self.rect = rect
        space.add(self, self.shape)


class Turret(Solid):
    """
    simple object that can shoot lasers and look at a point
    """
    body_image = pygame.image.load("sprites/objects/turret_body.png")
    head_image = pygame.image.load("sprites/objects/turret_head.png")

    def __init__(self, space, rect):
        super().__init__(body_type=pymunk.Body.KINEMATIC)
        self.position = rect.center
        self.shape = pymunk.Poly.create_box(self, size=rect.size)
        self.shape = self.create_shape(self.shape)
        self.rect = rect
        self.image = self.body_image.copy()
        self.turned = False

    def update(self):
        """
        sets the image to the physical body of the object
        """
        if self.rect.size != (img_rect_size := self.image.get_rect().size):
            self.rect.size = Vector2(Vector2(img_rect_size) + Vector2(self.rect.size)) // 2
        self.rect.center = self.position

    def turn_to(self, point: Vector2):
        """
        points the object towards a point
        """
        diff_points = point - Vector2(self.rect.center)
        angle = diff_points.angle_to(Vector2(0, 0))
        if diff_points.x < 0 and not self.turned:
            self.head_image = pygame.transform.flip(self.head_image, False, True)
            self.turned = True
        elif diff_points.x > 0 and self.turned:
            self.head_image = pygame.transform.flip(self.head_image, False, True)
            self.turned = False
        head = pygame.transform.rotate(self.head_image, angle)
        head_rect = head.get_rect()
        body_rect = self.body_image.get_rect()
        body_rect.top = head_rect.centery + 15
        self.image = pygame.surface.Surface((max(body_rect.size[0], head_rect.size[0]),
                                             body_rect.size[1] + head_rect.size[1]),
                                            pygame.SRCALPHA)
        self.image.blit(head, (0, 0))
        self.image.blit(self.body_image, body_rect)


class Laser(BaseObject):
    """
    object with no mass, that isn't effected by any forces only by original velocity
    """
    _image: Optional[pygame.Surface] = pygame.transform.scale(pygame.image.load("sprites/objects/Laser.png"), (50, 10))

    emission: Optional[Vector3] = (255, 0, 0)
    reflectivity: Optional[float]
    temperature: float = 1000.0
    melting_point: float = 0.0
    opacity: float = 0.5

    def __init__(self, space, start_point: Vector2, direction: Vector2, speed: int = 10, ):
        super().__init__(pymunk.Body.KINEMATIC)
        self.start_point = start_point
        self.speed = speed
        self.image = pygame.transform.rotate(self._image, direction.angle_to(Vector2(0, 0)))
        self.rect = self.image.get_rect()
        self.rect.center = start_point
        self.position = start_point
        direction.scale_to_length(speed)
        self.velocity = tuple(direction)
        shape = pymunk.Poly.create_box(self, (10, 10))
        space.add(self, shape)

    def update(self):
        self.rect.center = self.position


def main():
    """
    main function
    """
    pygame.init()
    cam_shape = 1200, 800
    screen = pygame.display.set_mode(cam_shape)
    clock = pygame.time.Clock()
    camera_group = pygame.sprite.Group()

    space = pymunk.Space()
    space.gravity = (0, 10)

    floor = Block(space, pygame.rect.Rect(25, 600, 1000, 100), pymunk.Body.STATIC)
    camera_group.add(floor)

    block1 = Block(space, pygame.rect.Rect(25, 400, 100, 100))
    block1.apply_impulse_at_local_point((1500, -1500), (0, 0))
    # block1.rotate(45)

    camera_group.add(block1)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        screen.fill("#71ddee")

        camera_group.update()
        camera_group.draw(screen)

        fps = clock.get_fps()
        fps = Text(f"{fps:.2f}FPS", (0, 0, 0))
        fps.draw(screen, ("top_left", 5, 10))

        # space.debug_draw(draw_options)

        pygame.display.update()

        tick(60)
        space.step(dt[0])


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass