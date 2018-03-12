import numpy as np
import pygame as pg
import pygame.draw as draw

import food

class Environment:

	def __init__(self, surface, n_plants=50, smell_on=True):

		self.smell_on = smell_on

		self.surface = surface
		self.n_plants = n_plants

		self.plants = np.array([food.Plant(self.surface) for _ in range(self.nplants)])


	def draw(self, surface):

		for plant in self.plants:
			plant.draw()

	def plants_remove(self, keep_index):

		self.plants = self.plants[keep_index]
