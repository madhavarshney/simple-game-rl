import pygame

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

class Game:

    def __init__(self, human=True):
        self.gamestate = {
            "player": player(),
            "obstacles": [],
            'over': False
        }

    def start(self, display=True):
        clock = pygame.time.Clock()
        if display:
            self.screen = pygame.display.set_mode([WIDTH + PADDING, HEIGHT + PADDING])

        while not self.gamestate['over']:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.gamestate['over'] = True

            keys_pressed = pygame.key.get_pressed()
            if keys_pressed[pygame.K_LEFT]:
                self.go_left()

            elif keys_pressed[pygame.K_RIGHT]:
                self.go_right()

            if display:
                self.display()

            clock.tick(FPS)

    def display(self):
        if self.screen:
            self.screen.fill(WHITE)
            pygame.draw.circle(self.screen, BLUE, tuple(self.gamestate['player']), PADDING*2)
            pygame.display.update()

    def go_left(self):
        self.gamestate['player'][0] = max(2*PADDING, self.gamestate['player'][0] - SPEED)

    def go_right(self):
        self.gamestate['player'][0] = min(WIDTH - PADDING, self.gamestate['player'][0] + SPEED)


if __name__ == "__main__":
    pygame.init()
    Game().start()
    pygame.quit()