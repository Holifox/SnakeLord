import pygame as pg
import pygame_menu as pg_menu
import ctypes
from math import hypot

BACK_COLOR = (10, 50, 50)
BACK_COLOR2 = (10, 30, 30)
BORDER_COLOR = (10, 70, 70)
FONT_COLOR = (10, 80, 80)

pg.init()
# ctypes.windll.user32.SetProcessDPIAware()
face = pg.display.set_mode((0, 0), pg.FULLSCREEN)
W, H = face.get_size()
pg.display.set_caption("Snake Lord")
font = pg.font.SysFont('Verdana', 40)
clock = pg.time.Clock()

face2 = pg.Surface((W*3, H*3), pg.SRCALPHA)
face2_x, face2_y = -W, -H

# Load the background image
back = pg.image.load(r'back.png')
run = True
FPS = 15


class SnakeItem(pg.sprite.Sprite):
    def __init__(self, x, y, r) -> None:
        super().__init__()
        surf = pg.Surface((2*r, 2*r), pg.SRCALPHA)
        pg.draw.circle(surf, (0, 30, 30), (r, r), r)
        self.image = surf
        self.rect = (x, y, x + r, y + r)
        self.r = r


class Snake():
    def __init__(self, length: int, dencity: int, thickness: int) -> None:
        # pg.sprite.Group.__init__(self, *snake_items)
        num_items = length // dencity
        items = []
        for i in range(num_items):
            item = SnakeItem(W/2-i*dencity, H/2, thickness)
            items.append(item)
        self.items = items
        self.dencity = dencity
        self.thickness = thickness

    def move(self) -> None:
        head_item = self.items[0]
        mouse_x, mouse_y = pg.mouse.get_pos()
        head_item_x, head_item_y = head_item.rect[:2]

        dist_x, dist_y = mouse_x - head_item_x, mouse_y - head_item_y
        dist = hypot(dist_x, dist_y)
        cos = dist_x / dist
        sin = dist_y / dist
        
        new_item_x = head_item_x + self.dencity * cos
        new_item_y = head_item_y + self.dencity * sin
        new_item = SnakeItem(new_item_x, new_item_y, head_item.r)
        self.items.insert(0, new_item)
        self.items.pop()

    def draw(self, surface):
        for item in self.items:
            x, y = item.rect[:2]
            surface.blit(item.image, (x, y))

        
main_snake = Snake(
    length = 300, 
    dencity = 7, 
    thickness = 15
    )
    

def game():
    global main_menu, run, face, main_snake

    main_menu.disable()
    while run:
        events = pg.event.get()
        for event in events:
            if event.type == pg.QUIT:
                exit()

        face.blit(back, (0, 0))
        face.blit(face2, (face2_x, face2_y))
        main_snake.move()
        main_snake.draw(face)   
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
main_menu.add.button('Records')
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

main_menu.mainloop(face, bgfun = lambda: face.blit(back, (0, 0)))