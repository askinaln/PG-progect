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

wall_image = load_image('background.jpg')  # Фото заднего фона
player_image = load_image('player3.png')  # Фото игрока - космического корабля
obstcl_images = [load_image('planet2.png'), load_image('meteor.png'), load_image('planet1.png'),
                 load_image('meteor2.png')]  # Фото препятствий
bullet_image = load_image('bullet.png')  # Фото пули


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

    def update(self):  # Движение фона
        if self.rect.y < 0:
            self.rect.y += 2


class Obstacles(Sprite):  # Класс Препятствие
    def __init__(self, image):
        super().__init__(obs_group)
        self.image = pygame.transform.scale(image, (100, 100))
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(WIDTH - self.rect.width)
        self.rect.y = random.randrange(-200, -50)
        self.speed = random.randrange(1, 8)
        self.sdv_x = random.randrange(-2, 4)

    def update(self):  # Движение спрайтов
        self.rect.y += self.speed
        self.rect.x += self.sdv_x
        if self.rect.top > HEIGHT:  # Если препятствие вышло за края поля, то перемещаем его наверх
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
        if self.rect.top > HEIGHT:  # Если игрок остался снизу за полем, то он проиграл
            pass  # Проиграл

    def upbull(self):  # Функция выстрела, создание вылетающей пули
        bullet = Bullet(self.rect.centerx, self.rect.top)
        sprite_group.add(bullet)
        bull_group.add(bullet)


class Bullet(pygame.sprite.Sprite):  # Класс Пули
    def __init__(self, x, y):
        super().__init__(bull_group)
        self.image = pygame.transform.scale(bullet_image, (40, 40))
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speedy = -10

    def update(self):
        self.rect.y += self.speedy
        if self.rect.bottom < 0:  # Если пуля вышла за края поля, убираем её
            self.kill()


sprite_group = SpriteGroup()
obs_group = SpriteGroup()
hero_group = SpriteGroup()
bull_group = SpriteGroup()

player = Player(hero_group)  # Создаём игрока - космический корабль
back = BackGround(LEVELS[level][0])  # Создаём фон - звездное небо

for i in range(LEVELS[level][1]):  # Создаем нуэное количество препятствий
    j = i % len(obstcl_images)
    obs = Obstacles(obstcl_images[j])


def terminate():
    pygame.quit()
    sys.exit()


clock = pygame.time.Clock()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:  # Нажатие на пробел - Выстрел
            if event.key == pygame.K_SPACE:
                player.upbull()

    # Обновляем все группы спрайтов
    hero_group.update()
    obs_group.update()
    back.update()
    bull_group.update()

    proverka_bullet = pygame.sprite.groupcollide(obs_group, bull_group, True,
                                                 True)  # Проверяем попала ли пуля в препятствие
    if proverka_bullet:  # Если попали, то нужно создать новые препятствия вместо удаленных
        for _ in range(len(proverka_bullet)):
            obs_group.add(Obstacles(obstcl_images[random.randrange(len(obstcl_images))]))

    if pygame.sprite.spritecollide(player, obs_group,
                                   False):  # Проверяем врезался ли наш игрок в препятсвие, если да - игра заканчивается
        pass  # проигрыш

    # Отрисовываем игру
    screen.fill(pygame.Color("black"))
    sprite_group.draw(screen)
    obs_group.draw(screen)
    hero_group.draw(screen)
    clock.tick(FPS)
    pygame.display.flip()
pygame.quit()
