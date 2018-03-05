import numpy as np
import pygame as pg
import pygame.draw as draw

import random

class Animal:

    def __init__(self, surface):

        # Assign physical properties
        self.orientation = 0
        self.position = np.random.rand(2) * surface.get_size()

        self.velocity = np.array([0.5, 0], dtype='float')#np.random.rand(2) * 10 - 5
        self.maxvelovity = 1.0
        self.acceleration = np.array([0, 0, 0], dtype='float')
        self.maxacceleration = 0.1

        # Assign variables used in draw()
        self.surface = surface
        self.bodydrawsize = 6.0
        self.velocitylinelength = 1.5
        self.innercolour = np.random.rand(3) * 255
        self.outercolour = np.array([255, 255, 255])

        # Assign variables for whiskers()
        self.nwhiskers = 3
        self.visionrange = 10

        # Assign variables for eat()
        self.eatdistance = 3

    def draw(self, surface):

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
        #draw.line(surface, self.outercolour, self.position, self.position + self.velocity * self.bodydrawsize, 1)

        # Draw whiskers
        # self.whiskersangle = np.linspace(0, 2*np.pi, self.nwhiskers, endpoint=False) + self.orientation
        # self.whiskersendpoint = [self.wrap_coordinates(self.surface, self.rotate(self.position, self.position + [0, self.visionrange], angle)) for angle in self.whiskersangle]
        # for endpoint in self.whiskersendpoint:
        #     draw.line(surface, self.outercolour, self.position, endpoint, 1)

    def move(self, acceleration=None):

        if acceleration == None:
            self.acceleration = np.zeros(2)# + [0,0.01]
        else:
            self.acceleration = acceleration
        self.velocity += np.clip(self.acceleration, -self.maxacceleration, self.maxacceleration)
        self.position += np.clip(self.velocity, -self.maxvelovity, self.maxvelovity)
        self.position = self.wrap_coordinates(self.surface, self.position)
        self.acceleration *= 0

    def whiskers(self, surface):

        self.whiskersignal = np.zeros(self.nwhiskers)
        self.whiskersangle = np.linspace(0, 2*np.pi, self.nwhiskers, endpoint=False) + self.orientation
        self.whiskersendpoints = [self.rotate(self.position, self.position + [0, self.visionrange], angle) for angle in self.whiskersangle]
        for i, endpoint in enumerate(self.whiskersendpoints):
            self.whiskerpixels = self.get_line(self.position, endpoint)
            self.pixelvalues = [surface.get_at(pixel)[:-1] for pixel in self.whiskerpixels]
            self.whiskeroutput = np.sum(self.pixelvalues)
            if self.whiskeroutput > 0: 
                self.whiskeroutput = 1
            self.whiskersignal[i] = self.whiskeroutput

        return self.whiskersignal

    def eat(self, foodposition):

        self.deltaposition = np.array(foodposition - self.position)
        self.fooddistance = np.sqrt(np.sum(self.deltaposition * self.deltaposition, axis=1))
        self.noteatindex = self.fooddistance > self.eatdistance

        return self.noteatindex

    def wrap_coordinates(self, surface, coordinates):
        width, height = surface.get_size()
        x, y = coordinates

        if x >= width:
            x -= width
        elif x < 0:
            x += width

        if y >= height:
            y -= height
        elif y < 0:
            y += height 

        return np.array([x, y])

    def rotate(self, origin, point, angle):
        ox, oy = origin
        px, py = point
        qx = ox + np.cos(angle) * (px - ox) - np.sin(angle) * (py - oy)
        qy = oy + np.sin(angle) * (px - ox) + np.cos(angle) * (py - oy)

        return np.array([qx, qy])

    def get_line(self, start, end):
        x1, y1 = np.array(start, dtype='int')
        x2, y2 = np.array(end, dtype='int')
        
        steep = abs(y2 - y1) > abs(x2 - x1)
        if steep:
            x1, y1 = y1, x1
            x2, y2 =  y2, x2

        swapped = False
        if x1 > x2:
            x1, x2 = x2, x1
            y1, y2 = y2, y1
            swapped = True

        if y1 < y2:
            ystep = 1
        else:
            ystep = -1

        dx = x2 - x1
        dy = abs(y2 - y1)
        error = -dx / 2
        y = y1

        line = []
        for x in range(x1, x2 + 1):
            if steep:
                line.append((y, x))
            else:
                line.append((x, y))

            error = error + dy
            if error > 0:
                y = y + ystep
                error = error + dx

        return line[1:]













