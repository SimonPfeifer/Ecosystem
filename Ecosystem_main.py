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

        # Switches for features
        self.training = True
        self.smell_on = False
 
        # Initialise the pygame display and define its surface parameters
        pg.init()
        self._display_surf = pg.display.set_mode(self.size, pg.HWSURFACE | pg.DOUBLEBUF)

        # Add animals to the ecosystem
        self.animals = np.array([agent.Agent(self._display_surf) for _ in range(self.nanimals)])

        # Add plants to the environment
        self.environment = environment.Environment(self._display_surf, n_plants=self.nplants, smell_on=self.smell_on)

        self.on_render()
        for animal in self.animals:
            animal.state_previous = animal.whiskers(self._display_surf)

    def on_event(self, event):

        if event.type == pg.QUIT:

            self._running = False

    def on_loop(self):

        if not self.training:
            for animal in self.animals:
                # AGENTS                
                # Senses
                self.state = animal.whiskers(self._display_surf)

                # Actions
                self.action = animal.brain.predict(self.state)
                animal.action(self.action)
                animal.move(timestep=self.dt)

                # Reactions
                self.reward = 0
                self.keepindex = animal.eat(self.environment.plant_positions)
                if not self.keepindex.all():
                    self.environment.plants_remove(self.keepindex)
                    self.environment.plants_replenish()
                    self.reward = np.sum(self.keepindex == False)

        if self.training:
            for animal in self.animals:
                # AGENTS
                # Order of updating should be:
                # 1. Action (e.g. move) given the state of previous loop
                # 2. Reaction (e.g. eat) receive reward given action
                # 3. Observe (e.g whiskers) receive new state given action 

                # Observe
                self.state = animal.whiskers(self._display_surf)

                # Train
                animal.brain.remember([animal.state_previous, animal.action_previous, animal.reward_previous, self.state])
                self.input_train, self.target_train = animal.brain.get_batch()
                animal.brain.loss += animal.brain.model.train_on_batch(self.input_train, self.target_train)
                animal.state_previous = self.state

                # Actions
                self.action = animal.brain.predict(animal.state_previous)
                animal.action(self.action)
                animal.move(timestep=self.dt)

                # Reactions
                self.reward = 0
                self.keepindex = animal.eat(self.environment.plant_positions)
                if not self.keepindex.all():
                    self.environment.plants_remove(self.keepindex)
                    self.environment.plants_replenish()
                    self.reward = np.sum(self.keepindex == False)

                # Store values for next interation
                animal.state_previous = self.state
                animal.action_previous = self.action
                animal.reward_previous = self.reward
                

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