import time
import random
from collections import deque

import pygame
import numpy as np
import matplotlib.pyplot as plt

from keras import Sequential
from keras.layers import Dense
from keras.optimizers import adam_v2

from game import Game

class DQN:
    """ Implementation of deep q learning algorithm """

    def __init__(self, env):
        self.action_space = env.action_space
        self.state_space = env.state_space
        self.epsilon = 1
        self.gamma = .95
        self.batch_size = 10
        self.epsilon_min = .01
        self.epsilon_decay = .995
        # self.learning_rate = 0.001
        self.learning_rate = .0025
        self.memory = deque(maxlen=100000)
        self.model = self.build_model()

    def build_model(self):
        model = Sequential()
        model.add(Dense(64, input_shape=(self.state_space,), activation='relu'))
        model.add(Dense(64, activation='relu'))
        model.add(Dense(self.action_space, activation='linear'))
        model.compile(loss='mse', optimizer=adam_v2.Adam(lr=self.learning_rate))
        return model

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def act(self, state):
        if np.random.rand() <= self.epsilon:
            return random.randrange(self.action_space)
        act_values = self.model.predict(state)
        return np.argmax(act_values[0])

    def replay(self):
        if len(self.memory) < self.batch_size:
            return

        minibatch = random.sample(self.memory, self.batch_size)
        states = np.array([i[0] for i in minibatch])
        actions = np.array([i[1] for i in minibatch])
        rewards = np.array([i[2] for i in minibatch])
        next_states = np.array([i[3] for i in minibatch])
        dones = np.array([i[4] for i in minibatch])

        states = np.squeeze(states)
        next_states = np.squeeze(next_states)

        targets = rewards + self.gamma*(np.amax(self.model.predict_on_batch(next_states), axis=1))*(1-dones)
        targets_full = self.model.predict_on_batch(states)

        ind = np.array([i for i in range(self.batch_size)])
        targets_full[[ind], [actions]] = targets

        self.model.fit(states, targets_full, epochs=1, verbose=0)
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay


def train_dqn(env, episode):

    loss = []
    agent = DQN(env)
    max_steps = 250

    for e in range(episode):
        state = env.reset()
        state = np.reshape(state, (1, env.state_space))
        rewards = 0

        for step_num in range(max_steps):
            action = agent.act(state)
            next_state, reward, done = env.step(action)
            rewards += reward
            next_state = np.reshape(next_state, (1, env.state_space))
            agent.remember(state, action, reward, next_state, done)
            state = next_state
            agent.replay()

            # print(action, score, reward, next_state, done)
            if done or step_num == max_steps - 1:
                print(f"episode: {e}/{episode}, score: {rewards}, game score: {env.score}, time: {step_num}")
                break

        loss.append(rewards)

    return loss


if __name__ == '__main__':
    np.random.seed(0)
    pygame.init()

    env = Game()
    num_ep = 100
    loss = train_dqn(env, num_ep)

    pygame.quit()

    plt.plot([i for i in range(num_ep)], loss)
    plt.xlabel('episodes')
    plt.ylabel('reward')
    plt.show()
