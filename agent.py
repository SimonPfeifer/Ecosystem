import numpy as np
import pygame as pg
import pygame.draw as draw

import neuralnet

class Agent:

    def __init__(self, surface):

        # Assign physical properties
        self.health = 1

        self.orientation = 0
        self.position = np.random.rand(2) * surface.get_size()

        self.velocity = np.array([0.0, 0.0], dtype='float')#np.random.rand(2) * 10 - 5
        self.maxvelovity = 0.1
        self.acceleration = np.array([0, 0], dtype='float')
        self.maxacceleration = 1.0

        # Assign a neural net as a brain
        self.brain = neuralnet.NeuralNet(input_size=5, output_size=9)
        self.state_previous = None
        self.action_previous = None
        self.reward_previous = 0

        # Assign variables used in draw()
        self.whiskersdraw = False

        self.surface = surface
        self.bodydrawsize = 6.0
        self.velocitylinelength = 1.5
        self.innercolour = np.random.rand(3) * 255
        self.outercolour = np.array([255, 255, 255])

        # Assign variables for whiskers()
        self.nwhiskers = 5
        self.visionrange = 30

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
        # draw.line(surface, self.outercolour, self.position, self.position + self.velocity * self.bodydrawsize, 1)

        # Draw whiskers
        if self.whiskersdraw:
            self.whiskersangle = np.linspace(0, 2*np.pi, self.nwhiskers, endpoint=False) + self.orientation
            self.whiskersendpoint = [self.rotate(self.position, self.position + [0, self.visionrange], angle) for angle in self.whiskersangle]
            for endpoint in self.whiskersendpoint:
                self.whiskerpixels = self.get_line(self.position, endpoint)
                self.whiskerpixels = [self.wrap_coordinates(surface, pixelcoordinate) for pixelcoordinate in self.whiskerpixels]
                [surface.set_at(pixel, self.outercolour) for pixel in self.whiskerpixels]

    def action(self, action):
        '''
        Table of action values with corresponding acceleration values
        -------------------      -----------------------------------
        |  0  |  1  |  2  |      |  [-1,-1]  |  [0,-1]  |  [1,-1]  |
        -------------------      -----------------------------------
        |  3  |  4  |  5  |  ==> |  [-1, 0]  |  [0, 0]  |  [1, 0]  |
        -------------------      -----------------------------------
        |  6  |  7  |  8  |      |  [-1, 1]  |  [0, 1]  |  [1, 1]  |
        -------------------      -----------------------------------
        '''
        if action == 0:
            self.acceleration = np.array([-1,-1])
        elif action == 1:
            self.acceleration = np.array([0,-1])
        elif action == 2:
            self.acceleration = np.array([1,-1])
        elif action == 3:
            self.acceleration = np.array([-1,0])
        elif action == 4:
            self.acceleration = np.array([0,0])
        elif action == 5:
            self.acceleration = np.array([1,0])
        elif action == 6:
            self.acceleration = np.array([-1,1])
        elif action == 7:
            self.acceleration = np.array([0,1])
        elif action == 8:
            self.acceleration = np.array([1,1])        

    def move(self, timestep, acceleration=None):

        if acceleration != None:
            self.acceleration = acceleration
            
        self.velocity += self.normalised(self.acceleration) * self.maxacceleration * timestep
        self.position += self.normalised(self.velocity) * self.maxvelovity * timestep
        self.position = self.wrap_coordinates(self.surface, self.position)
        self.acceleration *= 0

    def whiskers(self, surface):

        self.whiskersignal = np.zeros(self.nwhiskers)
        self.whiskersangle = np.linspace(0, 2*np.pi, self.nwhiskers, endpoint=False) + self.orientation
        self.whiskersendpoints = [self.rotate(self.position, self.position + [0, self.visionrange], angle) for angle in self.whiskersangle]
        for i, endpoint in enumerate(self.whiskersendpoints):
            self.whiskerpixels = self.get_line(self.position, endpoint)
            self.whiskerpixels = [self.wrap_coordinates(surface, pixelcoordinate) for pixelcoordinate in self.whiskerpixels]
            self.pixelvalues = [surface.get_at(pixel)[:-1] for pixel in self.whiskerpixels]
            self.whiskeroutput = np.sum(self.pixelvalues)
            if self.whiskeroutput > 0: 
                self.whiskeroutput = 1
            self.whiskersignal[i] = self.whiskeroutput
        self.whiskersignal.reshape((1, -1))

        return self.whiskersignal

    def eat(self, foodposition):

        self.deltaposition = np.array(foodposition - self.position)
        self.fooddistance = np.sqrt(np.sum(self.deltaposition * self.deltaposition, axis=1))
        self.noteatindex = self.fooddistance > self.eatdistance

        return self.noteatindex

    def normalised(self, a, axis=-1, order=2):
        l2 = np.atleast_1d(np.linalg.norm(a, order, axis))
        l2[l2==0] = 1
        normed = a / np.expand_dims(l2, axis)

        return normed[0]

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
        dx = x2 - x1
        dy = y2 - y1

        is_steep = abs(dy) > abs (dx)

        if is_steep:
            x1, y1 = y1, x1
            x2, y2 = y2, x2

        swapped = False
        if x1 > x2:
            x1, x2 = x2, x1
            y1, y2 = y2, y1
            swapped = True

        dx = x2 - x1
        dy = y2 - y1

        error = int(dx / 2.0)
        ystep = 1 if y1 < y2 else -1

        y = y1
        line = []
        for x in range(x1, x2 + 1):
            coord = (y, x) if is_steep else (x, y)
            line.append(coord)
            error -= abs(dy)
            if error < 0:
                y += ystep
                error += dx

        if swapped:
            line.reverse()

        return line[1:]













