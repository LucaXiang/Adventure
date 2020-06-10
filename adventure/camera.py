import pygame


CAMERA_GIRD_COLOR = (0, 0, 150)


class Camera:
    pos = None
    scale = 1
    window = None
    canvas = None
    width = 0
    height = 0
    surface = None

    rect = None
    offset_x = 0
    offset_y = 0
    block_size = 0

    def __init__(self, scale, pos, window, canvas, block_size):
        self.scale = scale
        px, py = pos
        self.pos = {'x': px, 'y': py}
        self.window = window
        self.canvas = canvas
        self.block_size = block_size
        self.set_scale(scale)


    def set_scale(self, scale):
        if scale < 0.01:
            return
        w, h = self.window
        self.width  = (w * scale);
        self.height = (h * scale);
        self.scale = scale
        self.surface = pygame.Surface((self.width, self.height))
        self.update_camera_rect()
        self.update_offset()

    def update_offset(self):
        cw, ch = self.canvas
        ww, wh = self.window
        rect = self.rect;

        if rect.w > ww or rect.w >= cw:
            self.offset_x = round(max((ww - (rect.w / self.scale)) / 2, 0))
        else:
            self.offset_x = 0

        if rect.h > wh or rect.h >= ch:
            self.offset_y = round(max((wh - (rect.h / self.scale)) / 2, 0))
        else:
            self.offset_y = 0

    def update_camera_rect(self):
        pos = self.pos
        w, h = self.canvas
        temp_x = (pos['x'] - (self.width / 2))
        temp_y = (pos['y'] - (self.height / 2))
        rect_x = temp_x
        rect_y = temp_y

        if temp_x < 0 or temp_x > (w - self.width):
            rect_x = 0 if temp_x < 0 else max(w - self.width, 0)

        if temp_y < 0 or temp_y > (h - self.height):
            rect_y = 0 if temp_y < 0 else max(h - self.height, 0)

        rect_w = w if self.width > w else self.width
        rect_h = h if self.height > h else self.height

        self.rect = pygame.Rect(rect_x, rect_y, rect_w, rect_h)

    def get_mouse_hover_point(self):
        block_size = self.block_size
        mx, my = pygame.mouse.get_pos();
        scaled_size = block_size / self.scale
        bx = int(((mx - self.offset_x) + self.rect.x / self.scale) / scaled_size)
        by = int(((my - self.offset_y) + self.rect.y / self.scale) / scaled_size)
        return bx, by

    def get_camere_block(self):
        block_size = self.block_size
        x = int(self.rect.x / block_size)
        y = int(self.rect.y / block_size)
        c_w = (self.rect.x + self.rect.w)
        c_h = (self.rect.y + self.rect.h)
        c_w1 = int(c_w / block_size) - x
        c_h1 = int(c_h / block_size) - y
        w = c_w1 + 1 if ((c_w1 % block_size) != 0) else c_w1
        h = c_h1 + 1 if ((c_h1 % block_size) != 0) else c_h1
        return x - 1, y - 1, w + 1, h + 1

    def draw_camera_gird(self, canvas):
        block_size = self.block_size
        x, y, w, h = self.get_camere_block()
        for i in range(0, w + 1):
            offset = x + i
            pygame.draw.line(canvas, CAMERA_GIRD_COLOR, (offset * block_size, y * block_size),
                             (offset * block_size, (y + h) * block_size), 1)
        for i in range(0, h + 1):
            offset = y + i
            pygame.draw.line(canvas, CAMERA_GIRD_COLOR, (x * block_size, offset * block_size),
                             ((x + w) * block_size, offset * block_size), 1)
