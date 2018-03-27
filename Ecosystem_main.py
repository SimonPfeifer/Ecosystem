import numpy as np
import pygame as pg
import pygame.draw as draw

#from pygame.locals import *

import agent, food

width = 750
height = 500
 
class Ecosystem:

    def __init__(self, width, height):

        self._running = True # Parameter which keeps track of the programmes running state.
        self._display_surf = None
        self.size = self.width, self.height = width, height

        self.fps = 60        
        self.clock = pg.time.Clock()

        self.n_animals = 1
        self.n_plants = 50
 
    def on_init(self):

        self._running = True

        # Switches for optional features
        self.smell_on = False

        # Initialise the pygame display and define its surface parameters
        pg.init()
        self._display_surf = pg.display.set_mode(self.size, pg.HWSURFACE | pg.DOUBLEBUF)

        # Add animals to the ecosystem
        self.animals = np.array([agent.Agent(self._display_surf) for _ in range(self.n_animals)])

        # Add plants to the ecosystem
        self.plants = np.array([food.Plant(self._display_surf) for _ in range(self.n_plants)])


    def on_event(self, event):

        if event.type == pg.QUIT:

            self._running = False

    def on_loop(self):

        # ENVIRONMENT
        # Spawn new food if total number is below n_plants
        self.n_new_plants = self.n_plants - len(self.plants)
        if self.n_new_plants > 0:
            self.new_plants = np.array([food.Plant(self._display_surf) for _ in range(self.n_new_plants)])
            self.plants = np.hstack([self.plants, self.new_plants])
        # AGENTS
        for animal in self.animals:
            # Order of updating should be:
            # 1. Sensory (e.g. vision) which serves as input for NN
            # 2. Action (e.g. move) which is the ouput of the NN given the available information
            # 3. Reaction (e.g. eat) that follows the given output
            
            # Senses
            self.nn_input = animal.whiskers(self._display_surf)
            print(self.nn_input)

            # Actions
            self.nn_output = None
            animal.move(timestep=self.dt, acceleration=self.nn_output)

            # Reactions
            self.plant_positions = [plant.position for plant in self.plants]
            self.keep_index = animal.eat(self.plant_positions)
            if self.keep_index.all() == False:
                self.plants = self.plants[self.keep_index]
                animal.health += np.sum(self.keep_index == False)

        pass

    def on_render(self):

        self._display_surf.fill((0,0,0))
        
        for animal in self.animals:

           animal.draw(self._display_surf)

        for plant in self.plants:

            plant.draw(self._display_surf)
        
        pg.display.update()

        pass

    def on_cleanup(self):

        pg.quit()
 
    def on_execute(self):

        if self.on_init() == False:
            self._running = False
 
        while( self._running ):

            for event in pg.event.get():
                self.on_event(event)

            self.dt = self.clock.tick(self.fps)
            self.on_loop()
            self.on_render()

        self.on_cleanup()

 
if __name__ == "__main__" :

    # Create instance of the programme
    theApp = Ecosystem(width, height)
    theApp.on_execute()