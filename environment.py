import numpy as np
import pygame as pg
import pygame.draw as draw

import food

class Environment:

	def __init__(self, surface, n_plants=50, smell_on=True):

		self.smell_on = smell_on

		self.surface = surface
		self.n_plants = n_plants

		self.plants = np.array([food.Plant(self.surface) for _ in range(self.n_plants)])
		self.plant_positions = np.array([plant.position for plant in self.plants])


	def draw(self, surface):

		for plant in self.plants:
			plant.draw(surface)

	def plants_remove(self, keep_index):

		self.plants = self.plants[keep_index]
		self.plant_positions = self.plant_positions[keep_index]

		if keep_index.all():
			return False
			
		else:
			return True

	def plants_replenish(self):

		self.n_new_plants = self.n_plants - len(self.plants)
		self.new_plants = np.array([food.Plant(self.surface) for _ in range(self.n_new_plants)])
		self.new_plant_positions = np.array([plant.position for plant in self.new_plants])
		self.plants = np.hstack([self.plants, self.new_plants])
		self.plant_positions = np.vstack([self.plant_positions, self.new_plant_positions])

