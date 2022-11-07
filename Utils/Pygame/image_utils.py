"""
gives utils for images
"""
import pygame
import pygame.transform as trans


def load_sheet(url, height, width, template_size):
    """
    loads a sheet of player sprites
    @param url: !url of the sheet, or name of the sprite if one of the defaults, or !b64 data
    @param height: the height of the each sprite
    @param width: the width of each sprite
    @param template_size: the size of the template that was needed
    @return: tuple of all the "stances" of the player
    """
    images: list[pygame.Surface] = []
    full_image = pygame.image.load(url)
    assert full_image.get_rect().size == template_size, "Invalid sprite sheet size"
    for i in range(0, template_size[0], height):
        small_image = pygame.Surface((height, width), pygame.SRCALPHA)
        small_image.blit(full_image, (0, 0), (i, 0, height, width))
        images.append(small_image)
    return images


def tint_image(image: pygame.Surface, color=(0, 0, 0), strength=127):
    image = image.copy()
    strength /= 255
    image.fill((color[0]*strength, color[1]*strength, color[2]*strength), None, pygame.BLEND_RGBA_ADD)
    # image.fill(color[0:3] + (0,), None, pygame.BLEND_RGBA_ADD)
    return image
