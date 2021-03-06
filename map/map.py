import sys, os
import math

sys.path.append(sys.path[0])
import libtcodpy as libtcod

sys.path.append(os.path.join(sys.path[0], 'object'))
from object.object import *
from object.spells import *
from object.item import *
from object.misc import *

MAX_DEPTH = 25
# Variables for tile bitmasking
tile_bitshift = 4
tile_bit_offset = 31

ground_tiles = [',', '.', "'", '`']


class Level:
    def __init__(self, map=None, objects=None, depth=None, fov_map=None, draw_map=None, spawn_nodes=None):
        self.map = map
        self.objects = objects
        self.depth = depth
        self.fov_map = fov_map
        self.draw_map = draw_map
        self.spawn_nodes = spawn_nodes

    def update_level(self, map, objects, fov_map, draw_map):
        self.map = map
        self.objects = objects
        self.fov_map = fov_map
        self.draw_map = draw_map


class Tile:
    # a tile of the map and its properties
    def __init__(self, blocked=True, block_sight=None):
        self.blocked = blocked
        #all tiles start unexplored
        self.explored = False
        self.tile = '#'
        self.spawn_node = False
        self.opacity = 1.0
        self.color = libtcod.Color(99, 99, 99)
        #by default, if a tile is blocked, it also blocks sight
        if block_sight is None: block_sight = blocked
        self.block_sight = block_sight

    def set_color(self, col):
        self.color = col

    #Thanks to my friend Art for help with this bitmasking stuff.    
    def return_bitmask(self):
        bit_mask_values = {',': 1, '.': 2, '`': 4, "'": 8, '#': 16}  #dictionary for tiles and respective bits
        ##sets the bits on or off based on if its true or false
        tilemask = (self.blocked * 1) | (self.block_sight * 2) | (self.explored * 4) | (self.spawn_node * 8 )
        ##Shift the bitmask over, incase new bools are added in front.
        ##Should keep old maps compatable
        tilemask = tilemask | bit_mask_values[
                                  self.tile] << tile_bitshift  ##gets the bit for the tile char, then shifts over
        return tilemask

    def build_from_bitmask(self, bitmask):
        bit_unmask_values = {1: ',', 2: '.', 4: '`', 8: "'", 16: '#'}
        self.blocked = bool((bitmask & 1) * True)
        self.block_sight = bool((bitmask & 2) * True)
        self.explored = bool((bitmask & 4) * True)
        self.spawn_node = bool((bitmask & 8) * True)
        self.tile = bit_unmask_values[(bitmask >> tile_bitshift) & tile_bit_offset]


class Rect:
    # a rectangle on the map. used to characterize a room.
    def __init__(self, x, y, w, h):
        self.x1 = x
        self.y1 = y
        self.x2 = x + w
        self.y2 = y + h

    def center(self):
        center_x = (self.x1 + self.x2) / 2
        center_y = (self.y1 + self.y2) / 2
        return (center_x, center_y)

    def intersect(self, other):
        #returns true if this rectangle intersects with another one
        return (self.x1 <= other.x2 and self.x2 >= other.x1 and
                self.y1 <= other.y2 and self.y2 >= other.y1)


class SpawnNode:
    def __init__(self, tile, x, y, game):
        self.tile = tile
        self.x = x
        self.y = y
        self.owner = None
        self.active = True
        self.objects = game.objects
        self.player = game.player
        self.ticker = game.ticker
        self.game = game
        # Speed for spawning, need to play around with values
        self.un_explored_speed = 2000  #200 turn  spawn
        self.explored_speed = 4000  #400 turn spawn
        self.group = []
        self.threat = 0
        self.max_group_size = 0

    def turn_on(self):
        self.active = True

    def turn_off(self):
        self.active = False

    def remove_from_group(self, monster):
        for mon in self.group:
            if mon == monster:
                self.group.remove(monster)
                break

    def spawn_mobs(self, game):
        # #Need to play around with values, mob spawning is too sparse or too great
        ##NEED MOAR MANA!
        if not self.active:
            if len(self.group) < 2:
                self.turn_on()
            else:
                self.ticker.schedule_turn(self.explored_speed, self.owner)
                return
        if libtcod.map_is_in_fov(game.fov_map, self.x, self.y):
            ##if the node is in the view of the player, do nothing
            ##but schedule the next spawn turn
            self.ticker.schedule_turn(self.explored_speed, self.owner)

        else:
            #todo: pick leaders and subordinates
            self.max_group_size = libtcod.random_get_int(0, 2, 9)
            base_group_monster = game.build_objects.get_random_monster_name()
            for m in range(self.max_group_size):
                mon = game.build_objects.create_monster(game, self.x, self.y, mob_name=base_group_monster)
                mon.ai.add_node(self)
                self.group.append(mon)
                game.logger.log.info(mon.ai.node)
                game.objects.append(mon)

            self.turn_off()
            self.ticker.schedule_turn(self.explored_speed, self.owner)
            for object in self.group:
                object.message = game.message
                object.objects = game.objects


class Map:
    def __init__(self, mh, mw, rmin, rmax, r, rm, ri, logger=None):
        self.MAP_HEIGHT = mh
        self.MAP_WIDTH = mw
        self.ROOM_MIN_SIZE = rmin
        self.ROOM_MAX_SIZE = rmax
        self.MAX_ROOMS = r
        self.MAX_ROOM_MONSTERS = rm
        self.MAX_ROOM_ITEMS = ri
        self.logger = logger
        self.depth = 0

    def set_ground(self, x, y):
        self.map[x][y].blocked = False
        self.map[x][y].block_sight = False
        self.map[x][y].tile = ground_tiles[libtcod.random_get_int(0, 0, (len(ground_tiles) - 1))]
        self.map[x][y].opacity = 0.0
        self.map[x][y].color = libtcod.Color(125, 125, 125)

    def create_room(self, room, game=None):
        # go through the tiles in the rectangle and make them passable
        objects = None
        if game:
            objects = game.objects

        for x in range(room.x1 + 1, room.x2):
            for y in range(room.y1 + 1, room.y2):
                self.set_ground(x, y)

        while 1:
            x = libtcod.random_get_int(0, room.x1 - 1, room.x2 - 1)
            y = libtcod.random_get_int(0, room.y1 - 1, room.y2 - 1)
            #only place it if the tile is not blocked
            if not self.is_blocked(x, y, objects):
                break
        if game:
            self.create_spawn_node(x, y, game)

    def create_h_tunnel(self, x1, x2, y):
        # horizontal tunnel. min() and max() are used in case x1>x2
        for x in range(min(x1, x2), max(x1, x2) + 1):
            self.set_ground(x, y)

    def create_v_tunnel(self, y1, y2, x):
        for y in range(min(y1, y2), max(y1, y2) + 1):
            self.set_ground(x, y)

    def return_bitmask_map(self, map=None, width=None, height=None):
        # returns a 1d array with the bitmasks of each tile
        if not width:
            width = self.MAP_WIDTH
        if not height:
            height = self.MAP_HEIGHT
        if not map:
            map = self.map

        bit_map_arr = []
        for x in range(width):
            for y in range(height):
                bit_map_arr.append(map[x][y].return_bitmask())
        return bit_map_arr

    def build_bitmask_map(self, bitmask_map, game):
        # build a map from a bitmask array
        #tiles[y*10+x]
        map = [[Tile() for y in range(self.MAP_HEIGHT)] for x in range(self.MAP_WIDTH)]
        self.spawn_nodes = []
        for x in range(self.MAP_WIDTH):
            for y in range(self.MAP_HEIGHT):
                map[x][y].build_from_bitmask(bitmask_map[x * self.MAP_HEIGHT + y])
                if map[x][y].spawn_node:
                    self.create_spawn_node(x, y, game, map)
        self.map = map
        return self.map

    def return_spawn_nodes(self):
        return self.spawn_nodes

    def load_map(self, map):
        pass

    def create_spawn_node(self, x, y, game=None, map=None):
        # #spawn nodes will have a turn in the ticker,
        ##undiscovered node will have a higher speed.
        ##Nodes in FoV will do nothing
        if not map:
            map = self.map
        map[x][y].spawn_node = True
        node = SpawnNode(map[x][y], x, y, game)
        node_obj = Object()
        node_obj.node = node
        node_obj.use = node.spawn_mobs
        node_obj.node.owner = node_obj
        node_obj.node.ticker.schedule_turn(0, node_obj)
        self.spawn_nodes.append(node_obj)

    def make_map(self, game=None, depth=0, empty=False):
        self.logger.log.info('Creating map.')
        if game:
            game.objects = [game.player]
            game.gEngine.map_init_level(self.MAP_WIDTH, self.MAP_HEIGHT)
        # fill map with "blocked" tiles
        self.spawn_nodes = []
        map = [[Tile(True)
                for y in range(self.MAP_HEIGHT)]
               for x in range(self.MAP_WIDTH)]
        self.map = map

        map2x = [[Tile(True)
                  for y in range(self.MAP_HEIGHT * 2)]
                 for x in range(self.MAP_WIDTH * 2)]
        self.map2x = map2x

        rooms = []
        num_rooms = 0
        for r in range(self.MAX_ROOMS):
            #random width and height
            w = libtcod.random_get_int(0, self.ROOM_MIN_SIZE, self.ROOM_MAX_SIZE)
            h = libtcod.random_get_int(0, self.ROOM_MIN_SIZE, self.ROOM_MAX_SIZE)
            #random position without going out of the boundaries of the map
            x = libtcod.random_get_int(0, 0, self.MAP_WIDTH - w - 1)
            y = libtcod.random_get_int(0, 0, self.MAP_HEIGHT - h - 1)

            #"Rect" class makes rectangles easier to work with
            new_room = Rect(x, y, w, h)

            #run through the other rooms and see if they intersect with this one
            failed = False
            for other_room in rooms:
                if new_room.intersect(other_room):
                    failed = True
                    break

            if not failed:
                #this means there are no intersections, so this room is valid

                #"paint" it to the map's tiles
                self.create_room(new_room, game)

                #add some contents to this room, such as monsters
                if not empty:
                    self.place_objects(new_room, game)

                #center coordinates of new room, will be useful later
                (new_x, new_y) = new_room.center()

                if num_rooms == 0:
                    if game:
                        #this is the first room, where the player starts at
                        game.player.x = new_x
                        game.player.y = new_y

                else:
                    #all rooms after the first:
                    #connect it to the previous room with a tunnel

                    #center coordinates of previous room
                    (prev_x, prev_y) = rooms[num_rooms - 1].center()

                    #draw a coin (random number that is either 0 or 1)
                    if libtcod.random_get_int(0, 0, 1) == 1:
                        #first move horizontally, then vertically
                        self.create_h_tunnel(prev_x, new_x, prev_y)
                        self.create_v_tunnel(prev_y, new_y, new_x)
                    else:
                        #first move vertically, then horizontally
                        self.create_v_tunnel(prev_y, new_y, prev_x)
                        self.create_h_tunnel(prev_x, new_x, new_y)

                #finally, append the new room to the list
                rooms.append(new_room)
                num_rooms += 1

        if game:
            ##Stairs, upstairs get placed under the player
            m = Misc(type='up')
            up = Object(game.con, game.player.x, game.player.y, '<', 'set of stairs going up', libtcod.white,
                        blocks=False, misc=m)
            game.objects.append(up)
            up.send_to_back(game.objects)

            ##Down stairs get randomly placed.
            if depth < MAX_DEPTH:
                down_placed = False
                while down_placed == False:
                    x = libtcod.random_get_int(0, 0, self.MAP_WIDTH - w - 1)
                    y = libtcod.random_get_int(0, 0, self.MAP_HEIGHT - h - 1)
                    #only place it if the tile is not blocked
                    if not self.is_blocked(x, y, game.objects):
                        m = Misc(type='down')
                        down = Object(game.con, x, y, '>', 'set of stairs going down', libtcod.white, blocks=False,
                                      misc=m)
                        game.objects.append(down)
                        down.send_to_back(game.objects)
                        down_placed = True

            for object in game.objects:
                object.message = game.message
                object.objects = game.objects

            game.gEngine.map_clear()
            for y in range(self.MAP_HEIGHT):
                for x in range(self.MAP_WIDTH):
                    c = self.map[x][y]
                    game.gEngine.map_add_tile(x, y, c.tile, c.blocked, c.block_sight, c.explored, c.spawn_node, c.color,
                                              c.opacity)

            fov_map = game.gEngine.get_fov_map()
            mmap = game.gEngine.get_map()
            #self.logger.log.debug(len(self.map))
            return Level(self.map, game.objects, depth, fov_map, mmap, self.spawn_nodes)
        else:
            return Level(self.map, depth=depth)

    def set_draw_map(self, map, gEngine):
        for y in range(self.MAP_HEIGHT):
            for x in range(self.MAP_WIDTH):
                c = map[x][y]
                gEngine.map_add_tile(x, y, c.tile, c.blocked, c.block_sight, c.explored, c.spawn_node, c.color,
                                     c.opacity)
        gEngine.map_init_level(self.MAP_WIDTH, self.MAP_HEIGHT)

    def set_draw_map_2x(self, map, gEngine):  # converts a normal generated level into a subcell compatable map
        for y in range(self.MAP_HEIGHT):
            for x in range(self.MAP_WIDTH):
                c = map[x][y]
                self.map2x[x * 2][y * 2] = c
                self.map2x[x * 2 + 1][y * 2] = c
                self.map2x[x * 2][y * 2 + 1] = c
                self.map2x[x * 2 + 1][y * 2 + 1] = c
                gEngine.map_add_tile_2x(x * 2, y * 2, c.tile, c.blocked, c.block_sight, c.explored, c.spawn_node,
                                        c.color, c.opacity)
                gEngine.map_add_tile_2x(x * 2 + 1, y * 2, c.tile, c.blocked, c.block_sight, c.explored, c.spawn_node,
                                        c.color, c.opacity)
                gEngine.map_add_tile_2x(x * 2, y * 2 + 1, c.tile, c.blocked, c.block_sight, c.explored, c.spawn_node,
                                        c.color, c.opacity)
                gEngine.map_add_tile_2x(x * 2 + 1, y * 2 + 1, c.tile, c.blocked, c.block_sight, c.explored,
                                        c.spawn_node, c.color, c.opacity)

    def place_objects(self, room, game):

        # choose random number of items
        num_items = libtcod.random_get_int(0, 0, self.MAX_ROOM_ITEMS)

        for i in range(num_items):
            #choose random spot for this item
            x = libtcod.random_get_int(0, room.x1 + 1, room.x2 - 1)
            y = libtcod.random_get_int(0, room.y1 + 1, room.y2 - 1)

            #only place it if the tile is not blocked
            if not self.is_blocked(x, y, game.objects):
                dice = libtcod.random_get_int(0, 0, 100)
                if dice < 70:
                    #create a healing potion (70% chance)
                    game.objects.append(game.build_objects.build_potion(game, x, y))

                else:
                    #create a random scroll (30% chance to get 1 of 3 scrolls (10% chance per scroll))
                    game.objects.append(game.build_objects.build_scroll(game, x, y))

    def is_blocked(self, x, y, objects=None):
        # first test the map tile
        if self.map[x][y].blocked:
            return True
        if objects:
            #now check for any blocking objects
            for object in objects:
                if object.blocks and object.x == x and object.y == y:
                    return True

        return False 