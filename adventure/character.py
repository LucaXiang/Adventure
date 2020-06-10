import pygame
import adventure


LEFT_BLOCK = [[1, 0]]
RIGHT_BLOCK = [[-1, 0]]
TOP_BLOCK = [[0, 1]]
BOTTOM_BLOCK = [[0, -1]]

ALL_BLOCK = LEFT_BLOCK + RIGHT_BLOCK + TOP_BLOCK + BOTTOM_BLOCK



SPRITE_FALL = "fall"
SPRITE_JUMP = "jump"
SPRITE_DJUMP = "djump"
SPRITE_IDLE = "idle"
SPRITE_RUN = "run"

MOV_SPEED = 320
JUMP_POWER = 380
DJUMP_POWER = 280


class Character:
    w = 0
    h = 0

    x = 0
    y = 0

    vx = 0
    vy = 0

    status = None
    sprite = None
    delay  = 0

    target = None
    last_y = -99999999
    last_blocks = None
    last_test   = None

    djump = True

    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.status = StatusIdle()
        self.sprite = SPRITE_IDLE
        self.last_test = LEFT_BLOCK


    def handle(self, inputs):
        self.status.handle(self, inputs)
        self.vx = 0
        if inputs[pygame.K_a]:
            self.vx = -MOV_SPEED
        elif inputs[pygame.K_d]:
            self.vx = MOV_SPEED

    def update(self, delay):
        self.delay = delay
        self.status.update(self, delay)
        dvx = (self.vx * delay)
        if dvx != 0.0000:
            test = LEFT_BLOCK if dvx < 0 else RIGHT_BLOCK
            self.last_test = test
        else:
            test = self.last_test
        self.update_target(test)
        if self.target is not None:
            size = adventure.default.block_size
            x, y = self.target
            t_x  = (((x + 1) * size + 1) if dvx < 0 else (x *  size) - 1)
            w    = 0 if dvx < 0 else self.w

            if test == LEFT_BLOCK:
                if (self.x + dvx) - t_x < 0:
                    self.x = t_x - w
                    dvx = 0
            else:
                if (self.x + w + dvx) - t_x > 0:
                    self.x = t_x - w
                    dvx = 0
        self.x += dvx
        self.y += (self.vy * delay)

    def draw(self, canvas):
        r = self.last_test == LEFT_BLOCK
        if self.status.name == "idle" or self.status.name == "run" or self.status.name == "djump":
            i = self.status.index % self.status.count
            p = adventure.default.texture.get_texture(self.sprite, r)
            s = p.subsurface((i * self.w, 0, self.w, self.h))
        else:
            s = adventure.default.texture.get_texture(self.sprite, r)
        canvas.blit(s, (self.x, self.y))
        if self.target is not None:
            x, y = self.target
            pygame.draw.rect(adventure.default.canvas, (100, 0, 0), (x * 32, y * 32, 32, 32))

    def get_current_block(self):
        block_size = adventure.default.block_size
        x = self.x / block_size
        y = self.y / block_size
        c_w = self.x + self.w
        c_h = self.y + self.h
        c_w1 = c_w / block_size - x
        c_h1 = c_h / block_size - y
        w = c_w1 + 1 if ((c_w % block_size) > 0.5) else c_w1
        h = c_h1 + 1 if ((c_h % block_size) > 0.5) else c_h1
        return pygame.Rect(x, y, w, h)

    def get_surrounding_block(self, test):

        r = self.get_current_block()
        test_w = range(-1, r.w * 2)
        test_h = range(-1, r.h * 2)
        result = []
        for offset_y in range(0, r.h * 2 + r.h % 2):
            pos_y = r.y + test_h[offset_y]
            for offset_x in range(0, r.w * 2 + r.w % 2):
                pos_x = r.x + test_w[offset_x]
                for t in test:
                    mx, my = t
                    if r.collidepoint(pos_x + mx, pos_y + my):
                        result.append((pos_x, pos_y))
        return result

    def update_target(self, test):
        self.last_blocks = self.get_surrounding_block(test)
        adventure.default.draw_blocks()
        self.target = None
        flag = False;
        for block in self.last_blocks:
            x, y = block
            b = adventure.default.get_block_id(x, y)
            if b is not None and flag is False:
                self.target = block
                flag = True
                x, y = block
                pygame.draw.rect(adventure.default.canvas, (0, 100, 0), (x * 32, y * 32, 32, 32))

    def on_collision(self, b_id):
        block = adventure.default.blocks[b_id]
        if "collision" in block:
            if block["collision"] == "died":
                adventure.default.restart()
            elif block["collision"] == "jump":
                self.status = StatusDJump()
                self.sprite = SPRITE_DJUMP
                self.djump = False
                self.vy = -600
        if "transport" in block:
            adventure.default.load_level(block["transport"])


class StatusIdle:
    name = "idle"
    index = 0
    count = 11
    delay_sum = 0

    def handle(self, instance, inputs=None):
        if inputs is not None:
            if inputs[pygame.K_w]:
                instance.status = StatusJump()
                instance.sprite = SPRITE_JUMP
                instance.vy = -JUMP_POWER
            if inputs[pygame.K_d] or inputs[pygame.K_a]:
                instance.status = StatusRun()
                instance.sprite = SPRITE_RUN

    def update(self, instance, delay):

        if self.delay_sum > 0.05:
            self.index += 1;
            self.delay_sum = 0
        self.delay_sum += delay
        block = instance.get_surrounding_block(BOTTOM_BLOCK)
        fall = True
        for b in block:
            x, y = b
            b_id = adventure.default.get_block_id(x, y)
            if b_id is not None:
                instance.on_collision(b_id)
                fall = False
        if fall:
            instance.vy = 10
            instance.status = StatusFall()
            instance.sprite = SPRITE_FALL



class StatusJump:
    name = "jump"
    target = None
    release = False
    def handle(self, instance, inputs=None):
        if inputs is not None:
            if inputs[pygame.K_w]:
                if self.release and instance.djump:
                    instance.status = StatusDJump()
                    instance.sprite = SPRITE_DJUMP
                    instance.vy = -DJUMP_POWER
                    instance.djump = False
            else:
                self.release = True

    def update(self, instance, delay):
        instance.vy += (adventure.GRAVITY * delay)
        if instance.vy > 0:
            instance.status = StatusFall()
            instance.sprite = SPRITE_FALL

        else:
            self.update_target(instance)
            if self.target is not None:
                size = adventure.default.block_size
                x, y = self.target
                t_y = (y + 1) * size
                if (instance.y  - (adventure.GRAVITY * delay)) - t_y < 0:
                    instance.y = t_y + 1
                    instance.status = StatusFall()
                    instance.sprite = SPRITE_FALL
                    b = adventure.default.get_block_id(x, y)
                    instance.on_collision(b)
                    instance.vy = 1

    def update_target(self, instance):
        blocks = instance.get_surrounding_block(TOP_BLOCK)
        self.target = None
        for block in blocks:
            x, y = block
            b = adventure.default.get_block_id(x, y)
            if b is not None:
                self.target = block
                break


class StatusFall:
    name = "fall"
    target = None
    def handle(self, instance, inputs=None):
        if inputs is not None:
            if inputs[pygame.K_w] and instance.djump:
                instance.status = StatusDJump()
                instance.sprite = SPRITE_DJUMP
                instance.vy = -DJUMP_POWER
                instance.djump = False

    def update(self, instance: Character, delay):
        instance.vy += (adventure.GRAVITY * delay)
        self.update_target(instance)
        size = adventure.default.block_size
        if self.target is not None:
            x, y = self.target
            t_y = y * size
            if ((instance.y + instance.h) + (adventure.GRAVITY * delay)) - t_y > 0:
                instance.y = t_y - instance.h - 1
                instance.status = StatusIdle()
                instance.sprite = SPRITE_IDLE
                instance.djump = True
                instance.vy = 0

    def update_target(self, instance):
        blocks = instance.get_surrounding_block(BOTTOM_BLOCK)
        self.target = None
        for block in blocks:
            x, y = block
            b = adventure.default.get_block_id(x, y)
            if b is not None:
                self.target = block
                break


class StatusRun:
    name = "run"
    index = 0
    count = 12
    delay_sum = 0

    def handle(self, instance, inputs=None):
        if inputs is not None:
            if inputs[pygame.K_w]:
                instance.status = StatusJump()
                instance.sprite = SPRITE_JUMP
                instance.vy = -JUMP_POWER
            elif not inputs[pygame.K_a] and not inputs[pygame.K_d]:
                instance.status = StatusIdle()
                instance.sprite = SPRITE_IDLE

    def update(self, instance, delay):

        if self.delay_sum > 0.05:
            self.index += 1;
            self.delay_sum = 0
        self.delay_sum += delay
        block = instance.get_surrounding_block(BOTTOM_BLOCK)
        fall = True
        for b in block:
            x, y = b
            b_id = adventure.default.get_block_id(x, y)
            if b_id is not None:
                fall = False
                instance.on_collision(b_id)
        if fall:
            instance.vy = 10
            instance.status = StatusFall()
            instance.sprite = SPRITE_FALL


class StatusDJump:

    name = "djump"
    index = 0
    count = 6
    delay_sum = 0
    target = None


    def handle(self, instance, inputs):
        pass

    def update(self, instance, delay):
        if self.delay_sum > 0.05:
            self.index += 1;
            self.delay_sum = 0
        self.delay_sum += delay
        instance.vy += (adventure.GRAVITY * delay)
        if instance.vy > 0:
            instance.status = StatusFall()
            instance.sprite = SPRITE_FALL
        else:
            self.update_target(instance)
            if self.target is not None:
                size = adventure.default.block_size
                x, y = self.target
                t_y = (y + 1) * size
                if (instance.y - (adventure.GRAVITY * delay)) - t_y < 0:
                    b = adventure.default.get_block_id(x, y)
                    instance.on_collision(b)
                    instance.y = t_y + 1
                    instance.status = StatusFall()
                    instance.sprite = SPRITE_FALL
                    instance.vy = 1

    def update_target(self, instance):
        blocks = instance.get_surrounding_block(TOP_BLOCK)
        self.target = None
        for block in blocks:
            x, y = block
            b = adventure.default.get_block_id(x, y)
            if b is not None:
                self.target = block
                break
