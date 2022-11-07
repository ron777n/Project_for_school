"""
everything player
"""

import pygame
import pymunk
import pymunk.pygame_util
from pygame.math import Vector2

import physics
from Utils.Pygame.image_utils import load_sheet
from camera import CameraGroup
from Good_looking.Particles import ParticleEmitter
from Good_looking.Particles.falling import RainParticle
from Utils.Pygame.targeting import Tracker
from Utils.timing import FunctionedTimer, Timer


def cycle_generator(min_size, max_size):
    """
    calling next on this will cycle up and down the numbers from 0 to max_size
    :param min_size: the minimum to start with, inclusive
    :param max_size: the max size wanted, not inclusive
    """
    i = min_size
    down = 1
    while 1:
        i += down
        if i == max_size or i == min_size:
            down *= -1
        yield i


class Player(physics.objects.Solid):
    """
    fucks
    """
    MAX_JUMPS = 2
    TIMED_DASH = 300
    DASH_COOL_DOWN = 2000
    ACCELERATION = 0.3
    RUN_SPEED = 30
    TERMINAL_VELOCITY = 200
    CHANGE_RUN_IMAGE = 200
    friction = 0.9
    elasticity = 0.5
    mass = 10

    def __init__(self, space: pymunk.Space, pos, sprite_path=r"sprites/player_sprites/arm_less.png", looking=None):
        super().__init__(mass=100, moment=100)
        self.aura = None
        self.turn = False
        self.images = load_sheet(sprite_path, 93, 103, (651, 103))
        self._image = self.images[0]
        self.rect: Tracker = Tracker(looking, self._image.get_rect(center=pos))
        self.position = pos
        self.jumps = self.MAX_JUMPS
        self.is_grounded = False
        self.bumped = False
        self.moving = 0
        self.gravity = space.gravity
        self.vel = Vector2()
        self.velocity_func = self.player_velocity_func
        self.get_run_frame = cycle_generator(4, 6)
        self.camera = None

        self._head = pygame.transform.scale(pygame.image.load(r"sprites/player_sprites/dvir_head.png"), (40, 50))
        self.head = self._head.copy()

        self.timed_dash = Timer(self.TIMED_DASH, False)
        self.dash_cool_down = Timer(self.DASH_COOL_DOWN, False)
        self.run_image = self.images[5]
        FunctionedTimer(self.CHANGE_RUN_IMAGE, self._change_run, reset=True)

        shape = pymunk.Poly.create_box(self, (self.rect.size[0] * 0.7, self.rect.size[1] * 0.7))
        shape = self.create_shape(shape)
        space.add(self, shape)

    def _change_run(self):
        self.run_image = self.images[next(self.get_run_frame)]

    @property
    def target(self):
        """
        getter: gets the rect of what the plauyer is looking at
        :return:
        """
        return self.rect.target

    @target.setter
    def target(self, value: pygame.Rect):
        """
        sets the target to be a rect
        :param value:
        :return:
        """
        self.rect.target = value

    @target.deleter
    def target(self):
        del self.rect.target

    @property
    def image(self):
        """
        gets the image by the parameters
        :return: the image
        """
        # images = ('/run1.png', '/run2.png', '/run3.png', '/idle.png',
        #           '/fall.png', '/fallen.png', '/jump.png', '/oof.png', "/bob.png")
        if self.velocity.x < -2:
            self.turn = True
        elif self.velocity.x > 2:
            self.turn = False

        running = False
        if self.moving and self.is_grounded:
            img_index = 0
            running = True
        elif self.bumped:
            img_index = 3
        elif not self.is_grounded:
            if self.velocity.y <= 1:
                img_index = 2
            else:
                img_index = 0
        else:
            img_index = 1

        if running:
            image_ = self.run_image.copy()
        else:
            image_ = self.images[img_index].copy()

        if self.turn:
            image_ = pygame.transform.flip(image_, True, False)
        head_rect = self._head.get_rect()
        body_rect = image_.get_rect()
        head_rect.centery = body_rect.top
        full_body_image = pygame.surface.Surface(
            (max(body_rect.size[0], head_rect.size[0]), body_rect.size[1] + head_rect.size[1]), pygame.SRCALPHA)
        full_body_image.blit(image_, (0, 0))
        full_body_image.blit(self.head,
                             (body_rect.centerx - head_rect.centerx, head_rect.top + head_rect.size[1] / 1.25))
        # full_body = image_.copy()
        return full_body_image

    def jump(self):
        """
        makes the player jump
        """
        # self.apply_impulse_at_local_point((0, -15*self.mass*5), (0, 0))
        if self.jumps > 0:
            self.vel.y = -70
            self.jumps -= 1

    @staticmethod
    def player_velocity_func(body: 'Player', gravity, damping, delta_time):
        """
        e
        """
        if body.timed_dash.check():
            gravity = (0, 0)
        pymunk.Body.update_velocity(body, gravity, damping, delta_time)
        vel = body.vel
        physical_vel = body.velocity
        new_vel = Vector2(vel)
        # if vel != (-1, -1) and vel != (0, -1):
        #     print(vel)
        if vel[0] == -1:
            new_vel[0] = physical_vel[0]
        if vel[1] == -1:
            new_vel[1] = physical_vel[1]
        if body.check_grounding()["body"] is not None:
            if not body.is_grounded:
                body._land()
                body.is_grounded = True
        else:
            body.is_grounded = False
        # if not body.timed_dash.check():
        #     body.vel.update(-1)
        body.vel.update(-1, -1)
        new_vel = new_vel[0], new_vel[1]
        body.velocity = new_vel
        body.angular_velocity = 0.0
        body.angle = 0

    def check_grounding(self):
        """
        checks the hit boxes to see if player is grounded
        :return:
        """
        grounding = {'normal': pymunk.Vec2d.zero(), 'penetration': 0.0, 'impulse': pymunk.Vec2d.zero(),
                     'position': pymunk.Vec2d.zero(), 'body': None, }
        gravity_unit_vector = pymunk.Vec2d(1, 0).rotated(self.space.gravity.angle)

        def f(arbiter: pymunk.Arbiter):
            """
            yes
            :param arbiter:
            """
            n = arbiter.contact_point_set.normal

            if gravity_unit_vector.y + 0.708 > n.y > gravity_unit_vector.y - 0.708 and \
                    gravity_unit_vector.x + 0.708 > n.x > gravity_unit_vector.x - 0.708:
                grounding['normal'] = n
                grounding['penetration'] = -arbiter.contact_point_set.points[0].distance
                grounding['body'] = arbiter.shapes[1].body
                grounding['impulse'] = arbiter.total_impulse
                grounding['position'] = arbiter.contact_point_set.points[0].point_b

        self.each_arbiter(f)
        return grounding

    def update(self):
        """
        i don't like missing doc strings...
        """
        # super().update()
        self.rect.center = self.position[0], self.position[1] - 20
        if self.moving and self.is_grounded:
            if self.moving == 1:
                self.vel[0] = Player.RUN_SPEED
            elif self.moving == -1:
                self.vel[0] = -Player.RUN_SPEED  # else:  #     self.vel[0] = 0
        if self.aura is not None:
            self.aura.update()
        self.direct(self.rect.angle)

    def _land(self):
        # self.vel.update()
        self.bumped = False
        self.jumps = self.MAX_JUMPS
        self.dash_cool_down.disable()
        self.timed_dash.disable()

    def dash(self, left: bool):
        """
        sets the player velocity to double of the run speed and disables gravity for a short while
        :param left: -1 if the player is dashing left else 1
        """
        if not self.dash_cool_down.check() and not self.is_grounded:
            self.vel.x = Player.RUN_SPEED * 2 * (-1 if left else 1)
            self.timed_dash.reset()
            self.dash_cool_down.reset()

    def direct(self, angle):
        """
        directs the player to the given angle
        :param angle:
        """
        if angle > 90 or angle < -90:
            self.head = pygame.transform.flip(self._head, False, True)
            self.turn = True
        elif angle < 90 or angle > -90:
            self.head = self._head.copy()
            self.turn = False
        self.head = pygame.transform.rotate(self.head, angle)

    def coolify(self):
        """
        enables particles for the player to make it look cool
        :return:
        """
        groups = self.groups()
        for group in groups:
            if isinstance(group, CameraGroup):
                break
        else:
            return
        self.camera = group
        self.aura = ParticleEmitter(RainParticle, self.rect, Timer(25), camera_group=self.camera, rand=True)
