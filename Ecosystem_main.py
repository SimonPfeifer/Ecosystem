import numpy as np
import pygame as pg
import pygame.draw as draw

#from pygame.locals import *

import animal, plant

width = 750
height = 500
 
class Ecosystem:

    def __init__(self, width, height):

        self.clock = pg.time.Clock()

        self._running = True # Parameter which keeps track of the programmes running state.
        self._display_surf = None
        self.size = self.width, self.height = width, height

        self.n_animals = 1
        self.n_plants = 50
 
    def on_init(self):

        self._running = True

        # Initialise the pygame display and define its surface parameters
        pg.init()
        self._display_surf = pg.display.set_mode(self.size, pg.HWSURFACE | pg.DOUBLEBUF)

        # Add animals to the ecosystem
        self.animals = np.array([animal.Animal(self._display_surf) for _ in range(self.n_animals)])

        # Add plants to the ecosystem
        self.plants = np.array([plant.Plant(self._display_surf) for _ in range(self.n_plants)])


    def on_event(self, event):

        if event.type == pg.QUIT:

            self._running = False

    def on_loop(self):

        for animal in self.animals:
            # Order of updating should be:
            # 1. Sensory (e.g. vision) which serves as input for NN
            # 2. Action (e.g. move) which is the ouput of the NN given the available information
            # 3. Reaction (e.g. eat) that follows the given output
            
            # Senses
            self.nninput = animal.whiskers(self._display_surf)
            #print(self.nninput)

            # Actions
            self.nnoutput = None
            animal.move(self.nnoutput)

            # Reactions
            self.plantposition = [plant.position for plant in self.plants]
            self.keepindex = animal.eat(self.plantposition)
            if self.keepindex.all() == False:
                self.plants = self.plants[self.keepindex]

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

            self.on_loop()
            self.on_render()

            self.clock.tick(60)

        self.on_cleanup()
 
if __name__ == "__main__" :

    # Create instance of the programme
    theApp = Ecosystem(width, height)
    theApp.on_execute()