import random
import sys

import pygame
# from pygame.examples.glcube import CUBE_COLORS
from pygame.event import EventType
from pygame.locals import *

# Initialize the game engine
pygame.init()
pygame.font.init()

# Define the colors we will use in RGB format
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# Set the height and width of the screen
size = [640, 480]
screen = pygame.display.set_mode(size)

caption_show = "snake"
pygame.display.set_caption(caption_show)

# Loop until the user clicks the close button.
done = False
clock = pygame.time.Clock()

BLOCK_SIZE = 18
PLANT_SIZE = 20
CHINK_SIZE = (PLANT_SIZE - BLOCK_SIZE) / 2

speed = 0
sleep = False
alive = True
arrow_new = arrow = 'ARROW_R'
food_x, food_y = PLANT_SIZE, PLANT_SIZE
head_x, head_y = PLANT_SIZE, PLANT_SIZE
snake_length = 0
snake_body = []

caption = f"snake speed: {speed} score: {snake_length}"

step = 0
while True:
    clock.tick(60)
    event: EventType
    for event in pygame.event.get():
        assert isinstance(event.type, int)
        if event.type in (QUIT, QUIT):
            sys.exit()
        if event.type in (KEYDOWN, KEYDOWN):
            if event.key == pygame.K_RIGHT:
                arrow_new = 'ARROW_R' if arrow != 'ARROW_L' else arrow_new
            elif event.key == pygame.K_DOWN:
                arrow_new = 'ARROW_D' if arrow != 'ARROW_U' else arrow_new
            elif event.key == pygame.K_LEFT:
                arrow_new = 'ARROW_L' if arrow != 'ARROW_R' else arrow_new
            elif event.key == pygame.K_UP:
                arrow_new = 'ARROW_U' if arrow != 'ARROW_D' else arrow_new
            elif event.key == pygame.K_SPACE:
                sleep = not sleep
                if not alive:
                    sleep = False
                    alive = True
                    arrow_new = arrow = 'ARROW_R'
                    food_x, food_y = PLANT_SIZE, PLANT_SIZE
                    head_x, head_y = PLANT_SIZE, PLANT_SIZE
                    snake_length = 0
                    snake_body = []
            elif event.key == pygame.K_PAGEUP:
                speed = speed + 1 if speed < 10 else speed
            elif event.key == pygame.K_PAGEDOWN:
                speed = speed - 1 if speed > 1 else speed

    # 更新标题
    caption = f"snake speed: {speed} score: {snake_length} {('pause' if sleep else '') if alive else 'die'}"
    if caption_show != caption:
        pygame.display.set_caption(caption)
        caption_show = caption

    # 更新画面
    screen.fill(BLACK)
    pygame.draw.rect(screen, BLUE, (food_x + CHINK_SIZE, food_y + CHINK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
    for x, y in snake_body:
        pygame.draw.rect(screen, WHITE, (x + CHINK_SIZE, y + CHINK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
    head_color = GREEN if alive else RED
    pygame.draw.rect(screen, head_color, (head_x + CHINK_SIZE, head_y + CHINK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
    pygame.display.update()

    # 游戏停止控制
    if not alive or sleep:
        continue

    # 速度控制
    step += 1
    if step % (11 - speed) == 0:
        step = 0
        arrow = arrow_new if arrow != arrow_new else arrow
        # 生成食物
        if (food_x, food_y) in [(head_x, head_y)] + snake_body:
            food_x = random.randint(0, (size[0] / PLANT_SIZE) - 1) * PLANT_SIZE
            food_y = random.randint(0, (size[1] / PLANT_SIZE) - 1) * PLANT_SIZE

        # 蛇走一步
        if arrow == 'ARROW_R':
            next_x, next_y = head_x + PLANT_SIZE, head_y
        elif arrow == 'ARROW_D':
            next_x, next_y = head_x, head_y + PLANT_SIZE
        elif arrow == 'ARROW_L':
            next_x, next_y = head_x - PLANT_SIZE, head_y
        elif arrow == 'ARROW_U':
            next_x, next_y = head_x, head_y - PLANT_SIZE
        else:
            next_x, next_y = head_x, head_y

        # 碰撞墙壁
        if next_x < 0 or next_y < 0 or next_x > size[0] - 1 or next_y > size[1] - 1:
            alive = False
            continue

        # 碰撞身体
        if (next_x, next_y) in snake_body[:-1]:
            alive = False
            continue

        # 吃到食物
        if (next_x, next_y) == (food_x, food_y):
            snake_length += 1

        # 移动身体
        snake_body.insert(0, (head_x, head_y))
        while len(snake_body) > snake_length:
            snake_body.pop()
        head_x, head_y = next_x, next_y
