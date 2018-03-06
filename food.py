import numpy as np
import pygame as pg
import pygame.draw as draw

import random

class Plant:

    def __init__(self, surface):

        # Randomly place the plant
        self.position = np.random.rand(2) * surface.get_size()

        # etc..
        self.inner_colour = (176, 244, 66)
        self.outer_colour = (102, 147, 28)

        self.size = 3

    def draw(self,surface):

        draw.circle(surface, self.inner_colour, [int(self.position[0]), int(self.position[1])], 1)
        draw.circle(surface, self.outer_colour, [int(self.position[0]), int(self.position[1])], self.size)
