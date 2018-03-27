import numpy as np
import pygame as pg
import pygame.draw as draw

import random

class Agent:

    def __init__(self, surface):

        # Assign physical properties
        self.health = 1

        self.orientation = 0
        self.position = np.random.rand(2) * surface.get_size()

        self.velocity = np.array([0.0, 0.0], dtype='float')
        self.velocity_max = 0.1
        self.acceleration = np.array([0, 0, 0], dtype='float')
        self.acceleration_max = 10

        # Assign variables used in draw()
        self.draw_velocity = False
        self.draw_whiskers = False

        self.surface = surface
        self.body_draw_size = 6.0
        self.velocity_line_length = 1.5
        self.colour_inner = np.random.rand(3) * 255
        self.colour_outer = np.array([255, 255, 255])

        # Assign variables for whiskers()
        self.n_whiskers = 3
        self.vision_range = 20

        # Assign variables for eat()
        self.eat_range = 3

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
            self.whiskers_endpoint = [self.rotate(self.position, self.position + [0, self.vision_range], angle) for angle in self.whiskers_angle]
            for endpoint in self.whiskers_endpoint:
                self.whisker_pixels = self.get_line(self.position, endpoint)
                self.whisker_pixels = [self.wrap_coordinates(surface, pixel_coord) for pixel_coord in self.whisker_pixels]
                [surface.set_at(pixel, self.colour_outer) for pixel in self.whisker_pixels]

    def move(self, timestep, acceleration=None):

        if acceleration == None:
            self.acceleration = np.zeros(2) + (np.random.rand(2) * 2 - 1)
        else:
            self.acceleration = acceleration
        self.velocity += self.normalised(self.acceleration) * self.acceleration_max * timestep
        self.position += self.normalised(self.velocity) * self.velocity_max * timestep
        self.position = self.wrap_coordinates(self.surface, self.position)
        self.acceleration *= 0

    def whiskers(self, surface):

        self.whisker_signal = np.zeros(self.n_whiskers)
        self.whiskers_angle = np.linspace(0, 2*np.pi, self.n_whiskers, endpoint=False) + self.orientation
        self.whiskers_endpoints = [self.rotate(self.position, self.position + [0, self.vision_range], angle) for angle in self.whiskers_angle]
        for i, endpoint in enumerate(self.whiskers_endpoints):
            self.whisker_pixels = self.get_line(self.position, endpoint)[1:]
            self.whisker_pixels = [self.wrap_coordinates(surface, pixel_coord) for pixel_coord in self.whisker_pixels]
            self.pixel_values = [surface.get_at(pixel)[:-1] for pixel in self.whisker_pixels]
            self.whisker_output = np.sum(self.pixel_values)
            if self.whisker_output > 0: 
                self.whisker_output = 1
            self.whisker_signal[i] = self.whisker_output

        return self.whisker_signal

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

        return line













