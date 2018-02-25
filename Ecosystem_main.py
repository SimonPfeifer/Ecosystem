import pygame as pg
import pygame.draw as draw

from pygame.locals import *

import animal
 
class Ecosystem:

    def __init__(self):

        self._running = True # Parameter which keeps track of the programmes running state.
        self._display_surf = None
        self.size = self.width, self.height = 750, 500
 
    def on_init(self):

        self._running = True

        # Initialise the pygame display and define its surface parameters
        pg.init()
        self._display_surf = pg.display.set_mode(self.size, pg.HWSURFACE | pg.DOUBLEBUF)

        for _ in range(10):

            animal.Animal(self._display_surf)


        # draw.ellipse(self._display_surf,(140,240,12),[round(self.width/2), round(self.height/2), 20, 40], 1)

 
    def on_event(self, event):

        if event.type == pg.QUIT:
            self._running = False

    def on_loop(self):


        pass
    def on_render(self):
        
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
        self.on_cleanup()
 
if __name__ == "__main__" :

    # Create instance of the programme
    theApp = Ecosystem()
    theApp.on_execute()