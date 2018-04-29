import pygame
import math
BALL_IMAGE = "Extras\\Ball.png"
MAN = "Extras\\Ball.png"  # Find another file
SWORD = "Extras\\Sword.png"
GAME_BALL = "Extras\\Game_ball.png"
GRAVITY = 9.8
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLACK_PIXEL = (0, 0, 0, 1)
CYAN = (72, 118, 255)
LIGHT_GRAY = (192, 192, 192)


class Ball(pygame.sprite.Sprite):
    def __init__(self, (x, y), color, (vx, vy)):
        super(self.__class__, self).__init__()
        self.image = pygame.image.load(BALL_IMAGE).convert()
        array = pygame.PixelArray(self.image)
        self.rect = self.image.get_rect()
        array.replace(BLACK, color)
        self.image = array.make_surface()
        self.image.set_colorkey(WHITE)
        self.rect.centerx = x
        self.rect.centery = y
        self.__vx = vx
        self.__vy = vy
        self.size = self.image.get_width()

    def update_v(self, vx, vy):
        self.__vx = vx
        self.__vy = vy

    def update_loc(self):
        self.rect.x += self.__vx
        self.rect.y += self.__vy

    def get_pos(self):
        return self.rect.x, self.rect.y

    def get_v(self):
        return self.__vx, self.__vy

    def ball_info(self):
        return self.rect, self.get_pos(), self.get_v()


class Man(pygame.sprite.Sprite):
    def __init__(self, (x, y), (vx, vy), color):
        super(self.__class__, self).__init__()
        self.image = pygame.image.load(MAN).convert()
        array = pygame.PixelArray(self.image)
        self.rect = self.image.get_rect()
        array.replace(BLACK, color)
        self.image = array.make_surface()
        self.image.set_colorkey(WHITE)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.x_start = self.rect.x
        self.y_start = self.rect.y
        self.x_change = 0
        self.y_change = 0
        self.vx_top = vx
        self.vy_top = vy
        self.__vx = vx
        self.__vy = vy
        self.__ax = 0
        self.__ay = GRAVITY
        self.size = self.image.get_width()

    def update_a(self, (ax, ay)):
        self.__ax = ax
        self.__ay = ay

    def update_v(self, dimensions):
        vx = math.pow(self.vx_top, 2) + (2 * self.__ax * self.x_change)
        vy = math.pow(self.vy_top, 2) + (2 * self.__ay * self.y_change)
        vx /= dimensions
        vy /= dimensions
        self.__vx = math.sqrt(vx)
        self.__vy = math.sqrt(vy)

    def update_loc(self):
        self.rect.x += self.__vx
        self.rect.y += self.__vy

    def delta(self):
        self.x_change = self.rect.x - self.x_start
        self.y_change = self.rect.y - self.y_start

    def update_loc_speed(self, dimensions):
        self.update_loc()
        self.delta()
        self.update_v(dimensions)

    def get_pos(self):
        return self.rect.x, self.rect.y

    def get_vx(self):
        return self.__vx

    def get_vy(self):
        return self.__vy

    def get_v(self):
        return self.get_vx(), self.get_vy()

    def get_a(self):
        return self.__ax, self.__ay


class Sword(pygame.sprite.Sprite):
    def __init__(self, (x, y), vel, angle=-90):
        super(self.__class__, self).__init__()
        self.image = pygame.image.load(SWORD).convert()
        rot_image = pygame.transform.rotate(self.image, angle)
        self.rect = rot_image.get_rect()
        rot_rect = self.rect.copy()
        rot_rect.center = rot_image.get_rect().center
        self.image = rot_image.subsurface(rot_rect).copy()
        self.image.set_colorkey(BLACK)
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.mask_outline = [(t[0] + self.rect.x, t[1] + self.rect.y)
                             for t in self.mask.outline()]
        self.x = float(self.rect.x)
        self.y = float(self.rect.y)
        self.starting_vel = vel
        self.angle = 0
        self.__vx = vel * math.cos(self.angle)
        self.__vy = vel * math.cos(self.angle)
        self.rotate_angle = angle

    def update_image(self):
        x, y = self.rect.center
        self.image = pygame.image.load(SWORD).convert()
        self.image = pygame.transform.rotate(self.image, self.rotate_angle)
        self.image.set_colorkey(BLACK)
        self.mask = pygame.mask.from_surface(self.image)
        self.mask_outline = self.mask.outline()
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.mask_outline = [(t[0] + self.rect.x, t[1] + self.rect.y)
                             for t in self.mask.outline()]

    def update_starting_vel(self, starting_vel):
        self.starting_vel = starting_vel

    def update_a(self, num):
        self.angle += num
        self.rotate_angle += num
        self.angle %= 360
        self.rotate_angle %= 360
        self.update_image()

    def update_v_a(self):
        self.__vx = self.starting_vel
        self.__vy = -self.starting_vel
        self.__vx *= math.cos(math.radians(self.angle))
        self.__vy *= math.sin(math.radians(self.angle))
        self.__vx /= 50.0
        self.__vy /= 50.0
        self.__vx = round(self.__vx, 4)
        self.__vy = round(self.__vy, 4)

    def update_loc(self):
        self.x += self.__vx
        self.rect.x = round(self.x, 4)
        self.y += self.__vy
        self.rect.y = round(self.y, 4)

    def get_pos(self):
        return str(self.rect.topleft) + "\n(" + str(self.x) + ", " + str(self.y) + ")"  # Find error

    def get_mid(self):
        return self.rect.center

    def get_angle(self):
        return self.angle

    def get_v(self):
        return self.__vx, self.__vy

    def get_starting_v(self):
        return self.starting_vel

    def to_string(self):
        st = str(self.rect) + ", " + ", " + str(self.starting_vel)
        st += ", " + str(self.__vx) + ", "
        st += str(self.__vy) + ", " + str(self.angle)
        return st


class Player1B(pygame.sprite.Sprite):
    def __init__(self, (x, y), vel, angle, color, (left, right), screen_relation=(1, 1)):
        super(self.__class__, self).__init__()
        self.color = color
        self.img = pygame.image.load(GAME_BALL).convert()
        screen_relation[0] *= self.img.get_width()
        screen_relation[1] *= self.img.get_height()
        self.img = pygame.transform.scale(self.img, screen_relation)
        array = pygame.PixelArray(self.img)
        array.replace(WHITE, self.color)
        self.img = array.make_surface()
        rot_image = pygame.transform.rotate(self.img, angle)
        self.rect = rot_image.get_rect()
        rot_rect = self.rect.copy()
        rot_rect.center = rot_image.get_rect().center
        self.image = rot_image.subsurface(rot_rect).copy()
        if self.color != BLACK_PIXEL:
            self.image.set_colorkey(BLACK_PIXEL)
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.mask_outline = [(t[0] + self.rect.x, t[1] + self.rect.y)
                             for t in self.mask.outline()]
        self.x = float(self.rect.x)
        self.y = float(self.rect.y)
        self.starting_vel = vel
        self.angle = angle
        self.__vx = vel * math.cos(math.radians(self.angle))
        self.__vy = vel * math.sin(math.radians(self.angle))
        self.binds = (left, right)
        self.blank_line = False

    def update_image(self):
        x, y = self.rect.center
        self.image = pygame.transform.rotate(self.img, self.angle)
        if self.color != BLACK_PIXEL:
            self.image.set_colorkey(BLACK_PIXEL)
        self.mask = pygame.mask.from_surface(self.image)
        self.mask_outline = self.mask.outline()
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.mask_outline = [(t[0] + self.rect.x, t[1] + self.rect.y)
                             for t in self.mask.outline()]

    def change_blank_line(self):
        self.blank_line = not self.blank_line

    def update_color(self, color):
        self.color = color
        self.update_image()

    def update_starting_vel(self, starting_vel):
        self.starting_vel = starting_vel

    def update_a(self, num):
        self.angle += num
        self.angle %= 360
        self.update_image()

    def update_v_a(self):
        self.__vx = self.starting_vel
        self.__vy = -self.starting_vel
        self.__vx *= math.cos(math.radians(self.angle))
        self.__vy *= math.sin(math.radians(self.angle))
        self.__vx /= 50.0
        self.__vy /= 50.0
        self.__vx = round(self.__vx, 4)
        self.__vy = round(self.__vy, 4)

    def update_loc(self):
        self.x += self.__vx
        self.rect.x = round(self.x, 4)
        self.y += self.__vy
        self.rect.y = round(self.y, 4)

    def get_pos(self):
        return self.rect.topleft

    def get_blank_line(self):
        return self.blank_line

    def get_mid(self):
        return self.rect.center

    def get_angle(self):
        return self.angle

    def get_v(self):
        return self.__vx, self.__vy

    def get_starting_v(self):
        return self.starting_vel

    def get_image(self):
        self.update_image()
        return self.image

    def get_color(self):
        return self.color

    def get_binds(self):
        return self.binds

    def get_rect(self):
        return self.rect

    def to_string(self):
        string = "pos: " + str(self.get_pos()) + "\n"
        string += "vel: " + str(self.get_v()) + "\n"
        string += "angle: " + str(self.get_angle()) + "\n"
        string += "Color: " + str(self.color)
        return string


class Cursors:
    CURSOR_STRINGS = {              # sized 24x24
        "PENCIL": [
            (
                "                  X     ",  # 1
                "                 XoX    ",  # 2
                "                XoooX   ",  # 3
                "               XoooooX  ",  # 4
                "              XXXXooooX ",  # 5
                "             X..XXoooooX",  # 6
                "            X..X.XXXooX ",  # 7
                "           X..X...XXoX  ",  # 8
                "          X..X...X.XX   ",  # 9
                "         X..X...X..X    ",  # 10
                "        X..X...X..X     ",  # 11
                "       X..X...X..X      ",  # 12
                "      X..X...X..X       ",  # 13
                "     XX.X...X..X        ",  # 14
                "     XXX...X..X         ",  # 15
                "    X.XXX.X..X          ",  # 16
                "    X...XX..X           ",  # 17
                "   X....XXXX            ",  # 18
                "   X.....XX             ",  # 19
                "  XX...XX               ",  # 20
                "  XXXXXX                ",  # 21
                " XXXX                   ",  # 22
                " XX                     ",  # 23
                "                        ",  # 24
            ),
            (0, 23), (24, 24)
        ],
        "ERASER": [
            (
                "                        ",
                "                        ",
                "  XXXXXXXXXXXXXXXXXXXX  ",
                "  X..................X  ",
                "  X..................X  ",
                "  X..................X  ",
                "  X..................X  ",
                "  X..................X  ",
                "  X..................X  ",
                "  X..................X  ",
                "  X..................X  ",
                "  X..................X  ",
                "  X..................X  ",
                "  X..................X  ",
                "  X..................X  ",
                "  X..................X  ",
                "  X..................X  ",
                "  X..................X  ",
                "  X..................X  ",
                "  X..................X  ",
                "  X..................X  ",
                "  XXXXXXXXXXXXXXXXXXXX  ",
                "                        ",
                "                        "
            ),
            (12, 12), (24, 24)
        ],
        "GET_COLOUR": [
            (
                "                        ",   # 1
                "               XXXXX    ",   # 2
                "              X.....X   ",   # 3
                "             X.......X  ",   # 4
                "            X...XXX...X ",   # 5
                "            X..XoooX..X ",   # 6
                "            X..XoooX..X ",   # 7
                "            X..XoooX..X ",   # 8
                "            X...XXX...X ",   # 9
                "           X.........X  ",   # 10
                "          X.........X   ",   # 11
                "         XX....XXXXX    ",   # 12
                "        X.X...X         ",   # 13
                "       X..XXXX          ",   # 14
                "      XX....X           ",   # 15
                "     X.X...X            ",   # 16
                "    X..XXXX             ",   # 17
                "   XX....X              ",   # 18
                "  X.X...X               ",   # 19
                "  X.XXXX                ",   # 20
                " X....X                 ",   # 21
                " X..XX                  ",   # 22
                " XXX                    ",   # 23
                "                        "    # 24
            ),
            (0, 23), (24, 24)
        ],
        "BUCKET": [
            (
                "                        ",  # 1
                "                        ",  # 2
                "                        ",  # 3
                "                        ",  # 4
                "         XXX            ",  # 5
                "        X   X           ",  # 6
                "        XX  X           ",  # 7
                "       XX X X           ",  # 8
                "     XX.X..XX           ",  # 9
                "   XXX..X...X           ",  # 10
                "  XXX..XoX...X          ",  # 11
                " XXX....X.....X         ",  # 12
                " XXXX..........X        ",  # 13
                " XXX X.........X        ",  # 14
                " XXX  X........X        ",  # 15
                " XXX   X......X         ",  # 16
                " XXX    X....X          ",  # 17
                "  XX     X..X           ",  # 18
                "   X      XX            ",  # 19
                "                        ",  # 20
                "                        ",  # 21
                "                        ",  # 22
                "                        ",  # 23
                "                        "   # 24
            ),
            (3, 19), (24, 24)
        ]
    }

    blacks = "."
    whites = "X"
    xors = "o"

    def __init__(self):
        # Cursors.CURSOR_STRINGS["PENCIL"][0] = Cursors.PENCIL_STRING
        self.pencil_cursor = list(pygame.cursors.compile(Cursors.CURSOR_STRINGS["PENCIL"][0],
                                                         black=Cursors.blacks,
                                                         white=Cursors.whites,
                                                         xor=Cursors.xors))
        self.pencil_cursor.insert(0, Cursors.CURSOR_STRINGS["PENCIL"][1])
        self.pencil_cursor.insert(0, Cursors.CURSOR_STRINGS["PENCIL"][2])
        self.eraser_cursor = list(pygame.cursors.compile(Cursors.CURSOR_STRINGS["ERASER"][0],
                                                         black=Cursors.blacks,
                                                         white=Cursors.whites,
                                                         xor=Cursors.xors))
        self.eraser_cursor.insert(0, Cursors.CURSOR_STRINGS["ERASER"][1])
        self.eraser_cursor.insert(0, Cursors.CURSOR_STRINGS["ERASER"][2])
        self.get_colour_cursor = list(pygame.cursors.compile(Cursors.CURSOR_STRINGS["GET_COLOUR"][0],
                                                             black=Cursors.blacks,
                                                             white=Cursors.whites,
                                                             xor=Cursors.xors))
        self.get_colour_cursor.insert(0, Cursors.CURSOR_STRINGS["GET_COLOUR"][1])
        self.get_colour_cursor.insert(0, Cursors.CURSOR_STRINGS["GET_COLOUR"][2])
        self.bucket_cursor = list(pygame.cursors.compile(Cursors.CURSOR_STRINGS["BUCKET"][0],
                                                         black=Cursors.blacks,
                                                         white=Cursors.whites,
                                                         xor=Cursors.xors))
        self.bucket_cursor.insert(0, Cursors.CURSOR_STRINGS["BUCKET"][1])
        self.bucket_cursor.insert(0, Cursors.CURSOR_STRINGS["BUCKET"][2])

    @staticmethod
    def get_pencil_string():
        return Cursors.CURSOR_STRINGS["PENCIL"][0]

    @staticmethod
    def get_eraser_string():
        return Cursors.CURSOR_STRINGS["ERASER"][0]

    def get_pencil(self):
        return self.pencil_cursor

    def get_eraser(self):
        return self.eraser_cursor

    def get_get_colour(self):
        return self.get_colour_cursor

    def get_bucket(self):
        return self.bucket_cursor


class PingBall(pygame.sprite.Sprite):
    def __init__(self, (x, y), colour, velocity, angle):
        super(self.__class__, self).__init__()
        self.colour = colour
        self.velocity = velocity
        self.angle = angle  # degrees
        self.img = pygame.image.load(GAME_BALL).convert()
        array = pygame.PixelArray(self.img)
        array.replace(WHITE, self.colour)
        self.img = array.make_surface()
        rot_image = pygame.transform.rotate(self.img, angle)
        self.rect = rot_image.get_rect()
        rot_rect = self.rect.copy()
        rot_rect.center = rot_image.get_rect().center
        self.image = rot_image.subsurface(rot_rect).copy()
        if self.color != BLACK_PIXEL:
            self.image.set_colorkey(BLACK_PIXEL)
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.mask_outline = [(t[0] + self.rect.x, t[1] + self.rect.y)
                             for t in self.mask.outline()]
        self.__x = float(self.rect.x)
        self.__y = float(self.rect.y)
        self.__vx = velocity * math.cos(math.radians(self.angle))
        self.__vy = -velocity * math.sin(math.radians(self.angle))

    def update_image(self):
        x, y = self.rect.center
        self.image = pygame.transform.rotate(self.img, self.angle)
        if self.color != BLACK_PIXEL:
            self.image.set_colorkey(BLACK_PIXEL)
        self.mask = pygame.mask.from_surface(self.image)
        self.mask_outline = self.mask.outline()
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.mask_outline = [(t[0] + self.rect.x, t[1] + self.rect.y)
                             for t in self.mask.outline()]

    def update_v_a(self):
        self.__vx = self.starting_vel
        self.__vy = -self.starting_vel
        self.__vx *= math.cos(math.radians(self.angle))
        self.__vy *= math.sin(math.radians(self.angle))
        self.__vx /= 50.0
        self.__vy /= 50.0
        self.__vx = round(self.__vx, 4)
        self.__vy = round(self.__vy, 4)

    def update_loc(self):
        self.__x += self.__vx
        self.rect.x = round(self.__x, 4)
        self.__y += self.__vy
        self.rect.y = round(self.__y, 4)

    def hit(self, colour, hit_point, thing=None):
        """
        Non-goal horizontal sides will be white
        Non-goal vertical sides will be cyan
        Goals will be light gray
        Players and other things will be other colours
        """
        colour = [colour[i] for i in xrange(3)]
        if colour == WHITE:
            self.angle = 360 - self.angle
        elif colour == CYAN:
            big_angle = self.angle / 180
            self.angle = abs(180 - self.angle) + (big_angle * 180)
        elif colour == LIGHT_GRAY:
            return True
        else:
            if isinstance(thing, PongPlayer):
                rect = thing.rect
                x = hit_point[0] - rect.left
                y = hit_point[1] - rect.top
                if x == 0:
                    # 90 - 270
                    pass
                else:
                    # 270 - 90
                    pass


class PongPlayer(pygame.sprite.Sprite):
    def __init__(self):
        pass