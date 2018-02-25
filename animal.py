import pygame as pg
import pygame.draw as draw

import random

class Animal:

    def __init__(self, surface):

        # Randomly place each of the animals
        self.position = [random.randint(0,dim) for dim in surface.get_size()]

        # Give them a random velocity
        self.velocity = [random.randrange(-2,2) for _ in range(2)]

        # etc..
        self.inner_colour = [random.randint(0,255) for _ in range(3)]
        self.outer_colour = [random.randint(0,255) for _ in range(3)]

        self.draw(surface)

    def draw(self,surface):

        draw.circle(surface, self.inner_colour, self.position, 0)
        draw.circle(surface, self.outer_colour, self.position, 2)

    def move(self):

        self.position = [self.position[comp] + self.velocity[comp] for comp in range(2)]
