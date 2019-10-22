import sys
from copy import deepcopy, copy
from random import choice, randint

import pygame
from pygame.locals import *


class Game(object):
    def __init__(self, size, caption):
        pygame.init()
        pygame.font.init()

        self.caption = caption
        self.size = size
        self.screen = pygame.display.set_mode(size)
        self.clock = pygame.time.Clock()
        self.speed_max = 10
        self.speed_min = 1
        self.speed = 1
        self.step = 0

        pygame.display.set_caption(self.caption)

    def loop(self):
        self.screen.fill(BLACK)

    def event(self, event):
        pass

    def run_forever(self):
        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    sys.exit()
                self.event(event)
            pygame.display.set_caption(self.caption)
            self.loop()
            pygame.display.update()
            self.clock.tick(60)


# Define the colors we will use in RGB format
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

CYAN = (0, 255, 255)
YELLOW = (255, 255, 0)
MAGENTA = (255, 0, 255)

ORANGE = (255, 165, 0)


class Item(object):
    ITEM_LIST = {
        'I': [
            [(-1, 0), (0, 0), (1, 0), (2, 0)],
            [(0, -1), (0, 0), (0, 1), (0, 2)],
            [(-1, 0), (0, 0), (1, 0), (2, 0)],
            [(0, -1), (0, 0), (0, 1), (0, 2)],
        ],
        'J': [
            [(-1, 0), (-1, 1), (0, 1), (1, 1)],
            [(1, -1), (1, 0), (0, 1), (1, 1)],
            [(-1, 0), (0, 0), (1, 0), (1, 1)],
            [(0, -1), (1, -1), (0, 0), (0, 1)],
        ],
        'L': [
            [(1, 0), (-1, 1), (0, 1), (1, 1)],
            [(0, -1), (1, -1), (1, 0), (1, 1)],
            [(-1, 0), (0, 0), (1, 0), (-1, 1)],
            [(0, -1), (0, 0), (0, 1), (1, 1)],
        ],
        'O': [
            [(0, 0), (1, 0), (0, 1), (1, 1)],
            [(0, 0), (1, 0), (0, 1), (1, 1)],
            [(0, 0), (1, 0), (0, 1), (1, 1)],
            [(0, 0), (1, 0), (0, 1), (1, 1)],
        ],
        'S': [
            [(0, 0), (1, 0), (-1, 1), (0, 1)],
            [(0, -1), (0, 0), (1, 0), (1, 1)],
            [(0, 0), (1, 0), (-1, 1), (0, 1)],
            [(0, -1), (0, 0), (1, 0), (1, 1)],
        ],
        'Z': [
            [(-1, 0), (0, 0), (0, 1), (1, 1)],
            [(1, -1), (0, 0), (1, 0), (0, 1)],
            [(-1, 0), (0, 0), (0, 1), (1, 1)],
            [(1, -1), (0, 0), (1, 0), (0, 1)],
        ],
        'T': [
            [(0, -1), (-1, 0), (0, 0), (1, 0)],
            [(0, -1), (-1, 0), (0, 0), (0, 1)],
            [(-1, 0), (0, 0), (1, 0), (0, 1)],
            [(0, -1), (0, 0), (1, 0), (0, 1)],
        ]
    }
    COLOR_LIST = {
        'I': CYAN,
        'J': ORANGE,
        'L': YELLOW,
        'O': BLUE,
        'S': GREEN,
        'Z': RED,
        'T': MAGENTA,
    }

    def __init__(self, position, item_key=None, direction=None):
        self.position = position
        self.item_key = item_key if item_key else choice(list(self.ITEM_LIST.keys()))
        self.direction = direction if direction else randint(0, 3)
        pass

    @property
    def block_relative(self):
        return self.ITEM_LIST[self.item_key][self.direction]

    @property
    def block(self):
        return [
            [self.position[0] + block[0], self.position[1] + block[1], self.COLOR_LIST[self.item_key]]
            for block in self.block_relative
        ]

    @property
    def border(self):
        border = [None, None, None, None]
        for block in self.block:
            border[0] = block[1] if border[0] is None else block[1] if block[1] < border[0] else border[0]
            border[1] = block[0] if border[1] is None else block[0] if block[0] > border[1] else border[1]
            border[2] = block[1] if border[2] is None else block[1] if block[1] > border[2] else border[2]
            border[3] = block[0] if border[3] is None else block[0] if block[0] < border[3] else border[3]
        return border

    def rotate(self):
        new = deepcopy(self)
        new.direction = new.direction + 1 if new.direction < 3 else 0
        return new

    def move(self, action):
        new = deepcopy(self)
        if action == 'RIGHT':
            new.position[0] += 1
        elif action == 'DOWN':
            new.position[1] += 1
        elif action == 'LEFT':
            new.position[0] -= 1
        elif action == 'UP':
            new.position[1] -= 1
        return new


class Tetris(Game):
    BLOCK_SIZE = 28
    POSITION_NEXT = (12, 1)
    POSITION_NEW = (4, 1)

    alive = True
    pause = False
    score = 0
    item_next = None
    item_active = None
    block_static = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.plan_width = self.BLOCK_SIZE * 12
        self.plan_height = int(self.size[1] / self.BLOCK_SIZE) * self.BLOCK_SIZE
        self.pos_y_max = int(self.plan_height / self.BLOCK_SIZE) - 3
        self.pos_x_max = int(self.plan_width / self.BLOCK_SIZE) - 3

        self.reset()

    def reset(self):
        self.alive = True
        self.pause = False
        self.score = 0
        self.item_next = Item(self.POSITION_NEXT)
        self.item_active = Item(list(self.POSITION_NEW))
        self.item_active.position[1] = self.item_active.border[0] - self.item_active.border[2] - 1
        self.block_static = []

    def event(self, event):
        if event.type in (KEYDOWN, KEYDOWN):
            if event.key == pygame.K_UP:
                self.up()
            elif event.key == pygame.K_RIGHT:
                self.right()
            elif event.key == pygame.K_DOWN:
                self.step = (self.speed_max - self.speed) * 5
            elif event.key == pygame.K_LEFT:
                self.left()
            elif event.key == pygame.K_SPACE:
                self.pause = not self.pause
                if not self.alive:
                    self.reset()
            elif event.key == pygame.K_PAGEUP:
                self.speed = self.speed + 1 if self.speed < 10 else self.speed
            elif event.key == pygame.K_PAGEDOWN:
                self.speed = self.speed - 1 if self.speed > 1 else self.speed

    key_count = {}

    def key_press(self):
        key_pressed = pygame.key.get_pressed()
        if (key_pressed[pygame.K_a]) or (key_pressed[pygame.K_LEFT]):
            if self.key_count.get('LEFT', 0) >= self.speed_max - self.speed:
                self.key_count['LEFT'] = 0
                self.left()
            else:
                self.key_count['LEFT'] = self.key_count['LEFT'] + 1 if 'LEFT' in self.key_count else 1
        else:
            self.key_count['LEFT'] = 0
        if (key_pressed[pygame.K_d]) or (key_pressed[pygame.K_RIGHT]):
            if self.key_count.get('RIGHT', 0) >= self.speed_max - self.speed:
                self.key_count['RIGHT'] = 0
                self.right()
            else:
                self.key_count['RIGHT'] = self.key_count['RIGHT'] + 1 if 'RIGHT' in self.key_count else 1
        else:
            self.key_count['RIGHT'] = 0
        if (key_pressed[pygame.K_w]) or (key_pressed[pygame.K_UP]):
            if self.key_count.get('UP', 0) >= self.speed_max - self.speed:
                self.key_count['UP'] = 0
                self.up()
            else:
                self.key_count['UP'] = self.key_count['UP'] + 1 if 'UP' in self.key_count else 1
        else:
            self.key_count['UP'] = 0
        if key_pressed[pygame.K_s] or key_pressed[pygame.K_DOWN]:
            self.step = (self.speed_max - self.speed) * 5

    def loop(self):
        self.key_press()
        if self.alive and not self.pause:
            self.goes_down()
        self.caption = f"Tetris speed: {self.speed} score: {self.score} {('pause' if self.pause else '') if self.alive else 'die'}"
        self.draw_background()
        self.draw_fix_block()
        self.draw_item_block(self.item_active)
        self.draw_item_block(self.item_next)

    def up(self):
        item_new = self.item_active.rotate()
        if self.check_still(item_new):
            return
        if item_new.border[3] < 0:
            return
        if item_new.border[1] > self.pos_x_max:
            return
        self.item_active = item_new

    def right(self):
        if self.item_active.border[1] < self.pos_x_max:
            item_new = self.item_active.move('RIGHT')
            if not self.check_still(item_new):
                self.item_active = item_new

    def left(self):
        if self.item_active.border[3] > 0:
            item_new = self.item_active.move('LEFT')
            if not self.check_still(item_new):
                self.item_active = item_new

    def bingo_block(self, lines):
        block_static = copy(self.block_static)
        for block in block_static:
            if block[1] in lines:
                self.block_static.remove(block)
                # del block
            else:
                offset = 0
                for line in lines:
                    if block[1] < line:
                        offset += 1
                block[1] += offset

    def check_bingo(self, lines):
        bingo_line = []
        line_count = {}
        for block in self.block_static:
            line_count[block[1]] = line_count[block[1]] + 1 if block[1] in line_count else 1
        for line, count in line_count.items():
            if count >= 10:
                bingo_line.append(line)
        return bingo_line

    def still_block(self):
        tbc_line = set()
        for block in self.item_active.block:
            if block[1] == -1:
                self.alive = False
                return
            self.block_static.append(block)
            tbc_line.add(block[1])
        bingo_line = self.check_bingo(tbc_line)
        if bingo_line:
            self.bingo_block(bingo_line)
            self.score += len(bingo_line)
        self.item_active = self.item_next
        self.item_active.position = list(self.POSITION_NEW)
        self.item_active.position[1] = self.item_active.border[0] - self.item_active.border[2] - 1
        self.item_next = Item(self.POSITION_NEXT)

    def check_still(self, item):
        if item.border[2] > self.pos_y_max:
            return True
        for block in item.block:
            if block[:-1] in [x[:-1] for x in self.block_static]:
                return True

    def goes_down(self):
        self.step += 1
        if self.step >= (self.speed_max - self.speed) * 3:
            self.step = 0
            item_new = self.item_active.move('DOWN')
            if self.check_still(item_new):
                self.still_block()
            else:
                self.item_active = item_new

    def draw_background(self):
        self.screen.fill(BLACK)
        plan_margin = self.BLOCK_SIZE * 0.5
        pygame.draw.rect(self.screen, WHITE, (
            (plan_margin, plan_margin), (self.plan_width - plan_margin * 2, self.plan_height - plan_margin * 2)
        ))
        plan_margin = self.BLOCK_SIZE * 0.9
        pygame.draw.rect(self.screen, BLACK, (
            (plan_margin, plan_margin), (self.plan_width - plan_margin * 2, self.plan_height - plan_margin * 2)
        ))

    def draw_block(self, pos):
        x, y = (pos[0] + 1) * self.BLOCK_SIZE, (pos[1] + 1) * self.BLOCK_SIZE
        pygame.draw.rect(self.screen, BLACK, (
            (x, y), (self.BLOCK_SIZE, self.BLOCK_SIZE)
        ))
        margin = self.BLOCK_SIZE * 0.1
        pygame.draw.rect(self.screen, pos[2], (
            (x + margin, y + margin), (self.BLOCK_SIZE - margin * 2, self.BLOCK_SIZE - margin * 2)
        ))

    def draw_fix_block(self):
        for block_pos in self.block_static:
            self.draw_block(block_pos)

    def draw_item_block(self, item):
        for block in item.block:
            self.draw_block(block)


tetris = Tetris([480, 640], "Tetris")
tetris.run_forever()
