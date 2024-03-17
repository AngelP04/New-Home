import pygame

class Load_Bar:
    def __init__(self):
        self.progress = 0
        self.max_progress = 30
        self.begin = False
        self.finish = False
        self.display = False

    def get_progression(self, progression=0.4):
        self.progression = progression

    def display_bar(self):
        self.display = not self.display

    def new(self):
        self.progress = 0
        self.finish = False
        self.begin = False

    def draw(self, surface):
        if self.display:
            self.image = pygame.draw.polygon(surface, (128, 128, 128), [[515, 130], [563, 130], [540, 130 + self.progress]])
            self.bg = pygame.draw.polygon(surface, (128, 128, 128), [[515, 130], [563, 130], [540, 160]], 1)

    def update(self):
        if self.begin:
            if self.progress < self.max_progress:
                self.progress += self.progression
            else:
                self.finish = True