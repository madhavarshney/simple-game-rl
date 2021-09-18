import time
from dataclasses import dataclass, field
from math import sqrt
from random import randint

import pygame
import pygame.locals

WIDTH = 300
HEIGHT = 300
BLUE = (29, 140, 246)
GREY = (100, 100, 100)
BLACK = (0, 0, 0)


def check_circle_collision(obj_one, obj_two):
    return (
        sqrt((obj_one.x - obj_two.x) ** 2 + (obj_one.y - obj_two.y) ** 2)
        <= obj_one.size + obj_two.size
    )


@dataclass
class Player:
    x: int = WIDTH / 2
    last_x: int = WIDTH / 2
    y: int = HEIGHT - 40
    padding: int = 9
    speed: int = 14
    size: int = 15

    def go_left(self):
        self.last_x = self.x
        self.x = max(self.x - self.speed, self.padding)

    def go_right(self):
        self.last_x = self.x
        self.x = min(self.x + self.speed, WIDTH - self.padding)


@dataclass
class Obstacle:
    x: int = field(default_factory=lambda: randint(0, WIDTH))
    # y: int = field(default_factory=lambda: randint(-250, 0))
    y: int = field(default_factory=lambda: randint(-100, 100))
    # speed: int = field(default_factory=lambda: randint(50, 80) / 10)
    # size: int = field(default_factory=lambda: randint(10, 20))
    speed: int = 20
    size: int = 25
    hit: bool = False

    def move_down(self, factor=1):
        # self.y += self.speed * math.log(factor)
        self.y += self.speed


class GameState:
    def __init__(self):
        self.player = Player()
        self.obstacles = []
        self.over = False
        self.score = 0
        self.num_obstacles = 1
        self.start_time = time.time()

        for _ in range(self.num_obstacles):
            self.add_obstacle()

    def add_obstacle(self):
        self.obstacles.append(Obstacle())

    def update(self):
        # factor = time.time() - self.start_time
        reward = 0
        reward += 10 if abs(self.obstacles[0].x - self.player.x) < abs(self.obstacles[0].x - self.player.last_x) else -10

        for obstacle in self.obstacles:
            if check_circle_collision(obstacle, self.player):
                reward += 10
                obstacle.hit = True

        # if any([check_circle_collision(obstacle, self.player) for obstacle in self.obstacles]):
            # self.score -= 3 * factor
            # reward -= 3 * factor
            # self.score -= 100
            # reward -= 100

            # if self.score < 0:
                # self.over = True
            # self.over = True

        for obstacle in self.obstacles:
            # obstacle.move_down(factor=factor)
            obstacle.move_down()

            if obstacle.y > HEIGHT:
                if not obstacle.hit:
                    reward -= abs(obstacle.x - self.player.x) / 2 + 10

                self.obstacles.remove(obstacle)
                self.add_obstacle()
                # self.over = True

        # self.score += 0.25
        # reward += 0.25
        # self.score += 1
        # reward += 1

        self.score += reward

        return reward


class GameEnv():
    def __init__(self):
        self.done = False
        self.reward = 0
        self.render = True

        if self.render:
            self.screen = pygame.display.set_mode([WIDTH, HEIGHT])
            self.font = pygame.font.Font(None, 24)

    # --- AI control ---
    # 0 move left
    # 1 do nothing
    # 2 move right

    def reset(self):
        self.state = GameState()
        return self._get_state_vector()

    def step(self, action):
        self.reward = 0
        self.done = 0

        if action == 0:
            self.state.player.go_left()
            self.reward -= 1
        elif action == 2:
            self.state.player.go_right()
            self.reward -= 1

        self.reward += self.state.update()
        self.done = self.state.over

        if self.render:
            self.screen.fill((255, 255, 255))

            text = self.font.render(f'Score: {int(self.state.score)}', False, BLACK)
            self.screen.blit(text, (10, 10))

            pygame.draw.circle(self.screen, BLUE, (self.state.player.x, self.state.player.y), self.state.player.size)

            for obstacle in self.state.obstacles:
                pygame.draw.circle(self.screen, GREY, (obstacle.x, obstacle.y), obstacle.size)

            pygame.display.update()

        return self.reward, self._get_state_vector(), self.done

    def _get_state_vector(self):
        # obstacle_values = []

        # for obstacle in self.state.obstacles:
        #     # obstacle_values.extend([obstacle.x, obstacle.y, obstacle.size])
        #     obstacle_values.extend([obstacle.x])

        return [
            1 if self.state.player.x - self.state.obstacles[0].x > 0 else
            -1 if self.state.player.x - self.state.obstacles[0].x < 0 else 0
        ]
        # return [self.state.player.x, *obstacle_values]
        # return [self.paddle.xcor()*0.01, self.ball.xcor()*0.01, self.ball.ycor()*0.01, self.ball.dx, self.ball.dy]


class Game:
    ADD_OBSTACLE_EVENT = pygame.USEREVENT + 1

    def __init__(self):
        self.state = GameState()
        self.font = pygame.font.Font(None, 24)

    def run(self):
        screen = pygame.display.set_mode([WIDTH, HEIGHT])
        clock = pygame.time.Clock()

        # pygame.time.set_timer(Game.ADD_OBSTACLE_EVENT, 300)

        while not self.state.over:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.state.over = True

                # elif event.type == Game.ADD_OBSTACLE_EVENT:
                #     self.state.add_obstacle()

            keys_pressed = pygame.key.get_pressed()

            if keys_pressed[pygame.K_LEFT]:
                self.state.player.go_left()

            if keys_pressed[pygame.K_RIGHT]:
                self.state.player.go_right()

            self.state.update()

            screen.fill((255, 255, 255))

            text = self.font.render(f'Score: {int(self.state.score)}', False, BLACK)
            screen.blit(text, (10, 10))

            pygame.draw.circle(screen, BLUE, (self.state.player.x, self.state.player.y), self.state.player.size)

            for obstacle in self.state.obstacles:
                pygame.draw.circle(screen, GREY, (obstacle.x, obstacle.y), obstacle.size)

            pygame.display.flip()
            clock.tick(30)


if __name__ == '__main__':
    pygame.init()
    Game().run()
    pygame.quit()

    # env = Paddle()
    # while True:
    #      env.run_frame()