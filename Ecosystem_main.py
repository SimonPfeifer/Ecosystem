import pygame as pg
import pygame.draw as draw

#from pygame.locals import *

import animal, plant
 
class Ecosystem:

    def __init__(self):

        self.clock = pg.time.Clock()

        self._running = True # Parameter which keeps track of the programmes running state.
        self._display_surf = None
        self.size = self.width, self.height = 750, 500

        self.n_animals = 10
        self.n_plants = 20
 
    def on_init(self):

        self._running = True

        # Initialise the pygame display and define its surface parameters
        pg.init()
        self._display_surf = pg.display.set_mode(self.size, pg.HWSURFACE | pg.DOUBLEBUF)

        # Add animals to the ecosystem
        self.animals = [animal.Animal(self._display_surf) for _ in range(self.n_animals)]

        # Add plants to the ecosystem
        self.plants = [plant.Plant(self._display_surf) for _ in range(self.n_plants)]


    def on_event(self, event):

        if event.type == pg.QUIT:

            self._running = False

    def on_loop(self):

        for animal in self.animals:

            animal.move()

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

            self.clock.tick(5)

        self.on_cleanup()
 
if __name__ == "__main__" :

    # Create instance of the programme
    theApp = Ecosystem()
    theApp.on_execute()