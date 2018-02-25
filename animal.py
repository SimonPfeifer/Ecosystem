import pygame as pg
import pygame.draw as draw

import random

class Animal:

    def __init__(self, surface):

        self.x = random.randint(0,surface.get_width())
        self.y = random.randint(0,surface.get_height())

        self.inner_colour = [random.randint(0,255) for _ in range(3)]
        self.outer_colour = [random.randint(0,255) for _ in range(3)]

        self.draw(surface)

    def draw(self,surface):

        draw.circle(surface, self.inner_colour, [self.x,self.y], 0)
        draw.circle(surface, self.outer_colour, [self.x,self.y], 2)




