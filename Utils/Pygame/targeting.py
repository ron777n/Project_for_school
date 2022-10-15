"""
has two classes you could inherit from, that lets you follow a target
"""
from typing import Optional

import pygame.sprite
from pygame import Vector2


class Tracker(pygame.rect.Rect):
    """
    this object does not "follow" its target but it lets you get things like the distance between itself and its target
    or the angle
    """

    def __init__(self, target: Optional[pygame.rect.Rect] = None, *args):
        super().__init__(*args)
        self._target: Optional[pygame.rect.Rect] = target

    @property
    def target(self) -> pygame.Rect:
        """
        getter: gets the target rect
        setter: puts a target towards a rect
        """
        return self._target

    @target.setter
    def target(self, value):
        if hasattr(value, "rect"):
            self._target = value.rect
        elif isinstance(value, pygame.rect.Rect):
            self._target = value
        else:
            raise ValueError("target is not rect object or has rect object when setting target")

    @target.deleter
    def target(self):
        self._target = None

    @property
    def angle(self) -> float:
        """
        returns the angle between the self rect and the target rect
        :return:
        """
        if self.target is None:
            return 0
        diff_points = Vector2(self._target.center) - Vector2(self.center)
        return diff_points.angle_to(Vector2(0, 0))

    @property
    def distance(self) -> float:
        """
        returns the distance between the tracker and its target
        :return: float
        """
        return Vector2(self.center).distance_to(self._target.center)

    def __str__(self):
        return f"{id(self)}: {id(self._target) if self._target is not None else 'None'}"

    def __hash__(self):
        """
        need this to be hashed for the camera group.
        :return:
        """
        return hash(str(self))

    def __eq__(self, other):
        return isinstance(other, Tracker) and self.target == other.target and str(self) == str(other)

    def snap(self):
        """
        snaps itself to its target
        :return:
        """
        self.center = self._target.center


class BoundTracker(Tracker):
    """
    tracker stays inside its boundaries, if snapped
    """

    def __init__(self, boundaries, target: Optional[pygame.Rect] = None, *args):
        super().__init__(target, *args)
        self.offset = pygame.math.Vector2()
        self.boundaries = boundaries
        self.half_w = self.width / 2
        self.half_h = self.height / 2

    def snap(self):
        """
        centers the camera to an object
        """
        self.offset.x = min(self.target.centerx, self.boundaries[0] - self.half_w) - self.half_w
        self.offset.x = max(self.offset.x, 0)
        self.offset.y = min(self.target.centery, self.boundaries[1] - self.half_h) - self.half_h
        self.offset.y = max(self.offset.y, 0)
        self.topleft = tuple(self.offset)
