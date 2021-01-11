import pygame
import os
import sys
import random
from os import path


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


LEVELS = {  # длина поля уровня, количество препятсвий, минимальная скорость препятствия
    1: [(1500, 4000), 10, 1],
    2: [(1500, 8000), 15, 4]
}

pygame.init()
screen_size = WIDTH, HEIGHT = 1500, 700
screen = pygame.display.set_mode(screen_size)
FPS = 50

wall_image = load_image('background.jpg')  # Фото заднего фона
player_image = load_image('player3.png')  # Фото игрока - космического корабля
obstcl_images = [load_image('planet2.png'), load_image('meteor.png'), load_image('planet1.png'),
                 load_image('meteor2.png')]  # Фото препятствий
bullet_image = load_image('bullet.png')  # Фото пули
heart_image = load_image('heart.png')  # Фото сердца - жизней
fire_image = load_image("bullet.png")  # Фото частиц взрыва
vsp_image = load_image('vspishka.png')  # Фото для "обломков" при столкновении корабля

# Загружаем музыку
snd_dir = path.join(path.dirname(__file__), 'snd')
upbull_sound = pygame.mixer.Sound(path.join(snd_dir, 'vistrel.wav'))
boom_sound = pygame.mixer.Sound(path.join(snd_dir, 'boom.wav'))
gameover_sound = pygame.mixer.Sound(path.join(snd_dir, 'proigrish.wav'))
stolk_sound = pygame.mixer.Sound(path.join(snd_dir, 'stolknoven.wav'))
pobeda_sound = pygame.mixer.Sound(path.join(snd_dir, 'vinner.wav'))

allgame_music = []  # Список песен для начальной заставки (индекс 0),
# для игры (индекс 1), для конечной заставки(индекс 2)
allgame_music.append(pygame.mixer.Sound(path.join(snd_dir, 'nach.mp3')))
allgame_music.append(pygame.mixer.Sound(path.join(snd_dir, 'allgamemusic.ogg')))
allgame_music.append(pygame.mixer.Sound(path.join(snd_dir, 'over.ogg')))
pygame.mixer.music.set_volume(0.6)


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
    def __init__(self, size, speed):
        super().__init__(sprite_group)
        self.image = pygame.transform.scale(wall_image, size)
        self.rect = self.image.get_rect().move(0, 700 - size[1])
        self.abs_pos = (self.rect.x, self.rect.y)
        self.speed = speed

    def update(self):  # Движение фона
        if self.rect.y < 0:
            self.rect.y += self.speed


class Obstacles(Sprite):  # Класс Препятствие
    def __init__(self, image, speed_min):  # Изображение препятствия, минимальная его скорость
        super().__init__(obs_group)
        self.image = pygame.transform.scale(image, (100, 100))
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(WIDTH - self.rect.width)
        self.rect.y = random.randrange(-200, -50)
        self.speed = random.randrange(speed_min, 8)
        self.sdv_x = random.randrange(-2, 4)

    def update(self):  # Движение спрайтов
        self.rect.y += self.speed
        self.rect.x += self.sdv_x
        if self.rect.top > HEIGHT:  # Если препятствие вышло за края поля, то перемещаем его наверх
            self.rect.x = random.randrange(WIDTH - self.rect.width)
            self.rect.y = random.randrange(-200, -50)
            self.sdv_x = random.randrange(-2, 4)


class Player(Sprite):  # Класс игрока (космический корабль)
    def __init__(self):
        super().__init__(hero_group)
        self.image = pygame.transform.scale(player_image, (150, 150))
        self.rect = self.image.get_rect().move(750, 550)
        self.pos = (self.rect.x, self.rect.y)
        self.lives = 5
        self.points = 0

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

    def upbull(self):  # Функция выстрела, создание пули
        bullet = Bullet(self.rect.centerx, self.rect.top)
        sprite_group.add(bullet)
        bull_group.add(bullet)
        upbull_sound.play()  # звук выстрела


class Bullet(pygame.sprite.Sprite):  # Класс Пули
    def __init__(self, x, y):  # Первоначальные координаты пули
        super().__init__(bull_group)
        self.image = pygame.transform.scale(bullet_image, (40, 40))
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speedy = -10

    def update(self):  # Движение пули
        self.rect.y += self.speedy
        if self.rect.bottom < 0:  # Если пуля вышла за края поля, убираем её
            self.kill()


class Text(pygame.sprite.Sprite):  # Класс текста
    def __init__(self, font, text, x, y, color):
        super().__init__(text_group)
        self.color_copy = color
        self.font = font
        self.text = text
        self.color = color
        self.string_rendered = self.font.render(self.text, True, self.color)
        self.intro_rect = self.string_rendered.get_rect()
        self.intro_rect.y = y
        self.intro_rect.x = x
        self.sit = True

    def update(self):  # Обработка изменения цвета текста при наведении на него мыши
        if not self.sit:
            self.color = pygame.Color('#FF3333')
        else:
            self.color = self.color_copy
        self.string_rendered = self.font.render(self.text, True, self.color)


class Live(pygame.sprite.Sprite):  # Класс Пули
    def __init__(self, x, y):  # Первоначальные координаты пули
        super().__init__(hearts_group)
        self.image = pygame.transform.scale(heart_image, (60, 60))
        self.rect = self.image.get_rect()
        self.rect.y = y
        self.rect.x = x


class Particle(pygame.sprite.Sprite):
    def __init__(self, pos, dx, dy, image):
        super().__init__(prt_group)

        self.fire = [image]
        for scale in (5, 10, 15):
            self.fire.append(pygame.transform.scale(self.fire[0], (scale, scale)))

        self.image = random.choice(self.fire)
        self.rect = self.image.get_rect()

        self.velocity = [dx, dy]
        self.rect.x, self.rect.y = pos

        self.gravity = 1

    def update(self):
        self.velocity[1] += self.gravity
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]
        if not self.rect.colliderect((0, 0, WIDTH, HEIGHT)):
            self.kill()


def create_particles(position, image):
    # количество создаваемых частиц
    particle_count = 20
    # возможные скорости
    numbers = range(-5, 6)
    for _ in range(particle_count):
        Particle(position, random.choice(numbers), random.choice(numbers), image)


def start_screen():  # Главный экран
    intro_text = ["GALAXY GAME", "",
                  "",
                  "Easy level", "",
                  "",
                  'Advanced level', '',
                  '',
                  'Exit']

    fon = pygame.transform.scale(load_image('splashscreen.jpg'), screen_size)
    screen.blit(fon, (0, 0))
    font = pygame.font.SysFont('Snap ITC', 48)
    y = 200
    x = 500
    lines = []
    for line in intro_text:
        line1 = Text(font, line, x, y, pygame.Color('white'))
        screen.blit(line1.string_rendered, line1.intro_rect)
        x += 2
        line2 = Text(font, line, x, y, pygame.Color('#000033'))
        screen.blit(line2.string_rendered, line2.intro_rect)
        if line == intro_text[0]:
            x += 40
        y += 40
        lines.append(line1)
        lines.append(line2)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.MOUSEMOTION:  # Если пошевелили мышью
                for rect in lines:
                    if rect.text != intro_text[0] and rect.color != pygame.Color('white'):  # Если навели на текст,
                        # на который можем нажать, меняем цвет этого текста
                        if rect.intro_rect.left <= event.pos[0] <= rect.intro_rect.right and \
                                rect.intro_rect.top <= event.pos[1] <= rect.intro_rect.bottom:
                            rect.sit = False
                        else:
                            rect.sit = True
            elif event.type == pygame.MOUSEBUTTONDOWN:  # Нажатие мышью
                for rect in lines:
                    if rect.text != intro_text[0] and rect.color != pygame.Color('white'):
                        if rect.intro_rect.left <= event.pos[0] <= rect.intro_rect.right and \
                                rect.intro_rect.top <= event.pos[1] <= rect.intro_rect.bottom:  # В соотвествии
                            # с нажатым текстом, определяем уровень игрока
                            if rect.text == 'Easy level':
                                return 1
                            elif rect.text == 'Advanced level':
                                return 2
                            elif rect.text == 'Exit':
                                pygame.quit()
        screen.blit(fon, (0, 0))
        for rect in lines:
            rect.update()
            screen.blit(rect.string_rendered, rect.intro_rect)
        pygame.display.flip()
        clock.tick(FPS)


def gameover_screen(points, text):  # Экран окончания игры -> Нужно вывести количество набранных за игру очков и
    # текст прошел или не прошел игрок уровень
    intro_text = ['GAME OVER', "",
                  "",
                  text, '',
                  '',
                  f"POINTS: {points}", "",
                  "",
                  "Start over", "",
                  "",
                  'Go back to the main page', "",
                  "",
                  'Exit']

    fon = pygame.transform.scale(load_image('splashscreen.jpg'), screen_size)
    screen.blit(fon, (0, 0))
    font = pygame.font.SysFont('Snap ITC', 48)
    y = 100
    x = 600
    lines = []
    for line in intro_text:  # Создаем и выводим нужный текст
        line1 = Text(font, line, x, y, pygame.Color('white'))
        screen.blit(line1.string_rendered, line1.intro_rect)
        x += 2
        line2 = Text(font, line, x, y, pygame.Color('#000033'))
        screen.blit(line2.string_rendered, line2.intro_rect)
        if line == intro_text[0]:
            x -= 150
        y += 40
        lines.append(line1)
        lines.append(line2)

    runn = True
    while runn:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            elif event.type == pygame.MOUSEMOTION:
                for rect in lines:
                    if rect.text not in intro_text[:9] and rect.color != pygame.Color(
                            'white'):  # Если навели на текст,
                        # на который можем нажать, меняем цвет этого текста
                        if rect.intro_rect.left <= event.pos[0] <= rect.intro_rect.right and \
                                rect.intro_rect.top <= event.pos[1] <= rect.intro_rect.bottom:
                            rect.sit = False
                        else:
                            rect.sit = True
            elif event.type == pygame.MOUSEBUTTONDOWN:  # В соотвествии
                # с нажатым текстом, определяем дальнейшие действия игры
                for rect in lines:
                    if rect.text not in intro_text[:9] and rect.color != pygame.Color('white'):
                        if rect.intro_rect.left <= event.pos[0] <= rect.intro_rect.right and \
                                rect.intro_rect.top <= event.pos[1] <= rect.intro_rect.bottom:
                            if rect.text == 'Start over':
                                runn = False
                            elif rect.text == 'Go back to the main page':
                                return 'new'
                            elif rect.text == 'Exit':
                                terminate()
        screen.blit(fon, (0, 0))
        for rect in lines:
            rect.update()
            screen.blit(rect.string_rendered, rect.intro_rect)
        pygame.display.flip()
        clock.tick(FPS)


def terminate():
    pygame.quit()
    sys.exit()


clock = pygame.time.Clock()

pause = False
screen_need = True  # Переменная указывающая нужен ли выбор уровня
game_over = True  # Переменная о состоянии игры, если игрок умер нужно обновляться

running = True
while running:
    if game_over:  # Если игра только началась/перезапускается обновляем все элементы игры
        allgame_music[2].stop()  # Останавливаем музыку конца игры
        allgame_music[0].play(loops=-1)  # Включаем музыку главного экрана

        sprite_group = SpriteGroup()
        text_group = SpriteGroup()
        obs_group = SpriteGroup()
        hero_group = SpriteGroup()
        bull_group = SpriteGroup()
        hearts_group = SpriteGroup()
        prt_group = SpriteGroup()

        if screen_need:  # Если игрок снова выбирает уровень
            level = start_screen()
            screen_need = False

        player = Player()  # Создаём игрока - космический корабль
        back = BackGround(LEVELS[level][0], LEVELS[level][2])  # Создаём фон - звездное небо

        font = pygame.font.SysFont('Snap ITC', 48)
        text = Text(font, '0000', 5, 70, pygame.Color('white'))

        x, y = 5, 5
        for _ in range(player.lives):  # Создаем видимые для игрока жизни
            live = Live(x, y)
            x += 65

        for i in range(LEVELS[level][1]):  # Создаем нужное количество препятствий
            j = i % len(obstcl_images)
            obs = Obstacles(obstcl_images[j], LEVELS[level][2])
        game_over = False
        allgame_music[0].stop()  # Останавливаем музыку главного экрана
        allgame_music[1].play(loops=-1)  # Включаем музыку игры

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:  # Нажатие на пробел - Выстрел
            if event.key == pygame.K_SPACE:
                player.upbull()
            if event.key == pygame.K_q:
                pause = not pause

    if not pause:
        # Обновляем все группы спрайтов
        hero_group.update()
        obs_group.update()
        back.update()
        bull_group.update()
        prt_group.update()

        if back.rect.y == 0 and player.rect.y <= 0:  # Игрок выиграл
            pobeda_sound.play()  # Звук победы
            allgame_music[1].stop()  # Останавливаем музыку игры
            allgame_music[2].play(loops=-1)  # Включаем музыку конечной заставки
            gameover_screen(player.points, 'Happy! You have passed this level!')

        proverka_bullet = pygame.sprite.groupcollide(obs_group, bull_group, True,
                                                     True)  # Проверяем попала ли пуля в препятствие
        if proverka_bullet:  # Если попали, то нужно создать новые препятствия вместо удаленных
            for obs in proverka_bullet:
                create_particles((obs.rect.x + 5, obs.rect.y + 5), fire_image)
                boom_sound.play()  # звук взрыва
            for _ in range(len(proverka_bullet)):
                obs_group.add(Obstacles(obstcl_images[random.randrange(len(obstcl_images))], LEVELS[level][2]))
                player.points += 10  # зачисляем игроку очки, за каждое препятствие 10 очков
            text.text = str(player.points).rjust(4, '0')
            text.string_rendered = text.font.render(text.text, True, text.color)

        hits = pygame.sprite.spritecollide(player, obs_group, True, pygame.sprite.collide_circle)
        if hits:  # Проверяем врезался ли наш игрок в препятствие
            create_particles((player.rect.x + 10, player.rect.y + 10), vsp_image)
            for _ in hits:
                stolk_sound.play()  # Звук столкновения
                player.lives -= 1
                hearts_group.remove(hearts_group.sprites()[-1])
            if player.lives == 0:  # Если жизни игрока закончились, игра заканчивается - игрок проиграл
                allgame_music[1].stop()  # Останавливаем музыку игры
                allgame_music[2].play(loops=-1)  # Включаем музыку конечной заставки
                gameover_sound.play()  # музыка проигрыша
                game_over = True
                sit = gameover_screen(player.points, 'Oh.. Try again!')
                if sit == 'new':  # Если sit == 'new', то игрок выбрал вернуться на главную страницу ->
                    # уровень выбирается заново; если sit is None, то игрок начал заново или вышел из игры
                    screen_need = True

    # Отрисовываем игру
    screen.fill(pygame.Color("black"))
    sprite_group.draw(screen)
    prt_group.draw(screen)
    obs_group.draw(screen)
    hero_group.draw(screen)
    hearts_group.draw(screen)
    screen.blit(text.string_rendered, text.intro_rect)
    clock.tick(FPS)
    pygame.display.flip()
pygame.quit()
