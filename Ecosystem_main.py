import numpy as np
import pygame as pg
import pygame.draw as draw

import environment, agent, food

width = 750
height = 500
 
class Ecosystem:

    def __init__(self, width, height):

        self._running = True # Parameter which keeps track of the programmes running state.
        self._display_surf = None
        self.size = self.width, self.height = width, height

        self.fps = 60        
        self.clock = pg.time.Clock()

        self.nanimals = 1
        self.nplants = 50
 
    def on_init(self):

        self._running = True

        # Switches for optional features
        self.smellon = True
 
        # Initialise the pygame display and define its surface parameters
        pg.init()
        self._display_surf = pg.display.set_mode(self.size, pg.HWSURFACE | pg.DOUBLEBUF)

        # Add animals to the ecosystem
        self.animals = np.array([agent.Agent(self._display_surf) for _ in range(self.nanimals)])

        # Add plants to the environment
        self.environment = environment.Environment(self._display_surf, n_plants=self.nplants, smell_on=True)

    def on_event(self, event):

        if event.type == pg.QUIT:

            self._running = False

    def on_loop(self):

        # AGENTS
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
            animal.move(timestep=self.dt, acceleration=self.nnoutput)

            # Reactions
            self.keepindex = animal.eat(self.environment.plant_positions)
            self.if_plants_remove = self.environment.plants_remove(self.keepindex)
            if self.if_plants_remove:
                self.environment.plants_replenish()
                animal.health += np.sum(self.keepindex == False)

        pass

    def on_render(self):

        self._display_surf.fill((0,0,0))
        
        self.environment.draw(self._display_surf)

        for animal in self.animals:

           animal.draw(self._display_surf)
        
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