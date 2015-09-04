import libtcodpy as libtcod
import math
import textwrap
import shelve
import sys,os,time


    
os.path.join(sys.path[0],'map')
sys.path.append(os.path.join(sys.path[0],'map'))
import map.map as map

sys.path.append(os.path.join(sys.path[0],'object'))
from object import *
from object.build_objects import *

sys.path.append(os.path.join(sys.path[0],'utils'))
from utils.menu import *
from utils.utils import *
import utils.save_system as save_system
import utils.console as console

#actual size of the window
SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50

PANEL_HEIGHT = 7
#size of the map
MAP_WIDTH = 80#SCREEN_WIDTH
MAP_HEIGHT = 43#SCREEN_HEIGHT - PANEL_HEIGHT
MAX_DEPTH = 25

#sizes and coordinates relevant for the GUI
BAR_WIDTH = 20

PANEL_Y = SCREEN_HEIGHT - PANEL_HEIGHT
MSG_X = BAR_WIDTH + 2
MSG_WIDTH = SCREEN_WIDTH 
MSG_HEIGHT = PANEL_HEIGHT - 1
INVENTORY_WIDTH = 50
 
#parameters for dungeon generator
ROOM_MAX_SIZE = 10
ROOM_MIN_SIZE = 6
MAX_ROOMS = 30
MAX_ROOM_MONSTERS = 3
MAX_ROOM_ITEMS = 2
 
 
FOV_ALGO = 0  #default FOV algorithm
FOV_LIGHT_WALLS = True  #light walls or not
TORCH_RADIUS = 10
 
LIMIT_FPS = 60
 
color_dark_wall = libtcod.darker_grey
color_light_wall = libtcod.Color(99,99,99)
color_dark_ground = libtcod.dark_grey
color_light_ground = libtcod.Color(125,125,125)
color_tile_wall = libtcod.Color(177,177,177)
color_tile_ground = libtcod.Color(190,190,190)


class Game:
##============================================================================
    def __init__(self, content, logger, key_set):
##============================================================================
        self.version = '0.0.1a'
        self.objects = []
        self.logger = logger
        self.logger.log.info('Init Game and Game Screen.')
        self.debug_level = 'debug'  # prints errors verbosely to the game screen
                                    # On release, just a confirmation menu
                                    # Also affects the use of the python interpreter
                                    # in the console, disabled on release

        '''try:
            self.logger.log.debug('Init gEngine...')
            import cEngine as gEngine  # Try importing the pyd
            self.logger.log.debug('gEngine pyd/so imported')
        except ImportError, err:  # if that fails, import the python prototype
            sys.path.append(os.path.join(sys.path[0], 'gEngine'))
            self.logger.log.debug('gEngine pyd/so import failed, using python prototype')
            self.logger.log.exception(err)
            import gEngine.gEngine as gEngine'''
        import gEngine.gEngine as gEngine
            
        try:
            self.logger.log.debug("Importing Psyco.")
            import psyco
            psyco.full()
            psyco.log()
            psyco.profile()
            self.logger.log.debug('Psyco full used.')
        except ImportError:
            self.logger.log.debug("Importing Psyco failed.")
            pass

        #libtcod.console_set_keyboard_repeat(250,250)
        self.gEngine = gEngine.gEngine(SCREEN_WIDTH, SCREEN_HEIGHT, 'Ascension 0.0.1a', False, LIMIT_FPS)
        self.con = self.gEngine.console_new(MAP_WIDTH, MAP_HEIGHT)
        self.panel = self.gEngine.console_new(SCREEN_WIDTH, PANEL_HEIGHT)
        
        self.message = Message(self.panel, MSG_HEIGHT, MSG_WIDTH, MSG_X, self.logger, self.debug_level)
        self.build_objects = GameObjects(content)        
        self.ticker = Ticker()
        
        self.Map = map.Map(MAP_HEIGHT, MAP_WIDTH, ROOM_MIN_SIZE, ROOM_MAX_SIZE,
            MAX_ROOMS, MAX_ROOM_MONSTERS, MAX_ROOM_ITEMS, self.logger)
            
        self.keys = key_set
        self.setup_keys()
        self.current_dungeon = []  # an array that holds all off the dungeon levels
        self.console = console.Console(self, SCREEN_WIDTH-2, SCREEN_HEIGHT/2, self.debug_level)
        self.depth = None
        self.game_state = None

        libtcod.console_set_keyboard_repeat(50, 50)
        libtcod.sys_set_renderer(libtcod.RENDERER_SDL)

    #need to make this more efficient, going to set up keys in an array
##============================================================================
    def setup_keys(self):
##============================================================================
        key_conv = {'KEY_UP'        :libtcod.KEY_UP,
                    'KEY_DOWN'      :libtcod.KEY_DOWN,
                    'KEY_LEFT'      :libtcod.KEY_LEFT,
                    'KEY_RIGHT'     :libtcod.KEY_RIGHT,
                    }
        if self.keys.key_north in key_conv:
            self.keys.key_north = key_conv[self.keys.key_north]
        if self.keys.key_east in key_conv:
            self.keys.key_east  = key_conv[self.keys.key_east]
        if self.keys.key_south in key_conv:
            self.keys.key_south = key_conv[self.keys.key_south]
        if self.keys.key_west in key_conv:
            self.keys.key_west  = key_conv[self.keys.key_west]

##============================================================================
    def save_game(self):
##============================================================================
        ex = None
        for level in self.current_dungeon:
            if level.depth == self.depth:
                level.update_level(self.Map.map, self.objects, self.gEngine.get_fov_map(), self.gEngine.get_map())
        try:
            self.logger.log.info('Saving game.')
            save_system.save(self)
        except Exception, ex:
            self.message.error_message(ex, self)

##============================================================================
    def load_game(self):
##============================================================================
        self.logger.log.debug('Loading game')
        fighter_component = Fighter(hp=90, defense=2, power=5, death_function=self.player_death, money=800, speed=10)
        self.player = Object(self.con, 0, 0, '@', 'player', libtcod.white, blocks=True, fighter=fighter_component)

        #self.ticker.clear_ticker()
        #self.ticker.schedule_turn(self.player.fighter.speed, self.player)

        self.particles = []
        self.objects = []

        save_system.load(self)
        self.player.message = self.message
        self.player_hp_bar = StatusBar(self.player.fighter, BAR_WIDTH, libtcod.light_red, libtcod.darker_red, self.panel,type='hp', gEngine=self.gEngine)
        self.player_xp_bar = StatusBar(self.player.fighter, BAR_WIDTH, libtcod.light_grey, libtcod.dark_grey, self.panel,type='xp', gEngine=self.gEngine)

        self.load_level(self.depth)

        for object in self.objects:
            object.message = self.message
            object.objects = self.objects

##============================================================================
    def new_game(self):
##============================================================================
        self.logger.log.info('Starting new game.')
        #cell = ord('~')+1 chest = chr(127)
        
        fighter_component = Fighter(hp=90, defense=2, power=5, death_function=self.player_death, money=800, speed=10)
        self.player = Object(self.con,0, 0, '@', 'player', libtcod.white, blocks=True, fighter=fighter_component)
        self.player_hp_bar = StatusBar(self.player.fighter, BAR_WIDTH, libtcod.light_red, libtcod.darker_red, self.panel,type='hp', gEngine=self.gEngine)
        self.player_xp_bar = StatusBar(self.player.fighter, BAR_WIDTH, libtcod.light_grey, libtcod.dark_grey, self.panel,type='xp', gEngine=self.gEngine)
        #self.ticker.clear_ticker()
        #self.ticker.schedule_turn(self.player.fighter.speed, self.player)

        self.particles = []
        self.objects = []
        for i in xrange(1, MAX_DEPTH):
            self.current_dungeon.append(self.Map.make_map(self, i))
        
        self.gEngine.console_clear(0)
        town_menu(0, 'Welcome to Town', self, INVENTORY_WIDTH, SCREEN_HEIGHT, SCREEN_WIDTH)
        #self.initialize_fov()
     
        self.game_state = 'playing'
        self.inventory = []

        self.depth = 1
        self.load_level(self.depth, 'down')
        self.message.message('Welcome to Ascension!', 1)

    def load_level(self, level, direction=None):
        self.logger.log.info('Loading level %i' % level)
        self.ticker.schedule.clear()
        self.ticker.schedule_turn(self.player.fighter.speed, self.player)
        self.gEngine.map_init_level(self.Map.MAP_WIDTH, self.Map.MAP_HEIGHT)

        level_to_load = None
        #if direction:
        for item in self.current_dungeon:
            if item.depth == level:
                level_to_load = item
        #else:
        #    level_to_load = level

        self.objects = level_to_load.objects
        self.Map.map = level_to_load.map
        self.gEngine.set_fov_map(level_to_load.fov_map)
        #self.gEngine.set_map(level_to_load.draw_map)
        self.Map.set_draw_map(level_to_load.map, self)
        for node in level_to_load.spawn_nodes:
            self.ticker.schedule_turn(0, node)

        for item in self.objects:
            if direction:
                if item.misc:
                    if item.misc.type == 'down' and direction == 'up': # if the player goes up, we put him at down stairs
                        self.player.x = item.x
                        self.player.y = item.y
                    elif item.misc.type == 'up' and direction == 'down': # if the player goes down, we put him at the up stairs
                        self.player.x = item.x
                        self.player.y = item.y
            if item.fighter:
                self.ticker.schedule_turn(item.fighter.speed, item)
        #level_to_load = self.current_dungeon[level-1]
        self.gEngine.console_clear(0)
        self.gEngine.console_clear(self.con)
        self.initialize_fov()

        self.ticker.get_next_tick()
        self.game_state = 'playing'

##============================================================================
    def new_level(self):
##============================================================================
        self.logger.log.info('Generating new level.')
        self.ticker.schedule.clear()
        self.ticker.schedule_turn(self.player.fighter.speed, self.player)

        #self.Map.make_map(self)

        self.gEngine.console_clear(0)
        self.gEngine.console_clear(self.con)
        self.initialize_fov()
        
        self.ticker.get_next_tick()
        self.game_state = 'playing'


        self.message.message('Next Level', 1)
    
##============================================================================
    def initialize_fov(self):
##============================================================================
        self.fov_recompute = True
        self.logger.log.info('Initializing FoV.')
        self.fov_map = libtcod.map_new(MAP_WIDTH, MAP_HEIGHT)
        self.path = libtcod.path_new_using_function(MAP_WIDTH,MAP_HEIGHT,path_callback,self)
        for y in range(MAP_HEIGHT):
            for x in range(MAP_WIDTH):
                libtcod.map_set_properties(self.fov_map, x, y, not self.Map.map[x][y].blocked, not self.Map.map[x][y].block_sight)
                self.gEngine.map_set_properties(x,y,not self.Map.map[x][y].blocked, not self.Map.map[x][y].block_sight)
        self.gEngine.console_clear(self.con)#unexplored areas start black (which is the default background color)
     
##============================================================================
    def play_game(self):
##============================================================================
        try:
            player_action = None
            self.player_moved=True
            while not libtcod.console_is_window_closed():
                self.render_all()
                self.player_moved=False
                self.gEngine.console_flush()
         
                #erase all objects at their old locations, before they move
                for object in self.objects:
                    object.clear(self.gEngine)
                for particle in self.particles:
                    particle.clear(self.gEngine)
                
                #Monsters faster than the player, take turns first
                is_player_turn = self.ticker.next_turn(self)
                
                if is_player_turn:                    
                    player_action = self.handle_keys()
                    
                    ##Make sure the player takes his turn before continuing
                    ##Need to have certain actions take certain speeds
                    ##moving takes up the full speed, attacking dependant on weapon
                    ##inventory actions depend on what was done
                    while player_action == 'didnt-take-turn':
                        
                        player_action = self.handle_keys()
                        
                        if player_action == 'player-moved':
                            self.player_moved = True
                            
                        if libtcod.console_is_window_closed():
                            player_action = 'exit'
                            
                        self.render_all()                        
                        self.gEngine.console_flush()
                        
                        self.player_moved=False
                        
                        for object in self.objects:
                            object.clear(self.gEngine)
                            
                    if player_action == 'turn-used' or player_action == 'player-moved':
                        self.ticker.schedule_turn(self.player.fighter.speed,self.player)
                        
                if player_action == 'exit' or libtcod.console_is_window_closed():
                    self.logger.log.info('Exiting and saving game..')
                    self.save_game()
                    break
                    
                #fast forward until the next object gets its turn
                self.ticker.get_next_tick()
                if self.player.fighter.current_xp >= self.player.fighter.xp_to_next_level:
                    self.player.fighter.level_up()
            #check for game state = dead        
        except Exception,err:
            self.message.error_message(err,self)

##============================================================================
    def main_menu(self):
##============================================================================
        path = os.path.join(sys.path[0],'content')
        path = path.replace('core.exe','')
        img = self.gEngine.image_load(os.path.join(path,'img','menu_background_2.png'))
        m_menu = Menus(self,SCREEN_HEIGHT/2+22,SCREEN_WIDTH,24,'',['Play a new game', 'Continue last game', 'Options (not working)', 'Quit'], self.con)
        m_menu.is_visible = True
        #m_menu.can_drag = False
        
        while not libtcod.console_is_window_closed():
            self.gEngine.image_blit_2x(img, 0, 0, 0)
            r,g,b = libtcod.red
            self.gEngine.console_set_default_foreground(0, r,g,b)
            self.gEngine.console_print(0, SCREEN_WIDTH/2-13, SCREEN_HEIGHT/2-10,'By Grishnak and SentientDeth')
            libtcod.console_credits_render(2, SCREEN_HEIGHT-2, True)
            choice = m_menu.menu()
            self.gEngine.console_flush()
            
            if choice == 0:
                m_menu.destroy_menu()
                self.new_game()
                self.play_game()
                self.main_menu()
            if choice == 1:
                m_menu.destroy_menu()
                #try:
                self.load_game()
                #except:
                #    msgbox('\n No saved game to load.\n', 24)
                #    continue
                self.play_game()
                self.main_menu()
            if choice == 3 or choice == None:  #quit
                self.logger.log.info('Quitting game')
                break
##============================================================================
    def get_names_under_mouse(self):
##============================================================================
        #return a string with the names of all objects under the mouse
        mouse = libtcod.mouse_get_status()
        (x, y) = (mouse.cx, mouse.cy)
     
        #create a list with the names of all objects at the mouse's coordinates and in FOV
        names = [obj.name for obj in self.objects
            if obj.x == x and obj.y == y and libtcod.map_is_in_fov(self.fov_map, obj.x, obj.y)]
     
        names = ', '.join(names)  #join the names, separated by commas
        return names.capitalize()

##============================================================================
    def get_names_under_player(self):
##============================================================================
        if self.player_moved:
            names = []
            for object in self.objects:
                if object is not self.player:
                    if object.distance_to(self.player) == 0:
                            names.append(color_text(object.name,object.color))
                  
            n = len(names)
            if n > 0:
                names = ', '.join(names)
                if n ==1:
                    msg = color_text('You see a ',libtcod.white)
                    msg += names
                    msg += color_text(', here.',libtcod.white)
                else:
                    msg = color_text('You see ',libtcod.white)
                    msg += names
                    msg += color_text(' here.',libtcod.white)
                self.message.message(msg,0)
                        
##============================================================================
    def render_all(self):
##============================================================================
     
        if self.fov_recompute:
            #recompute FOV if needed (the player moved or something)
            fov_recompute = False
            libtcod.map_compute_fov(self.fov_map, self.player.x, self.player.y, TORCH_RADIUS, FOV_LIGHT_WALLS, FOV_ALGO)
            self.gEngine.map_draw(self.con,self.player.x,self.player.y)
            
     
        #draw all objects in the list, except the player. we want it to
        #always appear over all other objects! so it's drawn later.
        
            
        for object in self.objects:
            if object is not self.player:
                if object.misc:
                    if object.misc.type is 'up' or object.misc.type is 'down':
                        #Draw stairs if they are already found
                        if self.gEngine.map_is_explored(object.x,object.y):
                            object.draw(self.fov_map,self.gEngine,True)
                    else:
                        object.draw(self.fov_map,self.gEngine)
                else:
                    object.draw(self.fov_map,self.gEngine)
        self.player.draw(self.fov_map, self.gEngine)
        for particle in self.particles:
            particle.draw(self.fov_map,self.gEngine,True)
        #blit the contents of "con" to the root console
        self.gEngine.console_print(self.con, 1, 1, "Depth: %i" % self.depth)
        self.gEngine.console_blit(self.con, 0, 0, MAP_WIDTH, MAP_HEIGHT, 0, 0, 0, 1.0, 1.0)
     

        #prepare to render the GUI panel
        r,g,b = libtcod.black
        self.gEngine.console_set_default_background(self.panel, r, g, b)
        self.gEngine.console_clear(self.panel)
     
        #print the game messages
        self.message.flush_messages(self.gEngine)
     
        #show the player's stats
        self.player_hp_bar.render(1,1,self.gEngine)
        self.player_xp_bar.render(1,3,self.gEngine)

        #display names of objects under the mouse
        r,g,b = libtcod.light_gray
        self.gEngine.console_set_default_foreground(self.panel,r,g,b)
        self.gEngine.console_set_alignment(self.panel,libtcod.LEFT)

        self.gEngine.console_print(self.panel, 1, 5, "(%dfps)" % (libtcod.sys_get_fps()))
        self.gEngine.console_print(self.panel, 1, 0, self.get_names_under_mouse())
        
        #print a message with the names of objects under the player
        self.get_names_under_player()
        #blit the contents of "panel" to the root console
        self.gEngine.console_blit(self.panel, 0, 0, SCREEN_WIDTH, PANEL_HEIGHT, 0, 0, PANEL_Y,1.0,1.0)
     
     

##============================================================================
    def player_move_or_attack(self,dx, dy):
##============================================================================
        #the coordinates the player is moving to/attacking
        x = self.player.x + dx
        y = self.player.y + dy
     
        #try to find an attackable object there
        target = None
        for object in self.objects:
            if object.fighter and object.x == x and object.y == y:
                target = object
                break
            
        #attack if target found, move otherwise
        if target is not None:
            self.player.fighter.attack(target,True)
            return 'turn-used'
        else:
            self.player.move(dx, dy,self.Map.map,self.objects)
            self.fov_recompute = True
            return 'player-moved'

##============================================================================
    def player_death(self,player):
##============================================================================
        #the game ended!
        self.message.message('You died!', libtcod.red)
        self.game_state = 'dead'
     
        #for added effect, transform the player into a corpse!
        self.player.char = '%'
        self.player.color = libtcod.dark_red

##============================================================================
    def handle_keys(self):
##============================================================================
        key = libtcod.console_check_for_keypress(libtcod.KEY_PRESSED)
        #libtcod.sys_check_for_event()
        move_keys = {self.keys.key_north :(0,-1),
                    self.keys.key_south  :(0,1) ,
                    self.keys.key_east   :(1,0),
                    self.keys.key_west   :(-1,0),
                    }
        if key.vk == libtcod.KEY_ENTER and key.lalt:
            #Alt+Enter: toggle fullscreen
            libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())
     
        elif key.vk == libtcod.KEY_ESCAPE:
            message = 'Return to main menu?'
            w = len(message)*2
            d_box = DialogBox(self,w,10,20,20,message,type='option',con=self.con)
            first = True
            while 1:
                confirm = d_box.display_box()
                if confirm == 1:
                    d_box.destroy_box()
                    return 'exit'  #exit game
                elif confirm == 0:
                    if first:
                        first = False
                    else:
                        d_box.destroy_box()
                        return 'didnt-take-turn'
     
        if self.game_state == 'playing':
            #movement keys
            #For arrow keys, keypad keys, etc..
            if key.vk in move_keys:
                px,py=move_keys[key.vk]
                return self.player_move_or_attack(px,py)
                
            #for char based keys, 'w','a','s','d', etc..
            elif chr(key.c) in move_keys:
                px,py=move_keys[chr(key.c)]
                return self.player_move_or_attack(px,py)
                
            else:
                #test for other keys
                if key.c is ord('`') or key.c is ord('~'):
                    self.console.run_console()
                    return 'didnt-take-turn'
                    
                if key.c is ord(self.keys.key_pickup):
                    for object in self.objects:
                        if object.x == self.player.x and object.y == self.player.y and object.item:
                            object.item.pick_up(self.player.fighter.inventory)
                            return 'turn-used'
                            
                if key.c is ord('<'):
                    for object in self.objects:
                        if object.x == self.player.x and object.y == self.player.y and object.misc:
                            if object.misc.type == 'up':
                                if self.depth == 1:
                                    town_menu(0, 'Welcome to Town', self, INVENTORY_WIDTH, SCREEN_HEIGHT, SCREEN_WIDTH)
                                    return 'turn-used'
                                else:
                                    self.depth -= 1
                                    self.load_level(self.depth, 'up')

                                    return 'turn-used'
                                
                if key.c is ord('>'):
                    for object in self.objects:
                        if object.x == self.player.x and object.y == self.player.y and object.misc:
                            if object.misc.type == 'down':
                                #save previous level
                                self.logger.log.debug(self.depth)
                                #self.current_dungeon.append(Level(self.Map.map, self.objects, self.Map.depth))
                                self.depth += 1
                                self.load_level(self.depth, 'down')
                                #self.new_level()
                                return 'turn-used'
                                
                if key.c is ord(self.keys.key_equip):
                    eq = (self.player.fighter.wielded, self.player.fighter.equipment,None)
                    equipment_menu(eq, SCREEN_HEIGHT, SCREEN_WIDTH, self)
                    return 'turn-used'

                if key.c is ord(self.keys.key_char):
                    index = character_menu(0, 'Skills', self.player.fighter.skills, SCREEN_HEIGHT, SCREEN_WIDTH, self)
                    if index is not None:
                        index.increase_level(5)
                        return 'turn-used'

                if key.c is ord(self.keys.key_inventory):
                    #show the inventory; if an item is selected, use it
                    #msg = 'Press the key next to an item to use it, or any other to cancel.\n'
                    #chosen_item = inventory_menu(0, msg, self.player.fighter.inventory,INVENTORY_WIDTH,SCREEN_HEIGHT, SCREEN_WIDTH,game=self)
                    chosen_item = inventory(self.con, self.player, self)
                    if chosen_item is not None:
                        chosen_item.item.use(self.player.fighter.inventory,self.player,self)
                        return 'turn-used'
     
                if key.c is ord(self.keys.key_drop):
                    #show the inventory; if an item is selected, drop it
                    msg = 'Press the key next to an item to drop it, or any other to cancel.\n'
                    chosen_item = inventory_menu(0,msg,self.player.fighter.inventory,INVENTORY_WIDTH,SCREEN_HEIGHT,SCREEN_WIDTH,game=self)
                    if chosen_item is not None:
                        if chosen_item in self.player.fighter.inventory:
                            #self.player.objects = self.objects
                            chosen_item.objects = self.objects
                            chosen_item.item.drop(self.player.fighter.inventory, self.player)
                            chosen_item.send_to_back()
                        return 'turn-used'
                        
                return 'didnt-take-turn'
##============================================================================
    def scrolling_view(self):
##============================================================================
        pass
        self.view_map = []
        self.width = MAP_WIDTH
        self.height= MAP_HEIGHT
        self.fov_map = libtcod.map_new(self.width,self.height)
        self.view_map = [[" " for x in range(self.width)] for y in range(self.width)]
        self.item_view = []
        self.vx, self.vy = self.width//2, self.height//2
        ##Viewport code written by George from the libtcod forums
        ##==== Drawing the view port ==============
        for m in range(self.height):
            if self.player.y >= (self.map_y - self.height//2):
                y = (self.map_y - self.height) + m
                self.vy = (self.height//2) + (self.height//2 - (self.map_y - self.player.y)+1)
            elif self.player.y < self.height//2:
                y = 0 + m
                self.vy = self.player.y
            else:
                y = self.player.y - (self.height//2) + m

            for n in range(self.width):
                if self.player.x >= (self.map_x - self.width//2):
                    x = (self.map_x - self.width) + n
                    self.vx = (self.width//2) + (self.width//2 - (self.map_x - self.player.x) +1)
                elif self.player.x < self.width//2:
                    x = 0 + n
                    self.vx = self.player.x
                else:
                    x = self.player.x - (self.width//2) + n
        
        
def path_callback(xFrom,yFrom,xTo,yTo,userData):
    for obj in userData.objects:
        if obj.is_blocked(xTo,yTo,userData.Map.map,userData.objects):
            return 0.0
        else:
            return 1.0
    m = userData.Map.map
    if m[xTo][yTo].blocked:
        return 0.0
    else:
        return 1.0
        
        