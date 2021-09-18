import pygame

from random import randint

WIDTH = 600
HEIGHT = 900
PADDING = 8
SPEED = 10
FPS = 60

BLUE = (29, 140, 246)
GREY = (100, 100, 100)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

def player():
    x = WIDTH / 2
    y = 8 * HEIGHT / 9
    return [x, y]

def obstacle(factor=1):
    x = randint(0, WIDTH)
    y = 0
    size = randint(10, 20)
    speed = randint(50, 80) / 10 * factor
    return [x, y, size, speed]

class Game:

    def __init__(self, human=True):
        self.gamestate = {
            "player": player(),
            "obstacles": [],
            'over': False
        }
        self.add_obstacle(10)

    def start(self, display=True):
        clock = pygame.time.Clock()
        if display:
            self.screen = pygame.display.set_mode([WIDTH + PADDING, HEIGHT + PADDING])

        while not self.gamestate['over']:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.gamestate['over'] = True

            self.update()
            if display:
                self.display()

            clock.tick(FPS)

    def update(self):
        keys_pressed = pygame.key.get_pressed()
        if keys_pressed[pygame.K_LEFT]:
            self.go_left()

        elif keys_pressed[pygame.K_RIGHT]:
            self.go_right()

        for obstacle in self.gamestate['obstacles']:
            obstacle[1] += obstacle[3]
            if obstacle[1] > HEIGHT:
                self.replace_obstacle(obstacle)

    def display(self):
        if self.screen:
            self.screen.fill(WHITE)
            pygame.draw.circle(self.screen, BLUE, tuple(self.gamestate['player']), PADDING*2)

            for obstacle in self.gamestate['obstacles']:
                pygame.draw.circle(self.screen, GREY, tuple(obstacle[:2]), obstacle[2])
            pygame.display.update()

    def go_left(self):
        self.gamestate['player'][0] = max(2*PADDING, self.gamestate['player'][0] - SPEED)

    def go_right(self):
        self.gamestate['player'][0] = min(WIDTH - PADDING, self.gamestate['player'][0] + SPEED)

    def add_obstacle(self, num):
        for _ in range(num):
            self.gamestate['obstacles'].append(obstacle())

    def replace_obstacle(self, old_obstacle):
        self.add_obstacle(1)
        self.gamestate['obstacles'].remove(old_obstacle)


if __name__ == "__main__":
    pygame.init()
    Game().start()
    pygame.quit()