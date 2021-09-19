from math import sqrt, log
from random import randint
from dataclasses import dataclass

import pygame

WIDTH = 600
HEIGHT = 900
PADDING = 8
SPEED = 10

BLUE = (29, 140, 246)
GREY = (100, 100, 100)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

def check_collision(obj_one, obj_two):
    return (
        sqrt((obj_one.x - obj_two.x) ** 2 + (obj_one.y - obj_two.y) ** 2)
        <= obj_one.size + obj_two.size
    )

def distance(obj_one, obj_two):
    return sqrt((obj_one.x - obj_two.x) ** 2 + (obj_one.y - obj_two.y) ** 2)

@dataclass
class Player:
    x : int = WIDTH / 2
    y : int = 8 * HEIGHT / 9
    size : int = 2 * PADDING

    def go_left(self):
        self.x = max(2 * PADDING, self.x - SPEED)

    def go_right(self):
        self.x = min(WIDTH - PADDING, self.x + SPEED)


class Obstacle:

    def __init__(self):
        self.x = randint(0, WIDTH)
        self.y = 0
        self.size = randint(20, 30)
        self.speed = randint(50, 80) / 10

    def move_down(self):
        self.y += self.speed


class Game:
    def __init__(self, human=True, display=True):

        self.done = False
        self.reward = 0
        self.action_space = 3
        self.state_space = 29

        self.player = Player()
        self.obstacles = []
        self.score = 1
        self.fps = 300
        self.add_obstacle(10)

        if display:
            self.screen = pygame.display.set_mode([WIDTH + PADDING, HEIGHT + PADDING])
            self.font = pygame.font.Font(None, 24)

    def reset(self):
        self.__init__()
        return self._get_state_vector()

    def step(self, action):
        if action == 0:
            self.player.go_left()
        elif action == 2:
            self.player.go_right()

        self.update()
        self.display()
        state_vector = self._get_state_vector()
        return state_vector, self.reward, self.done

    def _get_state_vector(self):
        state_vector = [self.player.x]
        three_nearest = []

        for obstacle in self.obstacles:
            # state_vector.append(int((obstacle.x - self.player.x) > (obstacle.size + self.player.size)))
            # state_vector.append(int((obstacle.x - self.player.x - 2 * PADDING) > obstacle.size + self.player.size))
            # state_vector.append(int((obstacle.x - self.player.x + 2 * PADDING) > obstacle.size + self.player.size))
            # state_vector.append(int((self.player.y - obstacle.y) > (obstacle.size + self.player.size)))
            if len(three_nearest) < 7:
                three_nearest.append(obstacle)

            elif any([o.y < obstacle.y for o in three_nearest]) and obstacle.y - obstacle.size < self.player.y:
                farthest = min(three_nearest, key=lambda o: o.y)
                three_nearest.remove(farthest)
                three_nearest.append(obstacle)

        for obstacle in three_nearest:
            state_vector.extend([obstacle.x, obstacle.y, distance(obstacle, self.player)])
            state_vector.append((obstacle.x - self.player.x) > (obstacle.size + self.player.size) and (self.player.y - obstacle.y) > (obstacle.size + self.player.size))

        # state_vector.append(int(self.player.x <= (2 * PADDING)))
        # state_vector.append(int(self.player.y >= (WIDTH - PADDING)))
        return state_vector


    def start(self, display=True):
        clock = pygame.time.Clock()

        while not self.done:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.done = True

            self.update()
            if display:
                self.display()

            fps = self.fps # * log(self.score) * 3 / 5
            clock.tick(fps if fps > self.fps else self.fps)

    def update(self):
        keys_pressed = pygame.key.get_pressed()
        if keys_pressed[pygame.K_LEFT]:
            self.player.go_left()

        elif keys_pressed[pygame.K_RIGHT]:
            self.player.go_right()

        self.score += 1
        original_score = self.score
        self.move_obstacles()

        flag = False
        for obstacle in self.obstacles:
            if (self.player.y - obstacle.y) < (obstacle.size + self.player.size):
                self.reward = abs(obstacle.x - self.player.x) - (obstacle.size + self.player.size)
                if self.reward < 0:
                    self.reward *= 10
                    print('Scores:', original_score, self.score)
                    print('Info:', self.reward, abs(obstacle.x - self.player.x), (obstacle.size + self.player.size))
                    print('\n')
                flag = True

        if not flag:
            self.reward = 0

    def display(self):
        if self.screen:
            self.screen.fill(WHITE)
            pygame.draw.circle(self.screen, BLUE, (self.player.x, self.player.y), self.player.size)

            for obstacle in self.obstacles:
                pygame.draw.circle(self.screen, GREY, (obstacle.x, obstacle.y), obstacle.size)

            if self.font:
                text = self.font.render(f'Score: {self.score}', False, BLACK)
                self.screen.blit(text, (10, 10))

            pygame.display.update()

    def move_obstacles(self):
        for obstacle in self.obstacles:
            obstacle.move_down()
            if check_collision(self.player, obstacle):
                self.score -= sqrt(self.score) if sqrt(self.score) > 2 else self.score
                print('ouch')
            if obstacle.y > HEIGHT:
                self.replace_obstacle(obstacle)

    def add_obstacle(self, num):
        for _ in range(num):
            self.obstacles.append(Obstacle())

    def replace_obstacle(self, old_obstacle):
        self.add_obstacle(1)
        self.obstacles.remove(old_obstacle)


if __name__ == '__main__':
    pygame.init()
    Game().start()
    pygame.quit()