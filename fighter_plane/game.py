from random import randint

import pyglet
from cocos.actions import MoveBy, CallFunc, Repeat, Delay
from cocos.director import director
from cocos.layer import Layer
from cocos.scene import Scene
from cocos.sprite import Sprite

BUTTON_LEFT = 0x00000001
BUTTON_MIDDLE = 0x00000002
BUTTON_RIGHT = 0x00000004

Z_Plane = 3
Z_Bullet = 2
Z_Background = 1

WIDTH = 480
HEIGHT = 800


class Bullet(Layer):
    is_event_handler = True

    def __init__(self, ):
        super(Bullet, self).__init__()

    def creat(self, position, rotation, speed):
        image = pyglet.resource.image('bullet_205px_1235397_easyicon.net.png')
        sprite = Sprite(image, position=position, rotation=rotation, scale=0.03)
        self.add(sprite)

        length = HEIGHT - sprite.position[1] if rotation == 0 else -sprite.position[1]
        action = MoveBy((0, length), duration=abs(length) / speed)
        action.stop = lambda: self.remove(sprite)
        sprite.do(action)


class Enemy(Layer):
    def __init__(self):
        super(Enemy, self).__init__()
        # 定义动作 生成敌人+延时1秒
        action = CallFunc(self.creat) + Delay(1)
        # 重复运行动作
        self.do(Repeat(action))

    def creat(self):
        image = pyglet.resource.image('airplane_625px_1234720_easyicon.net.png')
        sprite = Sprite(image, (randint(24, WIDTH - 24), HEIGHT), rotation=180, scale=0.1)
        sprite.health = 5
        self.add(sprite)

        fire = Repeat(Delay(0.5) + CallFunc(self.fire, sprite))
        sprite.do(fire)

        length = -sprite.position[1]
        move = MoveBy((0, length), duration=abs(length) / (200 / 1))
        move.stop = lambda: self.remove(sprite)
        sprite.do(move)

    def fire(self, sprite):
        x, y = sprite.position
        bullet_layer.creat([x, y], 180, (300 / 1))


class Oneself(Layer):
    # 开启事件处理
    is_event_handler = True

    def __init__(self):
        super(Oneself, self).__init__()
        self.position = (WIDTH / 2, 0 + 100)

        self.sprite = Sprite('airplane_710px_1219057_easyicon.net.png', scale=0.1)
        self.add(self.sprite)

        # self.cshape = cm.AARectShape(eu.Vector2(self.anchor_x, self.anchor_y), self.anchor_x, self.anchor_y)

        fire = Repeat(Delay(0.2) + CallFunc(self.fire))
        self.do(fire)

    def on_mouse_motion(self, x, y, dx, dy):
        self.move(*director.get_virtual_coordinates(x, y))

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.move(*director.get_virtual_coordinates(x, y))

    def move(self, x, y):
        self.position = (x, self.position[1])

    def fire(self):
        x, y = self.position
        # bullet_layer.creat([x - 26, y + 18], 0, 420 / 1)
        # bullet_layer.creat([x - 16, y + 25], 0, 420 / 1)
        # bullet_layer.creat([x + 16, y + 25], 0, 420 / 1)
        # bullet_layer.creat([x + 26, y + 18], 0, 420 / 1)
        bullet_layer.creat([x, y + 50], 0, 420 / 1)


class Background(Layer):
    def __init__(self):
        super(Layer, self).__init__()

        self.schedule(self.callback)

    def callback(self, *args, **kwargs):
        enemy_removed = set()
        for enemy in enemy_layer.get_children():
            left = enemy.x - enemy.width
            right = enemy.x + enemy.width
            top = enemy.y + enemy.height
            bottom = enemy.y - enemy.height
            bullet_removed = set()
            for bullet in bullet_layer.get_children():
                if bullet.rotation == 0:
                    if left < bullet.x < right and bottom < bullet.y < top:
                        bullet_removed.add(bullet)
                        enemy.health -= 1
                        if enemy.health <= 0:
                            enemy_removed.add(enemy)

            for bullet in bullet_removed:
                bullet.to_remove = bullet.actions
                bullet_layer.remove(bullet)
        for enemy in enemy_removed:
            enemy.to_remove = enemy.actions
            enemy_layer.remove(enemy)
        bullet_removed = set()
        oneself = oneself_layer.get_children()[0]
        left = oneself_layer.x - oneself.width
        right = oneself_layer.x + oneself.width
        top = oneself_layer.y + oneself.height
        bottom = oneself_layer.y - oneself.height
        for bullet in bullet_layer.get_children():
            if bullet.rotation == 180:
                if left < bullet.x < right and bottom < bullet.y < top:
                    bullet_removed.add(bullet)
                    print('die')
        for bullet in bullet_removed:
            bullet.to_remove = bullet.actions
            bullet_layer.remove(bullet)


director.init(width=WIDTH, height=HEIGHT)
# 定义主场景
main_scene = Scene()
# 定义层次
background_layer = Background()
oneself_layer = Oneself()
enemy_layer = Enemy()
bullet_layer = Bullet()
# 向主场景添加元素
main_scene.add(background_layer, z=Z_Background)
main_scene.add(oneself_layer, z=Z_Plane)
main_scene.add(enemy_layer, z=Z_Plane)
main_scene.add(bullet_layer, z=Z_Bullet)
# 运行主场景
director.run(main_scene)
