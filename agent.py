import random
from collections import deque

import pygame
import pygame.event
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
        self.batch_size = 64
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
        model.compile(loss='mse', optimizer=adam_v2.Adam(learning_rate=self.learning_rate))
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


def make_plot(scores):
    plt.plot([i for i in range(len(scores))], scores)

    means = []
    for i in range(len(scores)):
        if i < 5:
            part = scores[:i+1]
        else:
            part = scores[i-4:i+1]
        means.append(sum(part) / len(part))

    plt.plot([i for i in range(len(means))], means)
    plt.xlabel('episodes')
    plt.ylabel('score')


def train_dqn(env, num_episodes, scores):
    agent = DQN(env)
    max_steps = 10000

    plt.ion()
    plt.show()

    for e in range(num_episodes):
        state = env.reset()
        state = np.reshape(state, (1, env.state_space))
        net_rewards = 0

        for step_num in range(max_steps):
            action = agent.act(state)
            reward, next_state, done = env.step(action)
            net_rewards += reward
            next_state = np.reshape(next_state, (1, env.state_space))
            agent.remember(state, action, reward, next_state, done)
            state = next_state
            agent.replay()

            # print(action, next_state, reward, score, done)

            if done or step_num == max_steps - 1:
                print(f"episode: {e}/{num_episodes}, net rewards: {net_rewards}, game score: {env.score}, steps: {step_num + 1}")
                break

        scores.append(env.score)

        make_plot(scores)
        plt.draw()
        plt.pause(0.001)


if __name__ == '__main__':
    np.random.seed(0)
    pygame.init()
    pygame.event.set_blocked(None)

    env = Game(should_display=True)
    scores = []

    try:
        num_ep = 500
        train_dqn(env, num_ep, scores)
    except KeyboardInterrupt:
        pygame.quit()

        plt.ioff()
        make_plot(scores)
        plt.show()
