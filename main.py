import pygame as pg
import pygame_menu as pg_menu
import ctypes
from math import hypot, sqrt, pow
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
font = pg.font.SysFont('Verdana', 60)
clock = pg.time.Clock()


# Load the background image
back = pg.image.load(r'back.png')
surf2 = pg.Surface(back.get_size()) 
surf2.blit(back, (0, 0))
surf2_pos = (W//2, H//2)
run = True
FPS = 30


# ------------------------------ Classes ------------------------------ #


class SnakeItem(pg.sprite.Sprite):
    def __init__(self, x, y, r) -> None:
        super().__init__()

        x, y = round(x), round(y)
        img_surf = pg.Surface((2*r, 2*r), pg.SRCALPHA)

        pg.draw.circle(img_surf, (0, 100, 80), (r, r), r)
        self.image = img_surf
        self.rect = pg.Rect(x, y, r*2, r*2)

        
class Snake:
    def __init__(self, length: int) -> None:
        thickness = 2*sqrt(length)
        dencity = thickness // 2
        items = []
        Cx, Cy = surf2.get_rect().center
        for i in range(length):
            item = SnakeItem(Cx - i*dencity, Cy, thickness)
            items.append(item)
        self.items = items
        self.len = length
        self.dencity = dencity
        self.thickness = thickness
        self.mouse_pos = (0, 0)

    def add_new_item(self):
        global surf2, surf2_pos, run

        # Take coords of snake's first item
        head_item = self.items[0]
        head_item_x, head_item_y = head_item.rect[:2]

        # determine mouse cursor position 
        mouse_x, mouse_y = pg.mouse.get_pos()
        if mouse_x != self.mouse_pos[0] and mouse_y != self.mouse_pos[1]:
            surf2_w, surf2_h = surf2.get_size()
            mouse_x += -surf2_pos[0] + 0.5 * surf2_w
            mouse_y += -surf2_pos[1] + 0.5 * surf2_h

            # Count coords for snake's new item
            dist_x, dist_y = mouse_x - head_item_x, mouse_y - head_item_y
            dist = hypot(dist_x, dist_y)
            cos = dist_x / dist
            sin = dist_y / dist
            dx, dy = round(self.dencity * cos), round(self.dencity * sin)
        else:   # if mouse cursor haven't moved
            dx, dy = self.shift

        new_item_x = head_item_x + dx
        new_item_y = head_item_y + dy

        # Set a new item and discard the last
        new_item = SnakeItem(new_item_x, new_item_y, self.thickness)
        if not surf2.get_rect().contains(new_item.rect):
            run = False
        self.items.insert(0, new_item)
    
        self.shift = (dx, dy)
        self.mouse_pos = (mouse_x, mouse_y)

    def check_bonus(self, bonuses):
        head_item = self.items[0]
        test_collide = pg.sprite.spritecollideany(head_item, bonuses)
        if test_collide == None: # if no bonuses were eaten
            tail_item = self.items.pop()
            clear(tail_item)
        else:
            self.len = len(self.items)
            self.thickness = 2*sqrt(self.len)

            bonus = test_collide
            bonus.kill()
            clear(bonus)


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


def show_room(dx, dy):
    global surf, surf2, surf2_pos, main_snake
    x, y = surf2_pos
    surf2_pos = (x - dx, y - dy)
    surf2_x, surf2_y = surf2_pos
    
    length = main_snake.len
    k = pow(length / 50, 0.3)
    small_surf2_x = W//2 - round((W//2 - surf2_x) / k)
    small_surf2_y = H//2 - round((H//2 - surf2_y) / k)
    small_surf2_pos = (small_surf2_x, small_surf2_y)

    surf2_w, surf2_h = surf2.get_size()
    small_surf2_w = round(surf2_w / k)
    small_surf2_h = round(surf2_h / k)
    
    small_surf2 = pg.transform.scale(surf2, (small_surf2_w, small_surf2_h))
    small_surf2_rect = small_surf2.get_rect(center = small_surf2_pos)
    surf.blit(small_surf2, small_surf2_rect)


def game():
    global main_menu, run, main_snake, surf2_pos, surf2
    
    main_menu.disable()
    end_menu.disable()
    surf2.blit(back, (0, 0))
    surf2_pos = (W//2, H//2)
    bonuses = set_bonuses(1000)
    bonuses.draw(surf2)
    pg.display.update()
    
    main_snake = Snake(50)

    run = True
    while run:
        events = pg.event.get()
        for event in events:
            if event.type == pg.QUIT:
                exit()

        main_snake.add_new_item()
        main_snake.check_bonus(bonuses)
        main_snake.draw()

        surf.fill((0, 0, 0))
        show_room(*main_snake.shift)
        text_surf = font.render(f'Score: {main_snake.len}', 1, (10, 100, 100))
        surf.blit(text_surf, (50, 30))
        
        pg.display.update()
        clock.tick(FPS)

    end_menu.enable()
    # surf2_rect = surf2.get_rect(center = surf2_pos)
    # end_menu.mainloop(surf, bgfun = lambda: surf.blit(surf2, surf2_rect))
    while end_menu.is_enabled():
        events = pg.event.get()
        end_menu.update(events)
        end_menu.draw(surf)
        pg.display.update()

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

end_menu = pg_menu.menu.Menu(
    'Game over', 600, 400, 
    mouse_motion_selection = True,
    theme = theme1, enabled = False)

# Add buttons on main_menu
main_menu.add.button('Start game', game)
main_menu.add.button('Exit', pg_menu.events.EXIT)

# Add buttons on end_menu
end_menu.add.button('Try again', game)
end_menu.add.button('Exit', pg_menu.events.EXIT)

def set_size(widget) -> None:
    ''' Costomise widgets '''
    name = str(widget)
    w, h = widget.get_rect()[2:]
    dw, dh = (250 - w)//2, (70 - h)//2
    widget.set_padding((dh, dw))

# Castomize menus
for menu in [main_menu, end_menu]:
    w, h = menu.get_size()
    w, h = w//2, h//2
    decorator = menu.get_decorator()
    decorator.add_line((w, -h), (w, h), color = BACK_COLOR, width = 4)
    decorator.add_line((w, h), (-w, h), color = BACK_COLOR, width = 4)
    decorator.add_line((-w - 2, h), (-w - 2, -h), color = BACK_COLOR, width = 4)

    for widget in menu._widgets:
        set_size(widget)

surf2_rect = surf2.get_rect(center = surf2_pos)
main_menu.mainloop(surf, bgfun = lambda: surf.blit(surf2, surf2_rect))