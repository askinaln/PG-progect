import pygame
import os
import sys
import random


def load_image(name, color_key=None):
    fullname = os.path.join('data', name)
    if color_key is not None:
        image = pygame.image.load(fullname).convert()
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    else:
        image = pygame.image.load(fullname).convert_alpha()
    return image


LEVELS = {  # длина поля уровня, количество препятсвий
    1: [(1500, 4000), 10],
    2: [{1500, 6000}, 18]
}

level = 1  # input

pygame.init()
screen_size = WIDTH, HEIGHT = 1500, 700
screen = pygame.display.set_mode(screen_size)
FPS = 50

wall_image = load_image('background.jpg')
player_image = load_image('player3.png')
obstcl_images = [load_image('planet2.png'), load_image('meteor.png'), load_image('planet1.png'),
                 load_image('meteor2.png')]


class SpriteGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()

    def get_event(self, event):
        for sprite in self:
            sprite.get_event(event)


class Sprite(pygame.sprite.Sprite):
    def __init__(self, group):
        super().__init__(group)
        self.rect = None

    def get_event(self, event):
        pass


class BackGround(Sprite):  # Фон игры (космос)
    def __init__(self, size):
        super().__init__(sprite_group)
        self.image = pygame.transform.scale(wall_image, size)
        self.rect = self.image.get_rect().move(0, 700 - size[1])
        self.abs_pos = (self.rect.x, self.rect.y)

    def update(self):
        if self.rect.y < 0:
            self.rect.y += 2


class Obstacles(Sprite):  # Препятствия
    def __init__(self, image):
        super().__init__(sprite_group)
        self.image = pygame.transform.scale(image, (100, 100))
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(WIDTH - self.rect.width)
        self.rect.y = random.randrange(-200, -50)
        self.speed = random.randrange(1, 8)
        self.sdv_x = random.randrange(-2, 4)

    def update(self):
        self.rect.y += self.speed
        self.rect.x += self.sdv_x
        if self.rect.top > HEIGHT:
            self.rect.x = random.randrange(WIDTH - self.rect.width)
            self.rect.y = random.randrange(-200, -50)
            self.sdv_x = random.randrange(-2, 4)


class Player(Sprite):  # Класс игрока (космический корабль)
    def __init__(self, hero_group):
        super().__init__(hero_group)
        self.image = pygame.transform.scale(player_image, (150, 150))
        self.rect = self.image.get_rect().move(750, 550)
        self.pos = (self.rect.x, self.rect.y)

    def update(self):  # Управление игроком (космическим кораблём)
        self.speedx = 0
        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_LEFT] or keystate[pygame.K_RIGHT]:  # Право\Лево
            if keystate[pygame.K_LEFT]:
                self.speedx = -8
            if keystate[pygame.K_RIGHT]:
                self.speedx = 8
            self.rect.x += self.speedx
        else:  # Верх\Низ
            if keystate[pygame.K_UP]:
                self.speedx = -8
            if keystate[pygame.K_DOWN]:
                self.speedx = 8
            self.rect.y += self.speedx
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.top > HEIGHT:  # Если игрок остался внизу игры, то он проиграл
            pass  # Проиграл


sprite_group = SpriteGroup()
hero_group = SpriteGroup()
player = Player(hero_group)

back = BackGround(LEVELS[level][0])

for i in range(LEVELS[level][1]):  # количество препятсвий
    j = i % len(obstcl_images)
    obs = Obstacles(obstcl_images[j])  # создаём препятсвие


def terminate():
    pygame.quit()
    sys.exit()


MYEVENTTYPE = pygame.USEREVENT + 1
pygame.time.set_timer(MYEVENTTYPE, 50)

clock = pygame.time.Clock()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    hero_group.update()
    sprite_group.update()
    back.update()

    screen.fill(pygame.Color("black"))
    sprite_group.draw(screen)
    hero_group.draw(screen)
    clock.tick(FPS)
    pygame.display.flip()
pygame.quit()
