import os
import pygame


class Texture:
    texture_dict =  {}
    path = None

    def __init__(self, path):
        self.path = path

    def get_texture(self, key, reverse=False):
        if (key, reverse) not in self.texture_dict:
            image_path = self.path + "/" + key + ".png"
            if os.path.isfile(self.path + "/" + key + ".png"):
                p = pygame.image.load(image_path)
                s =  p if not reverse else pygame.transform.flip(p, True, False)
                self.texture_dict[(key, reverse)] = s
            else:
                return None
        return self.texture_dict[(key, reverse)]
