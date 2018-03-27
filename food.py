import numpy as np
import pygame as pg
import pygame.draw as draw

import random

class Plant:

    def __init__(self, surface):

        # Randomly place the plant
        self.position = np.random.rand(2) * surface.get_size()

        # etc..
        self.colour_inner = (176, 244, 66)
        self.colour_outer = (102, 147, 28)

        self.size = 3

    def draw(self,surface):

        draw.circle(surface, self.colour_inner, [int(self.position[0]), int(self.position[1])], 1)
        draw.circle(surface, self.colour_outer, [int(self.position[0]), int(self.position[1])], self.size)
