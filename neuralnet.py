import numpy as np
from keras.models import Sequential
from keras.layers.core import Dense
from keras.optimizers import Adam
from keras.models import model_from_json

class NeuralNet:
    
    def __init__(self, input_size, output_size, json_file_path=None):

        self.input_size = input_size
        self.output_size = output_size
        self.max_memory = 1000
        self.discount = 0.9
        self.learning_rate = 0.2
        self.epsilon = 0.1
        
        self.model = self._model_init(json_file_path)
        
        self.memory = list()
        self.batch_size = 50
        self.epoch_count = 0
        self.loss = 0

    def _model_init(self, json_file_path):

        if json_file_path == None:
            model = Sequential()
            model.add(Dense(128, input_dim=self.input_size, activation='relu'))
            model.add(Dense(128, activation='relu'))
            model.add(Dense(self.output_size, activation='linear'))
            model.compile(loss='mse', optimizer=Adam(lr=self.learning_rate))

        else:
            model = model_from_json(json_file_path)

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
