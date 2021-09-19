from dataclasses import dataclass, field
from enum import Enum, IntEnum
from math import sqrt
from random import randint
from dataclasses import dataclass

import pygame

WIDTH = 300
HEIGHT = 300

BLUE = (29, 140, 246)
GREY = (180, 180, 180)
DARK_GREY = (80, 80, 80)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)


@dataclass
class Player:
    x: int = WIDTH / 2
    y: int = HEIGHT - 40
    padding: int = 9
    speed: int = 15
    size: int = 15

    def go_left(self):
        self.x = max(self.x - self.speed, self.padding)

    def go_right(self):
        self.x = min(self.x + self.speed, WIDTH - self.padding)


@dataclass
class Obstacle:
    x: int = field(default_factory=lambda: randint(0, WIDTH))
    y: int = field(default_factory=lambda: randint(-100, 0))
    speed: int = 14
    size: int = 25
    hit: bool = False

    def move_down(self):
        self.y += self.speed


class Game:
    class Mode(Enum):
        SEEK = 1
        AVOID = 2

    class Actions(IntEnum):
        LEFT = 0
        NOOP = 1
        RIGHT = 2

    def __init__(self, mode=Mode.AVOID, should_display=True):
        self.mode = mode
        self.screen = None
        self.reset()

        if should_display:
            self.screen = pygame.display.set_mode([WIDTH, HEIGHT])
            self.font = pygame.font.Font(None, 24)

    def reset(self):
        self.player = Player()
        self.obstacles = []
        self.over = False
        self.score = 0
        self.num_obstacles = 2

        self.obstacles.append(Obstacle())
        for _ in range(1, self.num_obstacles):
            self._add_obstacle()

        state_vector = self._get_state_vector()

        self.action_space = len(Game.Actions)
        self.state_space = len(state_vector)

        return state_vector

    def play(self):
        """
        Human player
        """
        clock = pygame.time.Clock()

        while not self.over:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.over = True

            keys_pressed = pygame.key.get_pressed()
            action = 0 if keys_pressed[pygame.K_LEFT] else 2 if keys_pressed[pygame.K_RIGHT] else 1

            self.step(action)
            clock.tick(15)

    def step(self, action: int):
        """
        Actions:
         0 - left
         1 - noop
         2 - right
        """
        reward = 0

        if action == Game.Actions.LEFT:
            self.player.go_left()
            reward -= 2

        elif action == Game.Actions.RIGHT:
            self.player.go_right()
            reward -= 2

        for obstacle in self.obstacles:
            if not obstacle.hit and self._check_circle_collision(obstacle, self.player):
                if self.mode == Game.Mode.SEEK:
                    reward += 200
                    self.score += 1
                    obstacle.hit = True
                elif self.mode == Game.Mode.AVOID:
                    reward -= 1000
                    self.over = True

        for obstacle in self.obstacles:
            obstacle.move_down()

            if obstacle.y > HEIGHT:
                if not obstacle.hit:
                    if self.mode == Game.Mode.SEEK:
                        reward -= 1000
                        self.over = True
                    elif self.mode == Game.Mode.AVOID:
                        reward += 200
                        self.score += 1

                self.obstacles.remove(obstacle)
                self._add_obstacle()

        if self.screen:
            self._render()

        return reward, self._get_state_vector(), self.over

    def _get_state_vector(self):
        obstacle_values = []

        for obstacle in self.obstacles:
            obstacle_values.extend([
                (self.player.x - obstacle.x) / WIDTH,
                (self.player.y - obstacle.y) / HEIGHT
            ])

        return obstacle_values

    def _render(self):
        """
        Render the game state to the screen using pygame
        """
        self.screen.fill(WHITE)

        text = self.font.render(f'Score: {int(self.score)}', False, BLACK)
        self.screen.blit(text, (10, 10))

        pygame.draw.circle(self.screen, BLUE, (self.player.x, self.player.y), self.player.size)

        for obstacle in self.obstacles:
            color = DARK_GREY if not obstacle.hit else GREY
            pygame.draw.circle(self.screen, color, (obstacle.x, obstacle.y), obstacle.size)

        pygame.display.update()

    def _add_obstacle(self):
        space = 250 if self.mode == Game.Mode.SEEK else 50
        y = min(self.obstacles[-1].y - space, 0)
        self.obstacles.append(Obstacle(y=randint(y-100, y)))

    def _check_circle_collision(self, obj_one, obj_two):
        return (
            sqrt((obj_one.x - obj_two.x) ** 2 + (obj_one.y - obj_two.y) ** 2)
            <= obj_one.size + obj_two.size
        )


if __name__ == '__main__':
    pygame.init()
    Game().play()
    pygame.quit()
