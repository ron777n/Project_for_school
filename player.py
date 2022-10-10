"""
everything player
"""
import pymunk

from Utils.timing import Timer, FunctionedTimer, tick, dt
from pygame.math import Vector2
import leveler
import physics
import pygame
import pymunk.pygame_util


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


def load_sheet(url):
    """
    loads a sheet of player sprites
    :param url: !url of the sheet, or name of the sprite if one of the defaults, or !b64 data
    :return: tuple of all the "stances" of the player
    """
    images: list[pygame.Surface] = []
    full_image = pygame.image.load(url)
    assert full_image.get_rect().size == (744, 103), "Invalid sprite sheet size"
    for i in range(0, 744, 93):
        small_image = pygame.Surface((93, 103), pygame.SRCALPHA)
        small_image.blit(full_image, (0, 0), (i, 0, 93, 103))
        images.append(small_image)
    return images


class PhysicalPlayer(physics.objects.Solid):
    """
    fucks
    """
    MAX_JUMPS = 2
    TIMED_DASH = 300
    DASH_COOL_DOWN = 2000
    ACCELERATION = 0.3
    FRICTION = -0.10
    RUN_SPEED = 30
    TERMINAL_VELOCITY = 200
    CHANGE_RUN_IMAGE = 200
    mass = 10

    def __init__(self, space: pymunk.Space, pos, sprite_path=r"sprites/player_sprites/dvir.png"):
        super().__init__(mass=100, moment=100)
        self.turn = False
        self.images = load_sheet(sprite_path)
        self._image = self.images[0]
        self.rect = self._image.get_rect(center=pos)
        self.position = pos
        self.jumps = self.MAX_JUMPS
        self.is_grounded = False
        self.bumped = False
        self.moving = 0
        self.gravity = space.gravity
        self.vel = Vector2()
        self.velocity_func = self.player_velocity_func
        self.get_run_frame = cycle_generator(5, 7)

        self.timed_dash = Timer(self.TIMED_DASH, False)
        self.dash_cool_down = Timer(self.DASH_COOL_DOWN, False)
        self.run_image = self.images[5]
        FunctionedTimer(self.CHANGE_RUN_IMAGE, self._change_run, reset=True)

        shape = pymunk.Poly.create_box(self, (self.rect.size[0] * 0.7, self.rect.size[1] * 0.7))
        shape.friction = 0.3
        shape.elasticity = 0.5
        shape.mass = self.mass
        space.add(self, shape)

    def _change_run(self):
        self.run_image = self.images[next(self.get_run_frame)]

    @property
    def image(self):
        """
        gets the image by the parameters
        :return: the image
        """
        # images = ('/run1.png', '/run2.png', '/run3.png', '/idle.png',
        #           '/fall.png', '/fallen.png', '/jump.png', '/oof.png', "/bob.png")
        if self.velocity.x < -1:
            self.turn = True
        elif self.velocity.x > 1:
            self.turn = False

        running = False
        if self.moving and self.is_grounded:
            img_index = 0
            running = True
        elif self.bumped:
            img_index = 4
        elif not self.is_grounded:
            if self.vel.y > 0:
                img_index = 0
            else:
                img_index = 3
        else:
            img_index = 2

        if running:
            image_ = self.run_image.copy()
        else:
            image_ = self.images[img_index].copy()

        if self.turn:
            image_ = pygame.transform.flip(image_, True, False)
        return image_

    def jump(self):
        # self.apply_impulse_at_local_point((0, -15*self.mass*5), (0, 0))
        if self.jumps > 0:
            self.vel.y = -70
            self.jumps -= 1

    @staticmethod
    def player_velocity_func(body: 'PhysicalPlayer', gravity, damping, delta_time):
        """
        e
        """
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
                body.land()
                body.is_grounded = True
        else:
            body.is_grounded = False
        if body.timed_dash.check():
            new_vel[1] = 0
        else:
            body.vel.update(-1)
        new_vel = new_vel[0], new_vel[1]
        body.velocity = new_vel
        body.angular_velocity = 0.0
        body.angle = 0

    def check_grounding(self):
        grounding = {
            'normal': pymunk.Vec2d.zero(),
            'penetration': 0.0,
            'impulse': pymunk.Vec2d.zero(),
            'position': pymunk.Vec2d.zero(),
            'body': None,
        }
        gravity_unit_vector = pymunk.Vec2d(1, 0).rotated(self.space.gravity.angle)

        def f(arbiter: pymunk.Arbiter):
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
        # super().update()
        self.rect.center = self.position[0], self.position[1] - 20
        if self.moving and self.is_grounded:
            if self.moving == 1:
                self.vel[0] = PhysicalPlayer.RUN_SPEED
            elif self.moving == -1:
                self.vel[0] = -PhysicalPlayer.RUN_SPEED
            # else:
            #     self.vel[0] = 0

    def land(self):
        # self.vel.update()
        self.bumped = False
        self.jumps = self.MAX_JUMPS
        self.dash_cool_down.disable()
        self.timed_dash.disable()

    def dash(self, left):
        if not self.dash_cool_down.check() and not self.is_grounded:
            self.vel.x = PhysicalPlayer.RUN_SPEED * 2 * left
            # self.rect.midbottom = self.position
            self.timed_dash.reset()
            self.dash_cool_down.reset()


def main():
    import camera
    import leveler
    levels = leveler.build_levels()
    level = leveler.join_levels(levels)
    pygame.init()
    camera_size = (1200, 600)
    pygame.display.set_mode(camera_size)
    main_camera = camera.CameraGroup(level.image, camera_size)
    player = PhysicalPlayer(level, (600, 500))
    draw_options = pymunk.pygame_util.DrawOptions(pygame.display.get_surface())
    main_camera.add(player)
    double_click_timer = Timer(200)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            elif event.type == pygame.KEYDOWN:
                normal = event.unicode
                if event.key == 27:
                    pygame.quit()
                    exit()
                double_click = double_click_timer.check(normal)
                if normal == ' ':
                    player.jump()
                elif event.key in (pygame.K_d, pygame.K_RIGHT):
                    if double_click:
                        player.dash(1)
                    player.moving = 1
                elif event.key in (pygame.K_a, pygame.K_LEFT):
                    if double_click:
                        player.dash(-1)
                    player.moving = -1
                elif event.key in (pygame.K_MINUS, pygame.K_UNDERSCORE):
                    main_camera.zoom /= 1.5
                elif event.key in (pygame.K_PLUS, pygame.K_EQUALS):
                    main_camera.zoom *= 1.5
                double_click_timer.reset(normal)

            elif event.type == pygame.KEYUP:
                if event.key in (pygame.K_d, pygame.K_RIGHT) and player.moving == 1:
                    player.moving = 0
                elif event.key in (pygame.K_a, pygame.K_LEFT) and player.moving == -1:
                    player.moving = 0

        player.update()
        main_camera.snap(player.rect)
        main_camera.update()
        main_camera.draw()
        # level.debug_draw(draw_options)

        pygame.display.update()
        tick(60)
        level.step(dt[0])


if __name__ == '__main__':
    main()
