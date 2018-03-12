import numpy as np
import pygame as pg
import pygame.draw as draw

import food

class Environment:

    def __init__(self, surface, n_plants=50, smell_on=False):

        self.smell_on = smell_on

        self.width, self.height = surface.get_size()
        self.surface = surface
        self.n_plants = n_plants

        self.plants = np.array([food.Plant(self.surface) for _ in range(self.n_plants)])
        self.plant_positions = np.array([plant.position for plant in self.plants])

        # Initialise map of smell intensity
        if self.smell_on:
            self.smellintensity = 50
            self.smellrange = 50
            self.smellcolour = 0 # 0=red, 1=green, 2=blue

            self.plantposition = [plant.position for plant in self.plants]
            self.smellmap = np.zeros([self.width, self.height, 3])
            self.xx, self.yy = np.meshgrid(np.linspace(0, self.height, self.height), np.linspace(0, self.width, self.width))
            for position in self.plantposition:
                self.smellmap[:, :, self.smellcolour] += gaussian2D([self.smellintensity, position[::-1], self.smellrange], [self.xx, self.yy])
            self.smellmap = np.clip(self.smellmap, 0, 255)


    def draw(self, surface):

        if self.smell_on:
            pg.surfarray.blit_array(surface, self.smellmap)

        for plant in self.plants:
            plant.draw(surface)

    def plants_remove(self, keep_index):

        self.plants_removed = self.plants[keep_index == False]
        self.plant_positions_removed = self.plant_positions[keep_index == False]
        self.plants = self.plants[keep_index]
        self.plant_positions = self.plant_positions[keep_index]

        if keep_index.all():
            return False

        else:
            if self.smell_on:
                for position in self.plant_positions_removed:
                    self.smellmap[:, :, self.smellcolour] -= gaussian2D([self.smellintensity, position[::-1], self.smellrange], [self.xx, self.yy])
            self.smellmap = np.clip(self.smellmap, 0, 255)

            return True

    def plants_replenish(self):

        self.n_new_plants = self.n_plants - len(self.plants)
        self.new_plants = np.array([food.Plant(self.surface) for _ in range(self.n_new_plants)])
        self.new_plant_positions = np.array([plant.position for plant in self.new_plants])
        self.plants = np.hstack([self.plants, self.new_plants])
        self.plant_positions = np.vstack([self.plant_positions, self.new_plant_positions])

        if self.smell_on:
            for position in self.new_plant_positions:
                self.smellmap[:, :, self.smellcolour] += gaussian2D([self.smellintensity, position[::-1], self.smellrange], [self.xx, self.yy])
            self.smellmap = np.clip(self.smellmap, 0, 255)


def gaussian2D(params, x):
    # Calculates value of gaussian with params = [a, [x, y], c]
    # at location x = [x, y]

    a, b, c = params
    X, Y = b
    x, y = x
    g = a * np.exp(-0.5 * ((x - X)**2 + (y - Y)**2) / c**2)

    return g