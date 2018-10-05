import os
import errno
import numpy as np
from keras.models import Sequential
from keras.layers.core import Dense
from keras.optimizers import Adam
from keras.models import load_model

class NeuralNet:
    
    def __init__(self, input_size, output_size, model_filepath=None):

        self.input_size = input_size
        self.output_size = output_size
        self.max_memory = 1000
        self.discount = 0.9
        self.learning_rate = 0.0001
        self.epsilon = 0.1
        
        self.model = self._model_init(model_filepath)
        
        self.memory = list()
        self.batch_size = 50
        self.epoch_count = 0
        self.loss = 0

    def _model_init(self, model_filepath):

        if model_filepath == None:
            model = Sequential()
            model.add(Dense(128, input_dim=self.input_size, activation='relu'))
            model.add(Dense(128, activation='relu'))
            model.add(Dense(self.output_size, activation='linear'))
            model.compile(loss='mse', optimizer=Adam(lr=self.learning_rate))

        else:
            model = load_model(model_filepath)

        return model

    def predict(self, state):
        
        if np.random.rand() <= self.epsilon:
            action = np.random.rand(self.output_size)
            action = np.argmax(action)
        else:
            Q = self.model.predict(state.reshape((1, -1)))
            action = np.argmax(Q)

        return action

    def remember(self, experience):
        # memory[i] = [state, action, reward, state_previous]
        self.memory.append(experience)
        if len(self.memory) > self.max_memory:
            del self.memory[0]

    def get_batch(self):
            len_memory = len(self.memory)
            inputs = np.zeros((min(len_memory, self.batch_size), self.input_size))
            targets = np.zeros((inputs.shape[0], self.output_size))
            for i, idx in enumerate(np.random.randint(0, len_memory, size=inputs.shape[0])):
                state_previous, action, reward, state = self.memory[idx]

                inputs[i] = state_previous
                targets[i] = self.model.predict(state.reshape((1, -1)))[0]
                Q_max = np.max(self.model.predict(state.reshape((1, -1)))[0])
                
                # reward_t + gamma * max_a' Q(s', a')
                targets[i, action] = reward + self.discount * Q_max
            
            return inputs, targets

    def save_model(self, filepath, model_index):

        filepath = filepath + '_%03d' % model_index
        if not os.path.exists(os.path.dirname(filepath)):
            try:
                os.makedirs(os.path.dirname(filepath))
            except OSError as exc: # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise

        self.model.save(filepath)
