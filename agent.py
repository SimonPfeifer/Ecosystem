import numpy as np
import pygame as pg
import pygame.draw as draw

import neuralnet

class Agent:

    def __init__(self, surface, smell_on=False):

        # Assign physical properties
        self.health = 1

        self.orientation = 0
        self.position = np.random.rand(2) * surface.get_size()

        self.velocity = np.array([0.0, 0.0], dtype='float')#np.random.rand(2) * 10 - 5
        self.velocity_max = 0.1

        self.acceleration = np.array([0, 0], dtype='float')
        self.acceleration_max = 0.001

        # Assign variables used in draw()
        self.draw_velocity = False
        self.draw_whiskers = False

        self.surface = surface
        self.body_draw_size = 6.0
        self.velocity_line_length = 1.5
        self.colour_inner = np.random.rand(3) * 255
        self.colour_outer = np.array([255, 255, 255])

        # Assign variables for whiskers()
        self.whiskers_on = True
        self.n_whiskers = 5
        self.vision_range = 30

        # Assign variables for smell()
        self.smell_on = smell_on
        self.smell_memory_length = 5
        self.smell_memory = range(self.smell_memory_length)

        # Assign variables for eat()
        self.eat_range = 3

        # Assign a neural net as a brain
        self.nn_input_size = 0
        if self.whiskers_on:
            self.nn_input_size += self.n_whiskers
        if self.smell_on:
            self.nn_input_size += self.smell_memory_length
        self.brain = neuralnet.NeuralNet(input_size=self.nn_input_size, output_size=9)
        self.state_previous = None
        self.action_previous = None
        self.reward_previous = 0

    def draw(self, surface):

        # Draw a triangle with animal position at the tip
        self.poly1 = self.position
        self.poly2 = [self.position[0] - 1.0 * self.body_draw_size, self.position[1] - 3.0 * self.body_draw_size]
        self.poly3 = [self.position[0] + 1.0 * self.body_draw_size, self.position[1] - 3.0 * self.body_draw_size]

        self.orientation = np.arctan2(0, 1) - np.arctan2(self.velocity[0], self.velocity[1])
        self.poly2 = self.rotate(self.poly1, self.poly2, self.orientation)
        self.poly3 = self.rotate(self.poly1, self.poly3, self.orientation)
    
        draw.polygon(surface, self.colour_inner, [self.poly1, self.poly2, self.poly3], 0)
        draw.polygon(surface, self.colour_outer, [self.poly1, self.poly2, self.poly3], 1)

        if self.draw_velocity:
            # Draw a line in the direction of the velocity vector
            draw.line(surface, self.colour_outer, self.position, self.position + self.velocity * self.body_draw_size, 1)

        # Draw whiskers
        if self.draw_whiskers:
            self.whiskers_angle = np.linspace(0, 2*np.pi, self.n_whiskers, endpoint=False) + self.orientation
            self.whisker_endpoints = [self.rotate(self.position, self.position + [0, self.vision_range], angle) for angle in self.whiskers_angle]
            for endpoint in self.whisker_endpoints:
                self.whisker_pixels = self.get_line(self.position, endpoint)
                self.whisker_pixels = [self.wrap_coordinates(surface, pixel_coord) for pixel_coord in self.whisker_pixels]
                [surface.set_at(pixel, self.colour_outer) for pixel in self.whisker_pixels]

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

        if acceleration == None:
            self.acceleration = np.zeros(2) + (np.random.rand(2) * 2 - 1)
        else:
            self.acceleration = acceleration
        self.acceleration = self.normalised(self.acceleration) * self.acceleration_max
        self.velocity += self.acceleration * timestep
        self.velocity = self.normalised(self.velocity) * self.velocity_max
        self.position += self.velocity * timestep
        self.position = self.wrap_coordinates(self.surface, self.position)
        self.acceleration *= 0

    def sense(self, surface, smell_map=None):

        self.sense_output = []
        if self.whiskers_on:
            self.sense_output += list(self.whiskers(surface))
        if self.smell_on and type(smell_map) != None:
            self.smell(smell_map)
            self.sense_output += list(self.smell_memory)

        return np.array(self.sense_output)

    def whiskers(self, surface):

        self.whisker_signal = np.zeros(self.n_whiskers)
        self.whiskers_angle = np.linspace(0, 2*np.pi, self.n_whiskers, endpoint=False) + self.orientation
        self.whiskers_endpoints = [self.rotate(self.position, self.position + [0, self.vision_range], angle) for angle in self.whiskers_angle]
        for i, endpoint in enumerate(self.whiskers_endpoints):
            self.whisker_pixels = self.get_line(self.position, endpoint)
            self.whisker_pixels = [self.wrap_coordinates(surface, pixel_coord) for pixel_coord in self.whisker_pixels]
            self.pixel_values = [surface.get_at(pixel)[:-1] for pixel in self.whisker_pixels]
            self.whisker_output = np.sum(self.pixel_values)
            if self.whisker_output > 0: 
                self.whisker_output = 1
            self.whisker_signal[i] = self.whisker_output
        self.whisker_signal.reshape((1, -1))

        return self.whisker_signal

    def smell(self, smell_map):

        self.smell_memory[1:] = self.smell_memory[:-1]
        self.smell_memory[0] = np.sum(smell_map[int(self.position[0]), int(self.position[1])])

    def eat(self, food_position):

        self.delta_position = np.array(food_position - self.position)
        self.food_distance = np.sqrt(np.sum(self.delta_position * self.delta_position, axis=1))
        self.not_eat_index = self.food_distance > self.eat_range

        return self.not_eat_index

    def normalised(self, a, axis=-1, order=2):
        '''
        Normalise a vector to unit length.
        '''
        
        l2 = np.atleast_1d(np.linalg.norm(a, order, axis))
        l2[l2==0] = 1
        normed = a / np.expand_dims(l2, axis)

        return normed[0]

    def wrap_coordinates(self, surface, coordinates):
        '''
        Translate the coordinates to opposite side of 
        if it has crossed the boundary.
        '''

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
        '''
        Rotate a point through an angle around an origin.
        '''

        ox, oy = origin
        px, py = point
        qx = ox + np.cos(angle) * (px - ox) - np.sin(angle) * (py - oy)
        qy = oy + np.sin(angle) * (px - ox) + np.cos(angle) * (py - oy)

        return np.array([qx, qy])

    def get_line(self, start, end):
        '''
        Calculate the pixel coordinates that lie between 2 points.
        '''

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
