"""
the basic objects
"""
from typing import Optional

import pygame
import pymunk
from pygame.math import Vector2


class BaseObject(pygame.sprite.Sprite, pymunk.Body):
    """
    cancer
    """
    _image: Optional[pygame.Surface] = None
    emission: Optional[pygame.Vector3]
    reflectivity: Optional[float]
    temperature: Optional[float]
    melting_point: Optional[float]
    mass: Optional[float] = None
    density: Optional[float] = None
    color: Optional[tuple[int, int, int, int]] = None

    def __init__(self, *args, **kwargs):
        super().__init__()
        pymunk.Body.__init__(self, **kwargs)
        self.rect: pygame.rect.Rect
        self.size: tuple[int, int] = (0, 0)

    @classmethod
    def create_shape(cls, shape, rect: Optional[pygame.Rect] = None, *args):
        """
        creates a basic shape for the class.
        :param shape:
        :param rect:
        """
        if cls.color is not None:
            shape.color = cls.color
        if cls.mass is not None:
            shape.mass = cls.mass
        elif rect is not None and cls.density:
            shape.mass = Vector2(rect.size).length() * cls.density
        else:
            shape.mass = 10
        return shape

    @property
    def image(self) -> pygame.Surface:
        if hasattr(self, "_image"):
            img = self._image
        else:
            img = pygame.surface.Surface(self.rect, pygame.SRCALPHA)
        if self.size != (0, 0):
            img = pygame.transform.scale(img, self.size)
        img = pygame.transform.rotate(img, self.image_angle)
        if self.rect.size != (img_rect_size := img.get_rect().size):
            self.rect.size = Vector2(Vector2(img_rect_size) + Vector2(self.rect.size)) // 2
        self.rect.center = self.position
        return img

    @property
    def image_angle(self):
        return -self.rotation_vector.angle_degrees


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

    @classmethod
    def create_shape(cls, shape, rect: Optional[pygame.Rect] = None, *args):
        """
        creates a basic shape for the class.
        :param shape:
        :param rect:
        """
        shape = super().create_shape(shape, rect, *args)
        if cls.elasticity is not None:
            shape.elasticity = cls.elasticity
        if cls.friction is not None:
            shape.friction = cls.friction
        return shape
