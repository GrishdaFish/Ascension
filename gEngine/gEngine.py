# #Python prototype for the c++ pyd
##Basicly a wrapper around libtcod, like the pyd is
##Used incase the pyd is absent so the code wont break.
##pretty much a c++ port, not very pythonic, doesnt need to be.
##Might clean it up later

import libtcodpy as libtcod
import logging
import sys
import light_mask
#import numpy
import particle
import draw

def in_rect(x, y, w, h):
    return x < w and y < h


class Tile:
    def __init__(self, x=0, y=0, cell='#', blocked=True, block_sight=True,
                 explored=False, spawn_node=None, color=(0, 0, 0), opacity=1.0):
        self.x = x
        self.y = y
        self.cell = cell
        self.blocked = blocked
        self.block_sight = block_sight
        self.explored = explored
        self.spawn_node = spawn_node
        self.color = color
        self.opacity = opacity


class LightSource:
    def __init__(self, x, y, color, radius, intensity, name='light'):
        self.x = x
        self.y = y
        self.color = color
        self.radius = radius
        self.intensity = intensity  # how much the light flickers
        self.flicker = 0
        self.name = name
        self.minx = 0
        self.miny = 0
        self.maxx = 0
        self.maxy = 0
        self.offset = 0
        self.factor = 0
        self.coef = 0

        self.pre_compute()

    def update(self):
        self.pre_compute()

    def pre_compute(self):
        self.minx = self.x - self.radius
        self.miny = self.y - self.radius
        self.maxx = self.x + self.radius
        self.maxy = self.y + self.radius
        self.offset = self.intensity / (1.0 + float(self.radius * self.radius) / 40)
        self.factor = self.intensity / (1.0 - self.offset)


class gEngine:
    def __init__(self, w, h, name, fs, fps):
        self.w = w
        self.h = h

        self.name = name
        self.fs = fs
        self.fps = fps

        self.mConsole = []
        self.mMap = []
        self.mMap2x = []
        self.mImages = []
        self.FOV = None
        self.numpy_list_2x = None
        self.color_dark_wall = libtcod.darkest_grey
        self.color_light_wall = libtcod.Color(99, 99, 99)
        self.color_dark_ground = libtcod.darker_grey
        self.color_light_ground = libtcod.Color(125, 125, 125)
        self.color_tile_wall = libtcod.Color(177, 177, 177)
        self.color_tile_ground = libtcod.Color(190, 190, 190)

        self.map_image = self.image_new(w, h)
        self.subcell_map_image = self.image_new(w * 2, h * 2)

        self.light_map = self.image_new(w, h)
        self.subcell_light_map = self.image_new(w * 2, h * 2)

        self.light_sources = []
        self.noise = libtcod.noise_new(1, libtcod.NOISE_SIMPLEX)

        self.light_mask = light_mask.LightMask(w, 43)

        self.particles = []

        #self.init_root()

    def run(self):
        pass

    def add_light_source(self, x, y, c, r, i, n='light'):
        self.light_sources.append(LightSource(x, y, c, r, i, n))

    def init_root(self):
        libtcod.console_init_root(self.w, self.h, self.name, self.fs)
        libtcod.sys_set_fps(self.fps)

    def console_set_key_color(self, con, r, g, b):
        col = libtcod.Color(r, g, b)
        if con == 0:
            libtcod.console_set_key_color(con, col)
        else:
            libtcod.console_set_key_color(self.mConsole[con - 1], col)

    #@staticmethod
    def console_set_custom_font(self, font_file, flags=libtcod.FONT_LAYOUT_ASCII_INCOL, h=0, v=0):
        font_file = font_file.replace('core.exe', '')
        libtcod.console_set_custom_font(font_file, flags, h, v)

    def console_new(self, width, height):
        self.mConsole.append(libtcod.console_new(width, height))
        return len(self.mConsole) # return the index instead of the object to allow lower level implementation

    def console_remove_console(self, con):
        if con > 1:  # so we dont try to delete root, or index oob error
            c = self.mConsole.pop(con - 1)
            libtcod.console_delete(c)

    def console_get_height_rect(self, con, x, y, width, height, fmt):
        if con == 0:
            return libtcod.console_get_height_rect(con, x, y, width, height, fmt)
        else:
            return libtcod.console_get_height_rect(self.mConsole[con - 1], x, y, width, height, fmt)

    def console_set_default_foreground(self, con, r, g, b):
        col = libtcod.Color(r, g, b)
        if con == 0:
            libtcod.console_set_default_foreground(con, col)
        else:
            libtcod.console_set_default_foreground(self.mConsole[con - 1], col)

    def console_set_default_background(self, con, r, g, b):
        col = libtcod.Color(r, g, b)
        if con == 0:
            libtcod.console_set_default_background(con, col)
        else:
            libtcod.console_set_default_background(self.mConsole[con - 1], col)

    def console_print_frame(self, con, x, y, width, height, clear):
        if con == 0:
            libtcod.console_print_frame(con, x, y, width, height, clear)
        else:
            libtcod.console_print_frame(self.mConsole[con - 1], x, y, width, height, clear)

    def console_print_rect(self, con, x, y, width, height, fmt):
        if con == 0:
            libtcod.console_print_rect(con, x, y, width, height, fmt)
        else:
            libtcod.console_print_rect(self.mConsole[con - 1], x, y, width, height, fmt)

    def console_blit(self, conSrc, xSrc, ySrc, wSrc, hSrc, conDest, xDest, yDest, foreAlph=1.0, backAlph=1.0):
        dest = None
        src = self.mConsole[conSrc - 1]
        if conDest == 0:
            dest = 0
        else:
            dest = self.mConsole[conDest - 1]
        libtcod.console_blit(src, xSrc, ySrc, wSrc, hSrc, dest, xDest, yDest, foreAlph, backAlph)

    def console_put_char_ex(self, con, x, y, c, cr, cg, cb, br, bg, bb):
        fore = libtcod.Color(cr, cg, cb)
        back = libtcod.Color(br, bg, bb)
        if con == 0:
            libtcod.console_put_char_ex(con, x, y, c, fore, back)
        else:
            libtcod.console_put_char_ex(self.mConsole[con - 1], x, y, c, fore, back)

    def console_set_char(self, con, x, y, c):
        if con == 0:
            libtcod.console_set_char(con, x, y, c)
        else:
            libtcod.console_set_char(self.mConsole[con - 1], x, y, c)

    def console_set_alignment(self, con, align):
        if con == 0:
            libtcod.console_set_alignment(con, align)
        else:
            libtcod.console_set_alignment(self.mConsole[con - 1], align)

    def console_print(self, con, x, y, fmt):
        if con == 0:
            libtcod.console_print(con, x, y, fmt)
        else:
            libtcod.console_print(self.mConsole[con - 1], x, y, fmt)

    def console_print_ex(self, con, x, y, flag, alignment, fmt):
        if con == 0:
            libtcod.console_print_ex(con, x, y, flag, alignment, fmt)
        else:
            libtcod.console_print_ex(self.mConsole[con - 1], x, y, flag, alignment, fmt)

    #@staticmethod
    def console_flush(self):
        libtcod.console_flush()

    def console_clear(self, con):
        if con == 0:
            libtcod.console_clear(con)
        else:
            libtcod.console_clear(self.mConsole[con - 1])

    def console_get_char_background(self, con, x, y):
        if con == 0:
            col = libtcod.console_get_char_background(0, x, y)
            return libtcod.color_get_hsv(col)
        else:
            col = libtcod.console_get_char_background(self.mConsole[con - 1], x, y)
            return libtcod.color_get_hsv(col)

    def console_get_char_foreground(self, con, x, y):
        if con == 0:
            col = libtcod.console_get_char_foreground(0, x, y)
            return col
        else:
            col = libtcod.console_get_char_foreground(self.mConsole[con - 1], x, y)
            return col

    def image_new(self, x, y):
        img = libtcod.image_new(x, y)
        self.mImages.append(img)
        return len(self.mImages)

    def image_load(self, path):
        img = libtcod.image_load(path)
        self.mImages.append(img)
        return len(self.mImages)

    def image_delete(self, img):
        i = self.mImages.pop(img - 1)
        libtcod.image_delete(i)

    def image_clear(self, i, r, g, b):
        col = libtcod.Color(r, g, b)
        libtcod.image_clear(self.mImages[i - 1], col)

    def image_put_pixel(self, i, x, y, r, g, b):
        col = libtcod.Color(r, g, b)
        libtcod.image_put_pixel(self.mImages[i - 1], x, y, col)

    def image_get_size(self, i):
        return libtcod.image_get_size(self.mImages[i - 1])

    def image_get_pixel(self, i, x, y):
        return libtcod.image_get_pixel(self.mImages[i - 1], x, y)

    def image_blit(self, i, c, x, y, w=-1, h=-1):
        if c == 0:
            libtcod.image_blit(self.mImages[i - 1], 0, x, y, libtcod.BKGND_SET, 1.0, 1.0, 0)
        else:
            libtcod.image_blit(self.mImages[i - 1], self.mConsole[c - 1], x, y, libtcod.BKGND_SET, 1.0, 1.0, 0)

    def image_blit_rect(self, i, c, x=0, y=0, w=-1, h=-1):
        if c == 0:
            libtcod.image_blit_rect(self.mImages[i - 1], 0, x, y, w, h, libtcod.BKGND_SET)
        else:
            libtcod.image_blit_rect(self.mImages[i - 1], self.mConsole[c - 1], x, y, w, h, libtcod.BKGND_SET)

    def image_blit_2x(self, i, c, x, y, sx=0, sy=0, w=-1, h=-1):
        if c == 0:
            libtcod.image_blit_2x(self.mImages[i - 1], 0, x, y, sx, sy, w, h)
        else:
            libtcod.image_blit_2x(self.mImages[i - 1], self.mConsole[c - 1], x, y, sx, sy, w, h)

    def map_init_level(self, sizeX, sizeY):
        self.FOV = libtcod.map_new(sizeX, sizeY)
        for tile in self.mMap:
            tile.explored = False
            self.map_set_properties(tile.x, tile.y, not tile.blocked, not tile.block_sight)

    def map_add_tile(self, x, y, cell, blocked, block_sight, explored, spawn_node, color, opacity):
        self.mMap.append(Tile(x, y, cell, blocked, block_sight, explored, spawn_node, color, opacity))

    def map_add_tile_2x(self, x, y, cell, blocked, block_sight, explored, spawn_node, color, opacity):
        self.mMap2x.append(Tile(x, y, cell, blocked, block_sight, explored, spawn_node, color, opacity))

    def map_set_properties(self, x, y, blocked, block_sight):
        libtcod.map_set_properties(self.FOV, x, y, blocked, block_sight)

    def map_clear(self):
        self.mMap = []
        self.mMap2x = []

    def set_fov_map(self, map):
        self.FOV = map

    def get_fov_map(self):
        return self.FOV

    def get_map(self):
        return self.mMap

    def set_map(self, mMap):
        self.mMap = mMap

    def set_map_2x(self, map2x):
        self.mMap2x = map2x

    def get_map_2x(self):
        return self.mMap2x

    #@jit
    def map_draw_2x(self, con, x, y):
        self.image_clear(self.subcell_map_image, 0, 0, 0)
        if con == 0:
            for tile in self.mMap2x:
                '''#for tile in self.numpy_list_2x.flat:
                r, g, b = tile.color
                brightness = self.light_mask.mask[tile.x + tile.y * (self.w * 2)]
                r *= brightness[0]
                g *= brightness[1]
                b *= brightness[2]
                self.image_put_pixel(self.subcell_map_image, tile.x, tile.y, int(r), int(g), int(b))'''
                if tile.block_sight:
                    r, g, b = self.color_light_wall
                    self.image_put_pixel(self.subcell_map_image, tile.x, tile.y, r, g, b)
                else:
                    r,g,b = self.color_light_ground
                    self.image_put_pixel(self.subcell_map_image, tile.x, tile.y, r, g, b)

            #self.render_ground_effects()
            #self.render_light_sources()
            self.console_clear(con)
            self.image_blit_2x(self.subcell_map_image, con, 0, 0)

    def blit_map(self, con):
        #self.console_clear(con)
        self.image_blit_rect(self.map_image, con, y=-1)

    def map_draw(self, con, x, y, light_mask=None, run_fov=True):
        #con = self.mConsole[con-1]
        self.image_clear(self.map_image, 0, 0, 0)
        if con == 0:
            libtcod.map_compute_fov(self.FOV, x, y, 0, True, libtcod.FOV_SHADOW)
            for tile in self.mMap:
                #if libtcod.map_is_in_fov(self.FOV, tile.x, tile.y) or not run_fov:
                    r, g, b = tile.color
                    '''if light_mask is not None:
                        brightness = light_mask.mask[tile.x + tile.y * self.w]
                        r *= brightness[0]
                        g *= brightness[1]
                        b *= brightness[2]
                        r = min(255, r)
                        g = min(255, g)
                        b = min(255, b)
                    self.image_put_pixel(self.map_image, tile.x, tile.y, int(r), int(g), int(b))'''
                    if tile.block_sight:
                        r, g, b = self.color_dark_wall
                        self.image_put_pixel(self.map_image, tile.x, tile.y, r, g, b)
                    else:
                        r,g,b = self.color_dark_ground
                        self.image_put_pixel(self.map_image, tile.x, tile.y, r, g, b)

            self.render_ground_effects()
            self.render_light_sources()
            #self.console_clear(con)
            #self.image_blit(self.map_image, con, self.w / 2, self.h / 2)
        else:
            libtcod.map_compute_fov(self.FOV, x, y, 0, True, libtcod.FOV_SHADOW)
            for tile in self.mMap:
                if libtcod.map_is_in_fov(self.FOV, tile.x, tile.y):
                    r, g, b = tile.color
                    if light_mask is not None:
                        brightness = light_mask.mask[tile.x + tile.y * self.w]
                        r *= brightness[0]
                        g *= brightness[1]
                        b *= brightness[2]
                    self.image_put_pixel(self.map_image, tile.x, tile.y, int(r), int(g), int(b))
                    tile.explored = True
                    '''if tile.block_sight:
                        r,g,b = self.color_light_wall
                        self.image_put_pixel(self.map_image,tile.x, tile.y, r,g,b)
                        # libtcod.console_put_char_ex(con,tile.x,tile.y,tile.cell,self.color_tile_wall,self.color_light_wall)
                    else:
                        r,g,b = self.color_light_ground
                        self.image_put_pixel(self.map_image,tile.x, tile.y, r,g,b)
                        # libtcod.console_put_char_ex(con,tile.x,tile.y,tile.cell,self.color_tile_ground,self.color_light_ground)
                    tile.explored = True
                else:
                    if tile.explored:
                        if tile.block_sight:
                            r,g,b = self.color_dark_wall
                            self.image_put_pixel(self.map_image,tile.x, tile.y, r,g,b)
                            # libtcod.console_put_char_ex(con,tile.x,tile.y,' ',self.color_tile_wall,self.color_dark_wall)
                        else:
                            r,g,b = self.color_dark_ground
                            self.image_put_pixel(self.map_image,tile.x, tile.y, r,g,b)
                            # libtcod.console_put_char_ex(con,tile.x,tile.y,' ',self.color_tile_ground,self.color_dark_ground)'''
            # calculate light here, after the map is already drawn, also add blood effects first
            self.render_ground_effects()
            #self.render_light_sources()
            #self.console_clear(con)
            #self.image_blit(self.map_image, con, self.w / 2, self.h / 2)

    def map_draw_scrolling(self, con, game, x, y):
        self.image_clear(self.map_image, 0, 0, 0)
        if con == 0:
            pass
        else:
            libtcod.map_compute_fov(self.FOV, x, y, 5, True, libtcod.FOV_SHADOW)
            cx = game.player.x - (game.Map.MAP_WIDTH / 2)
            cy = game.player.y - (game.Map.MAP_HEIGHT / 2)
            minx, miny = game.Map.MAP_WIDTH, game.Map.MAP_HEIGHT
            for x in range(minx):
                dx = x + cx
                for y in range(miny):
                    dy = y + cy
                    if in_rect(dx, dy, minx, miny):
                        tile = game.Map.map[dx][dy]
                        if libtcod.map_is_in_fov(self.FOV, dx, dy):
                            if tile.block_sight:
                                r, g, b = self.color_light_wall
                                self.image_put_pixel(self.map_image, x, y, r, g, b)
                            else:
                                r, g, b = self.color_light_ground
                                self.image_put_pixel(self.map_image, x, y, r, g, b)
                            tile.explored = True
                        else:
                            if tile.explored:
                                if tile.block_sight:
                                    r, g, b = self.color_dark_wall
                                    self.image_put_pixel(self.map_image, x, y, r, g, b)
                                else:
                                    r, g, b = self.color_dark_ground
                                    self.image_put_pixel(self.map_image, x, y, r, g, b)
            self.console_clear(con)
            self.image_blit(self.map_image, con, self.w / 2, self.h / 2)

    def map_is_explored(self, x, y):
        for tile in self.mMap:
            if tile.x == x and tile.y == y:
                return tile.explored

    def render_ground_effects(self):
        pass

    def render_light_sources(self):
        self.image_clear(self.light_map, 0, 0, 0)
        for l in self.light_sources:
            minx = max(1, l.minx)
            miny = max(1, l.miny)
            maxx = min(l.maxx, self.w - 1)
            maxy = min(l.maxy, self.h - 1)
            l.flicker += 0.05
            n = self.noise
            v = 0.5 * libtcod.noise_get(n, [l.flicker])
            factor = l.factor + v
            for x in range(minx, maxx):
                for y in range(miny, maxy):
                    if libtcod.map_is_in_fov(self.FOV, x, y):
                        squaredDist = int((l.x - x) * (l.x - x) + (l.y - y) * (l.y - y))
                        coef = (1.0 / (1.0 + float(squaredDist) / 40) - l.offset) * factor
                        col = self.image_get_pixel(self.map_image, x, y)
                        col = libtcod.color_lerp(col, l.color, coef)  #  col + (l.color * coef)
                        r, g, b = col
                        self.image_put_pixel(self.map_image, x, y, r, g, b)

                        #self.offset = self.intensity /(1.0 + float(self.radius * self.radius)/40)
                        #self.factor = self.intensity / (1.0 - self.offset)

    def lightmask_set_size(self, w, h):
        self.light_mask.width = w
        self.light_mask.height = h
        self.lightmask_reset()

    def lightmask_reset(self):
        self.light_mask.reset()

    def lightmask_add_light(self, x, y, br):
        self.light_mask.add_light(x, y, br)

    def lightmask_compute(self, map):
        self.light_mask.compute_mask(map)

    def particle_explosion(self, num, x, y, r=False, b=False, color=None):
        particle.explosion(num, self.particles, x, y, r, b, color)

    def particle_nova(self, num, x, y, r=False, b=False):
        particle.nova(num, self.particles, x, y, r, b)

    def particle_cone_spray(self, num, ox, oy, dx, dy, r=False, b=False):
        particle.cone_spray(num, self.particles, ox, oy, dx, dy, r, b)

    def particle_cone(self, num, ox, oy, dx, dy, r=False, b=False):
        particle.cone(num, self.particles, ox, oy, dx, dy, r, b)

    def particle_projectile(self, num, ox, oy, dx, dy, r=False, b=False):
        particle.projectile(num, self.particles, ox, oy, dx, dy, r, b)

    def particle_update(self, map=None):
        for p in xrange(len(self.particles) - 1, 0, -1):
            self.particles[p].update(self.light_mask, map)
            if self.particles[p].dead:
                self.particles.pop(p)

    def particle_draw(self, con, c='*'):
        for p in self.particles:
            self.console_put_char_ex(con, int(p.x), int(p.y), c, 255, 255, 255, 0, 0, 0)
