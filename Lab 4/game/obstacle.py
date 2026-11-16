import pygame


class Obstacle:
    def __init__(self, x, ground_y, speed, width=25, height=40):
        self.x = float(x)
        self.previous_x = float(x)
        self.width = width
        self.height = height
        self.y = ground_y - height
        self.speed = float(speed)
        self.scored = False

    def move(self):
        self.previous_x = self.x
        self.x -= self.speed

    def off_screen(self):
        return self.x + self.width < 0

    def rect_at_x(self, x):
        return pygame.Rect(
            int(x),
            int(self.y),
            self.width,
            self.height
        )

    def rect(self):
        return self.rect_at_x(self.x)
