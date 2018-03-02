import numpy as np
import pygame as pg
import pygame.draw as draw

import random

class Animal:

    def __init__(self, surface):

        # Assign physical properties
        self.orientation = 0
        self.position = np.random.rand(2) * surface.get_size()

        self.velocity = np.random.rand(2) * 10 - 5
        self.maxvelovity = 10
        self.acceleration = np.array([0, 0, 0])
        self.maxacceleration = 2

        # Assign variables used in draw()
        self.bodydrawsize = 6.0
        self.velocitylinelength = 1.5
        self.innercolour = np.array([random.randint(0,255) for _ in range(3)])
        self.outercolour = np.array([255, 255, 255])

    def draw(self,surface):

        # Draw a triangle with animal position at the tip
        self.poly1 = self.position
        self.poly2 = [self.position[0] - 1.0 * self.bodydrawsize, self.position[1] - 3.0 * self.bodydrawsize]
        self.poly3 = [self.position[0] + 1.0 * self.bodydrawsize, self.position[1] - 3.0 * self.bodydrawsize]

        self.orientation = np.arctan2(0, 1) - np.arctan2(self.velocity[0], self.velocity[1])
        self.poly2 = self.rotate(self.poly1, self.poly2, self.orientation)
        self.poly3 = self.rotate(self.poly1, self.poly3, self.orientation)
  
        draw.polygon(surface, self.innercolour, [self.poly1, self.poly2, self.poly3], 0)
        draw.polygon(surface, self.outercolour, [self.poly1, self.poly2, self.poly3], 1)

        # Draw a line in the direction of the velocity vector
        draw.line(surface, self.outercolour, self.position, self.position + self.velocity * self.bodydrawsize, 1)

    def move(self, acceleration=np.random.rand(2)*2):

        if acceleration.any() == None:
            self.acceleration = np.zeros(3)
        else:
            self.acceleration = acceleration
        self.velocity += np.clip(self.acceleration, -self.maxacceleration, self.maxacceleration)
        self.position += np.clip(self.velocity, -self.maxvelovity, self.maxvelovity)
        self.acceleration *= 0

    def rotate(self, origin, point, angle):
        ox, oy = origin
        px, py = point
        qx = ox + np.cos(angle) * (px - ox) - np.sin(angle) * (py - oy)
        qy = oy + np.sin(angle) * (px - ox) + np.cos(angle) * (py - oy)

        return np.array([qx, qy])
