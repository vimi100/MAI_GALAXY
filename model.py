import sys
import matplotlib.pyplot as plt
import pygame
import os
import time

class Point:
    def __init__(self, posx, posy):
        self.x = posx
        self.y = posy

    def out(self):
        return self.x, self.y

    def __add__(self, vec):
        x = self.x + vec.x
        y = self.y + vec.y
        return Point(x, y)

    def __sub__(self, vec):
        x = self.x - vec.x
        y = self.y - vec.y
        return Point(x, y)

    def __isub__(self, vec):
        self.x -= vec.x
        self.y -= vec.y
        return self

    def get_length(self):
        return(self.x**2 + self.y**2)**0.5

    def mul(self, k):
        return Point(self.x * k, self.y * k)

class Velocity(Point):
    def __init__(self, vx, vy):
        super().__init__(vx, vy)

WIDTH = 1200
HEIGHT = 650

SUITABLE_SPEED = 10000

FPS = 30 * SUITABLE_SPEED

# Задаем цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

M = 6 * (10 ** 24)
G = 6.67 * (10 ** -11)

GM = G * M
EARTHPOS = Point(WIDTH / 2, HEIGHT / 2)
EARTHRAD = 6.3781 * 10**6

METRES_IN_PIXEL = EARTHRAD/((360+24)/2)


def to_pix_vec(v: Point):
    return v.mul(1 / METRES_IN_PIXEL)
def to_pix(x):
    return x*(1 / METRES_IN_PIXEL)


def pix_to_vec(v: Point):
    return v.mul(METRES_IN_PIXEL)
def pix_to(x):
    return x * METRES_IN_PIXEL


class Tail(pygame.sprite.Sprite):
    def __init__(self, position: Point):
        pygame.sprite.Sprite.__init__(self)
        self.position = position


class Satelite(Tail):
    def __init__(self, position: Point, v0: Point, do_lessen=False, do_graph = False):
        super().__init__(position)
        img_folder = os.path.join(game_folder, 'image')
        self.image = pygame.image.load(os.path.join(img_folder, 'satelite.png')).convert()
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.center = (position.out())
        self.v0 = v0
        self.a = Point(0, 0)
        self.graph = list()
        self.do_lessen = do_lessen
        self.do_graph = do_graph

    def move(self, direction):
        STEP = 400  # м/с
        if direction == 0:
            self.v0 += Velocity(0, -STEP)
        elif direction == 1:
            self.v0 += Velocity(-STEP, 0)
        elif direction == 2:
            self.v0 += Velocity(0, STEP)
        elif direction == 3:
            self.v0 += Velocity(STEP, 0)

    def lessen(self):
        if self.v0.x >= 0:
            self.v0.x -= 1 / 1000000
        else:
            self.v0.x += 1 / 1000000
        if self.v0.y >= 0:
            self.v0.y -= 1 / 1000000
        else:
            self.v0.y += 1 / 1000000

    def graphy_vec(self, elem: Point):
        self.graph.append(elem.get_length())
    def graphy(self, elem):
        self.graph.append(elem)


    def print_vabs(self):
        print(f"Текущая скорость равна {self.v0.get_length()} м/с")
    def print_v(self):
        print(f"Текущий вектор скорости равен x:{self.v0.x} y:{-self.v0.y}")
    def print_aabs(self):
        print(f"Текущее ускорение равно {self.a.get_length()} м/с**2")
    def print_a(self):
        print(f"Текущий вектор ускорения равен x:{self.a.x} y:{-self.a.y}")
    def print_r(self):
        printing = pix_to( (EARTHPOS - self.position).get_length() ) - EARTHRAD
        print(f"Текущее расстояние равно {printing/1000} км")

    def update(self):
        rprint = (pix_to((EARTHPOS - self.position).get_length())-EARTHRAD) / 1000
        r = pix_to_vec(EARTHPOS - self.position).get_length()
        self.a = pix_to_vec(EARTHPOS - self.position).mul((GM / (r ** 3)))
        self.v0 += self.a  # metres per seconds
        self.position += to_pix_vec(self.v0) #  pixels
        self.rect.center = (self.position.out())

        if self.do_lessen:
            self.lessen()
        if self.do_graph:
            #self.graphy_vec(self.a)
            self.graphy(rprint)


class Planet(Tail):
    def __init__(self, position):
        super().__init__(position)
        img_folder = os.path.join(game_folder, 'image')
        self.image = pygame.image.load(os.path.join(img_folder, 'earth.png')).convert()
        self.rect = self.image.get_rect()
        self.rect.center = (position.out())

    def update(self):
        pass


if __name__ == '__main__':
    # print("радиус Земли 6370000m")
    # posX = int(input("Смещение от центра Земли по х, м: "))
    # posY = -int(input("Смещение от центра Земли по y, м: "))
    # velX = int(input("Начальная скорость по x, м/с: "))
    # velY = -int(input("Начальная скорость по y, м/с :"))
    pygame.init()
    pygame.mixer.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Выход на орбиту")
    clock = pygame.time.Clock()
    all_sprites = pygame.sprite.Group()

    game_folder = os.path.dirname(__file__)

    # Задайте позицию спутника и его начальную скорость
####################################################################################################################
    sat = Satelite(EARTHPOS + Point(0, to_pix(EARTHRAD+475000)), Velocity(8100, 0), do_graph=True, do_lessen=False)
    earth = Planet(EARTHPOS)
####################################################################################################################
    all_sprites.add(earth, sat)
    running = True
    print(f"Расстояние {pix_to( (sat.position-EARTHPOS).get_length()) - EARTHRAD} метров от Земли")
    print(f"Начальная скорость {sat.v0.get_length()} м/с")
    while running:
        # Держим цикл на правильной скорости
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    sat.move(0)
                elif event.key == pygame.K_a:
                    sat.move(1)
                elif event.key == pygame.K_s:
                    sat.move(2)
                elif event.key == pygame.K_d:
                    sat.move(3)
                elif event.key == pygame.K_1:
                    sat.print_r()
                elif event.key == pygame.K_2:
                    sat.print_vabs()
                elif event.key == pygame.K_3:
                    sat.print_aabs()
                elif event.key == pygame.K_4:
                    sat.print_v()
                elif event.key == pygame.K_5:
                    sat.print_a()
        # Обновление
        all_sprites.update()
        collide = (sat.position.x-EARTHPOS.x) ** 2 + (sat.position.y-EARTHPOS.y) ** 2 <= to_pix(EARTHRAD) ** 2
        if collide:
            running = False
            print("Столкновение!")
        # Рендеринг
        screen.fill(BLACK)
        all_sprites.draw(screen)
        # После отрисовки всего, "переворачиваем" экран
        pygame.display.flip()
    if sat.do_graph:
        print(len(sat.graph))
        plt.plot(list(range(0, len(sat.graph))), sat.graph)
        plt.show()
    time.sleep(2)
    pygame.quit()
    sys.exit()
