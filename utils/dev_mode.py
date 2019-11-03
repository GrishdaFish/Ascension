__author__ = 'Grishnak'
import os, sys
import math
import libtcodpy as libtcod
os.path.join(sys.path[0],'map')
sys.path.append(os.path.join(sys.path[0],'map'))
import map.map as map

sys.path.append(os.path.join(sys.path[0],'object'))
from object import *
from object.build_objects import *

sys.path.append(os.path.join(sys.path[0],'utils'))
from menu import *
from utils import *
import save_system as save_system
import console as console
from menus.inventory import *
from menus.character import *
from menus.hot_bar import *
sys.path.append(os.path.join(sys.path[0],'gEngine'))
from map import prefab_generator

def quick_convert(map):
    new_map = []
    for tile in map:
        for t in tile:
            new_map.append(t.opacity)
    return new_map

class DevMode:
    def __init__(self, gEngine, Map):
        self.gEngine = gEngine
        self.particles = []
        self.Map = Map

    def run(self):
        path = os.path.join(sys.path[0],'content', 'prefabs','Prefabs.xp')
        #print path
        data = prefab_generator.load_prefab(path)
        #print data
        level = self.Map.make_map(empty=True)
        level.draw_map = self.Map.set_draw_map_2x(level.map, self.gEngine)
        level.draw_map = self.Map.set_draw_map(level.map, self.gEngine)
        level.fov_map = self.gEngine.get_fov_map()
        run_fov = True
        self.gEngine.lightmask_set_size(self.Map.MAP_WIDTH*2, self.Map.MAP_HEIGHT*2)
        #self.gEngine.light_mask.set_intensity(18.0)
        #lightmask = light_mask.LightMask(self.Map.MAP_WIDTH, self.Map.MAP_HEIGHT)'''
        self.gEngine.set_map_2x(self.gEngine.get_map_2x())

        self.qmap = quick_convert(self.Map.map2x)
        while not libtcod.console_is_window_closed():
            self.gEngine.console_clear(0)
            key = libtcod.console_check_for_keypress()
            mouse = libtcod.mouse_get_status()
            (x, y) = (mouse.cx, mouse.cy)
            self.gEngine.light_mask.reset()

            if key.vk == libtcod.KEY_SPACE:
                run_fov = not run_fov


            if x <  self.Map.MAP_WIDTH and y < self.Map.MAP_HEIGHT:
                self.gEngine.light_mask.add_light(x*2, y*2, 1.0 )
                pass
            self.gEngine.particle_update(self.Map.map2x)

            #self.gEngine.light_mask.add_light(40, 21, 1.0)
            #self.gEngine.lightmask_compute(self.Map.map2x)
            self.gEngine.map_draw(0, 40, 21, self.gEngine.light_mask)
            #self.gEngine.map_draw_2x(0, 40, 21)

            if mouse.lbutton:
                #self.gEngine.particle_cone(15,40, 21, x, y)
                #self.gEngine.particle_cone_spray(15,40, 21, x, y)
                self.gEngine.particle_projectile(1, 40*2, 21*2, x*2, y*2)
                #self.gEngine.particle_explosion(15, x, y)
                #self.gEngine.particle_nova(9,  x, y)
                pass

            self.gEngine.particle_draw(0)





            self.gEngine.console_print(0, 1, 5, "(%dfps)" % (libtcod.sys_get_fps()))
            self.gEngine.console_put_char_ex(0,40,21,'@', 255, 255, 255, 0, 0 ,0)
            self.gEngine.console_put_char_ex(0,x,y,"X",255,255,255,0,0,0)

            self.gEngine.console_flush()
