import pygame as pg
import pygame_menu as pg_menu
import ctypes
from math import hypot, sqrt
import random

BACK_COLOR = (10, 50, 50)
BACK_COLOR2 = (10, 30, 30)
BORDER_COLOR = (10, 70, 70)
FONT_COLOR = (10, 80, 80)
BONUS_COLORS = ((200, 100, 100), (100, 200, 100), (100, 100, 200))

pg.init()
ctypes.windll.user32.SetProcessDPIAware()
surf = pg.display.set_mode((0, 0), pg.FULLSCREEN)
W, H = surf.get_size()
pg.display.set_caption("Snake Lord")
font = pg.font.SysFont('Verdana', 40)
clock = pg.time.Clock()


# Load the background image
back = pg.image.load(r'back.png')
surf2 = pg.Surface((W*3, H*3)) #sub? scroll?
surf2.blit(back, (0, 0))
surf2_pos = (-W, -H)
run = True
FPS = 30


# ------------------------------ Classes ------------------------------ #


class SnakeItem(pg.sprite.Sprite):
    def __init__(self, x, y, r) -> None:
        super().__init__()

        x, y = round(x), round(y)
        self.rect = pg.Rect(x, y, r*2, r*2)
        img_surf = pg.Surface((2*r, 2*r), pg.SRCALPHA)

        pg.draw.circle(img_surf, (0, 100, 80), (r, r), r)
        self.image = img_surf
        self.r = r

        
class Snake():
    def __init__(self, length: int) -> None:
        # pg.sprite.Group.__init__(self)
        thickness = 2*sqrt(length)
        dencity = thickness // 2
        items = []
        for i in range(length):
            item = SnakeItem(W*1.5 - i*dencity, H*1.5, thickness)
            items.append(item)
        self.items = items
        self.dencity = dencity
        self.thickness = thickness

    def move(self, bonuses) -> None:
        '''The function makes the snake moving after mouse cursor'''
        global surf2, surf2_pos

        # Take coords of snake's first item
        head_item = self.items[0]
        head_item_x, head_item_y = head_item.rect[:2]

        # determine mouse cursor position 
        mouse_x, mouse_y = pg.mouse.get_pos()
        mouse_x -= surf2_pos[0]
        mouse_y -= surf2_pos[1]

        # Count coords for snake's new item
        dist_x, dist_y = mouse_x - head_item_x, mouse_y - head_item_y
        dist = hypot(dist_x, dist_y)
        cos = dist_x / dist
        sin = dist_y / dist
        dx, dy = round(self.dencity * cos), round(self.dencity * sin)
        new_item_x = head_item_x + dx
        new_item_y = head_item_y + dy

        # Set a new item and discard the last
        new_item = SnakeItem(new_item_x, new_item_y, head_item.r)
        self.items.insert(0, new_item)

        test_collide = pg.sprite.spritecollideany(new_item, bonuses)
        if test_collide == None: # if no bonuses were eaten
            tail_item = self.items.pop()
            clear(tail_item)
        else:
            bonus = test_collide
            bonus.kill()
            clear(bonus)

        self.head_item_shift = (dx, dy)

    def draw(self):
        global surf2
        for item in self.items:
            x, y = item.rect[:2]
            surf2.blit(item.image, (x, y))


# ------------------------------ Functions ------------------------------ #


def clear(obj) -> None:
    global surf2, back
    x, y = obj.rect[:2]
    surf2.blit(back, (x, y), obj.rect)


def drag_screen():
    global main_snake, surf2_pos

    dx, dy = main_snake.head_item_shift
    x, y = surf2_pos
    surf2_pos = (x - dx, y - dy)


def set_bonuses(num: int) -> pg.sprite.Group:
    global surf2
    bonuses = pg.sprite.Group()
    r = 10
    w, h = surf2.get_size()

    for i in range(num):
        color = random.choice(BONUS_COLORS)
        x = random.randrange(2*r, w - 4*r)
        y = random.randrange(2*r, h - 4*r)

        img_surf = pg.Surface((2*r, 2*r), pg.SRCALPHA)
        pg.draw.circle(img_surf, color, (r, r), r)

        bonus = pg.sprite.Sprite(bonuses)
        bonus.image = img_surf
        bonus.rect = pg.Rect(x, y, 2*r, 2*r)

    return bonuses


def game():
    global main_menu, run, main_snake

    main_menu.disable()
    bonuses = set_bonuses(1000)
    bonuses.draw(surf2)
    main_snake = Snake(50)

    while run:
        events = pg.event.get()
        for event in events:
            if event.type == pg.QUIT:
                exit()

        main_snake.move(bonuses)
        print(len(main_snake.items))
        main_snake.draw()
        drag_screen()
        surf.fill((0, 0, 0))
        surf.blit(surf2, surf2_pos)
        pg.display.update()
        clock.tick(FPS)

    

# ------------------------------ Menus ------------------------------ #

theme1 = pg_menu.Theme(
    title_font_color = FONT_COLOR,
    title_background_color = BACK_COLOR,
    background_color = BACK_COLOR2,

    widget_background_color = BACK_COLOR,
    widget_border_width = 5,
    widget_border_color = BORDER_COLOR,
    widget_font_color = FONT_COLOR,
    widget_selection_effect = pg_menu.widgets.NoneSelection(),
    widget_margin = (0, 15))

main_menu = pg_menu.menu.Menu(
    'Menu', 600, 450, 
    mouse_motion_selection = True,
    theme = theme1)

# Add buttons on main_menu
main_menu.add.button('Start game', game)
main_menu.add.button('Exit', pg_menu.events.EXIT)

def set_size(widget) -> None:
    ''' Costomise widgets '''
    name = str(widget)
    w, h = widget.get_rect()[2:]
    dw, dh = (250 - w)//2, (70 - h)//2
    widget.set_padding((dh, dw))

# Castomize menus
for menu in [main_menu]:
    w, h = menu.get_size()
    w, h = w//2, h//2
    decorator = menu.get_decorator()
    decorator.add_line((w, -h), (w, h), color = BACK_COLOR, width = 4)
    decorator.add_line((w, h), (-w, h), color = BACK_COLOR, width = 4)
    decorator.add_line((-w - 2, h), (-w - 2, -h), color = BACK_COLOR, width = 4)

    for widget in menu._widgets:

        set_size(widget)

main_menu.mainloop(surf, bgfun = lambda: surf.blit(surf2, (0, 0)))