import pygame as pg
import pygame.draw as draw

import random

class Plant:

    def __init__(self, surface):

        # Randomly place the plant
        self.position = [random.randint(0,dim) for dim in surface.get_size()]

        # etc..
        self.inner_colour = (176, 244, 66)
        self.outer_colour = (102, 147, 28)

        self.size = random.randint(1,10)

        self.draw(surface)

    def draw(self,surface):

        draw.circle(surface, self.inner_colour, self.position, self.size)
        draw.circle(surface, self.outer_colour, self.position, self.size)
