import json
import random
import pygame
import os
from adventure import clock
from adventure import camera
from adventure import texture
from adventure import character
from bintrees import rbtree

FULL_SCREEN_FLAG = pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF;

BGCOLOR = (54, 143, 203)
GRAVITY = 800


class Adventure:
    initialized = False
    ready = False

    window_width = 0;
    window_height = 0;
    canvas_width = 0;
    canvas_height = 0;

    screen = None
    font = None
    clock = None
    level = None
    canvas = None
    ui = None
    draw_ui = False

    delay = 0;

    done = False

    scale = 1
    camera = None
    default_camera = None
    debug_camera = None

    world_col = 64
    world_row = 64
    block_size = 32

    debug = False

    world = None
    blocks = None

    texture = texture.Texture("res/texture")

    start_point = None

    # tmp for test
    # ------------------------------
    dir = 0
    background = []
    camera_background = []

    ch = None

    def init(self, config_obj):

        if not self.initialized:
            if os.name == 'nt':
                # is current os is windows fix dpi
                import ctypes
                ctypes.windll.user32.SetProcessDPIAware()

            # window config
            # ---------------------------------------------------------------------

            window_config = config_obj["window"]
            full_screen = window_config["fullScreen"]
            window_width = window_config["width"] if full_screen else window_config["width"];
            window_height = window_config["height"] if full_screen else window_config["height"];
            window_flag = FULL_SCREEN_FLAG if full_screen else 0

            # font config
            # ---------------------------------------------------------------------

            font_config = config_obj["font"]
            font_family = font_config["family"]
            font_size = font_config["size"]

            # clock config
            # ---------------------------------------------------------------------
            max_fps = config_obj['fps']
            self.clock = clock.GameClock(max_fps)

            # ui
            # ---------------------------------------------------------------------
            self.ui = pygame.Surface((window_width, window_height))

            # level
            # ---------------------------------------------------------------------
            self.level = config_obj['mainLevel']
            # init pygame
            pygame.init()

            # init font module
            pygame.font.init()

            self.screen = pygame.display.set_mode((window_width, window_height), window_flag)
            self.window_width, self.window_height = self.screen.get_size();

            self.font = pygame.font.SysFont(font_family, font_size)

            self.load_level(self.level)
            self.initialized = True
            self.dir = 4

    def start(self):
        self.clock.tick()
        while not self.done:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.done = True;
                    continue;
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_F8:
                        self.debug = not self.debug
                        if self.debug:
                            self.camera = self.debug_camera
                            self.camera.pos = self.default_camera.pos
                            self.camera.update_camera_rect()
                        else:
                            self.camera = self.default_camera
                    if event.key == pygame.K_r:
                        self.restart()
                        break

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.debug:
                        if event.button == 4 or event.button == 5:
                            delta = -0.01 if event.button == 4 else 0.01
                            self.debug_camera.set_scale(self.debug_camera.scale + delta)
                            self.screen.fill((0, 0, 0))

            if not self.ready:
                continue

            vx = self.lerp(self.default_camera.pos['x'], self.ch.x, 10 * self.delay)
            vy = self.lerp(self.default_camera.pos['y'], self.ch.y, 10 * self.delay)

            self.default_camera.pos["x"] = vx
            self.default_camera.pos["y"] = vy
            self.default_camera.update_camera_rect()
            self.draw_camera_background()
            self.draw_blocks()
            self.draw_background()
            self.ch.handle(pygame.key.get_pressed())
            self.ch.update(self.delay)
            self.ch.draw(self.canvas)

            # ------ debug ------ #
            if self.debug:
                self.default_camera.draw_camera_gird(self.canvas)
                px, py = self.debug_camera.get_mouse_hover_point();
                pygame.draw.rect(self.canvas, (255, 0, 0),
                                 (px * self.block_size, py * self.block_size, self.block_size, self.block_size), 2)
                pygame.draw.rect(self.canvas, (0, 255, 0), self.default_camera.rect, 2)

            self.camera.surface.blit(self.canvas.subsurface(self.camera.rect), (0, 0))

            self.screen.blit(pygame.transform.smoothscale(self.camera.surface, (self.window_width, self.window_height)),
                             (self.camera.offset_x, self.camera.offset_y))

            self.screen.blit(self.font.render(str(self.clock.get_fps()), True, (255, 0, 0)), (0, 0))
            pygame.display.update()
            if self.camera.offset_x > 0 or self.camera.offset_y > 0:
                self.screen.fill((0, 0, 0))
            pygame.draw.rect(self.canvas, BGCOLOR, self.default_camera.rect, 0)
            self.delay = self.clock.tick()

    def load_level(self, level):

        level_file_name = "./level/" + level;
        level_file = open(level_file_name, "r")
        level_obj = json.load(level_file)
        self.world_row = level_obj['worldRow']
        self.world_col = level_obj['worldCol']
        self.block_size = level_obj['blockSize']
        self.scale = level_obj['scale']
        self.canvas = pygame.Surface(((self.world_col * self.block_size) + 1, (self.world_row * self.block_size) + 1))
        self.canvas_width, self.canvas_height = self.canvas.get_size()

        self.default_camera = camera.Camera(self.scale,
                                            (self.canvas_width, self.canvas_height),
                                            (self.window_width, self.window_height),
                                            (self.canvas_width, self.canvas_height), self.block_size)
        self.debug_camera = camera.Camera(1,
                                          (self.canvas_width / 2, self.canvas_height),
                                          (self.window_width, self.window_height),
                                          (self.canvas_width, self.canvas_height), self.block_size)

        self.camera = self.default_camera
        self.camera.update_camera_rect()
        self.start_point = level_obj["start"]
        self.ch = character.Character(self.start_point["x"], self.start_point["y"], 32, 32)

        self.default_camera.pos['x'] = self.ch.x;
        self.default_camera.pos['y'] = self.ch.y;

        self.background = []
        self.camera_background = []
        self.world = rbtree.RBTree()
        self.blocks = level_obj["blocks"]
        index = 0
        for block in self.blocks:
            self.new_block(block, index)
            index += 1
        self.ready = True

        for bg in level_obj["camera_background"]:
            x = self.default_camera.rect.w * bg["x"]
            y = self.default_camera.rect.h * bg["y"]
            key = bg["key"]
            self.camera_background.append((x, y, key))

    def new_block(self, block, block_id):

        x = block['x']
        y = block['y']
        w = block['w']
        h = block['h']
        for row in range(0, h):
            for col in range(0, w):
                pos_y = y + row
                if pos_y not in self.world:
                    self.world.insert(pos_y, rbtree.RBTree())
                row_tree = self.world[pos_y]
                pos_x = x + col
                row_tree.insert(pos_x, block_id)
                if "gen" in block:
                    obj = block["gen"]
                    prob = 0 if "prob" not in block else block["prob"]
                    if random.randint(0, 100) < prob:
                        index = random.randint(0, len(obj) - 1)
                        self.background.append((pos_x + obj[index]["x"], pos_y + obj[index]["y"], obj[index]["key"]))

    def get_block_id(self, x, y):
        result = None
        if y in self.world:
            if x in self.world[y]:
                result = self.world[y][x]
        return result

    def draw_blocks(self):
        camera_block = pygame.Rect(self.default_camera.get_camere_block())
        for block in self.blocks:
            x = block['x']
            y = block['y']
            w = block['w']
            h = block['h']
            init_x = x * self.block_size
            init_y = y * self.block_size
            t = self.texture.get_texture(block["name"])
            if camera_block.colliderect((x, y, w, h)):
                if block['draw'] == "fill":
                    self.canvas.blit(t, (init_x, init_y))
                elif block['draw'] == "repeat":
                    offset_y = 0
                    while offset_y < h:
                        offset_x = 0
                        while offset_x < w:
                            if camera_block.collidepoint(x + offset_x, y + offset_y):
                                pos_x = init_x + offset_x * self.block_size
                                pos_y = init_y + offset_y * self.block_size
                                self.canvas.blit(t, (pos_x, pos_y))
                            offset_x += 1
                        offset_y += 1

    def draw_background(self):
        camera_block = pygame.Rect(self.default_camera.get_camere_block())
        for shit in self.background:
            x, y, key = shit
            t = self.texture.get_texture(key)
            if camera_block.collidepoint(x, y):
                self.canvas.blit(t, (x * self.block_size, (y * self.block_size)))

    def draw_camera_background(self):
        for bg in self.camera_background:
            x, y, key = bg
            t = self.texture.get_texture(key)
            self.canvas.blit(t, (self.default_camera.rect.x + x, self.default_camera.rect.y + y))

    @staticmethod
    def lerp(v1, v2, f):
        return v1 + ((v2 - v1) * f)

    def restart(self):
        self.ch.x = self.start_point["x"]
        self.ch.y = self.start_point["y"]
        self.ch.vx = 0
        self.ch.vy = 0


default = Adventure()
