import numpy as np
import pygame as pg
import pygame.draw as draw
import matplotlib.pyplot as plt

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
        self.training = False
        self.testing = True

        self.whiskers_on = True
        self.smell_on = False

        # Neural net diagnostics
        # General
        self.model_filepath_load = './models/testing/whiskers_15/model'
        self.counts_per_epoch = 100
        self.count = 0
        self.epoch = 0

        # Training
        self.model_filepath_save = './models/testing/whiskers_15/'
        self.epoch_train = 150

        # Testing
        self.epoch_test = 50
        self.reward_total = 0
        self.loss_array = np.zeros(self.epoch_test)
        self.actions_array = np.zeros(self.counts_per_epoch*self.epoch_test)

        # Initialise the pygame display and define its surface parameters
        pg.init()
        self._display_surf = pg.display.set_mode(self.size, pg.HWSURFACE | pg.DOUBLEBUF)

        # Add animals to the ecosystem
        self.animals = np.array([agent.Agent(self._display_surf, model_filepath=self.model_filepath_load+'_%03d'%i, whiskers_on=self.whiskers_on, smell_on=self.smell_on) for i in range(self.nanimals)])

        # Add plants to the environment
        self.environment = environment.Environment(self._display_surf, n_plants=self.nplants, smell_on=self.smell_on)

        # Initialise agents
        self.on_render()
        for animal in self.animals:
            animal.state_previous = animal.sense(self._display_surf, smell_map=self.environment.smell_map)

    def on_event(self, event):

        if event.type == pg.QUIT:

            self._running = False

    def on_loop(self):

        for animal in self.animals:
            # AGENTS
            # Order of updating should be:
            # 1. Action (e.g. move) given the state of previous loop
            # 2. Reaction (e.g. eat) receive reward given action
            # 3. Observe (e.g whiskers) receive new state given action 

            # Observe
            self.state = animal.sense(self._display_surf, smell_map=self.environment.smell_map)

            if self.training:
                # Train
                animal.brain.remember([animal.state_previous, animal.action_previous, animal.reward_previous, self.state])
                self.input_train, self.target_train = animal.brain.get_batch()
                animal.brain.loss += animal.brain.model.train_on_batch(self.input_train, self.target_train)

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
                self.reward_total += self.reward

            if self.training:
                # Store values for next interation
                animal.state_previous = self.state
                animal.action_previous = self.action
                animal.reward_previous = self.reward

            # Neural net diagnostics
            # Log quantity every loop
            if self.testing:
                self.actions_array[self.count * self.epoch] = self.action
    
            # Log quantity every epoch            
            if self.count == self.counts_per_epoch:
                self.count = 0
                if self.testing:
                    self.loss_array[self.epoch] = animal.brain.loss
                    animal.brain.loss = 0
                self.epoch += 1
            self.count += 1

            # Save neural net for each animal after number training epochs reached
            if self.training and self.epoch == self.epoch_train:
                for i, animal in enumerate(self.animals):
                    animal.brain.save_model(filepath=self.model_filepath_save, model_index=i)
                self._running = False

                plt.plot(range(len(self.loss_array)), self.loss_array)
                plt.yscale('log')
                plt.ylabel('Loss')
                plt.savefig(self.model_filepath_save + 'loss_over_epochs.png')

            # Output basic test results after number of test epochs reached and then quit
            if self.testing and self.epoch == self.epoch_test:
                print('Total reward: ', self.reward_total)
                self._running = False


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