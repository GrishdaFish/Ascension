import libtcodpy as libtcod
import textwrap
import sys
import StringIO
#from IPython.Shell import IPShellEmbed



#format for console commands is this:
#command (param-with-no-spaces) [additional-param-with-no-spaces]
#param and additional params are optional. Use '-' instead of spaces for paramaters

#Examples:

#spawn_consumable
##spawns a random consumable

#spawn_consumable potion
##spawns a random potion

#spawn_consumable potion light-healing
##spawns the chosen potion

class Console:
    '''Console for ingame custom commands like spawning monsters,
    items and other things, along with python interpreter commands,
    in debug mode.'''
##============================================================================
    def __init__(self,game,width,height,debug_level):
##============================================================================
        self.debug_level = debug_level
        globals().update(locals())
        self.width = width
        self.height = height
        self.game = game
        self.console = self.game.gEngine.console_new(width,height)
        self.input_list = []
        self.input_string = ''
        self.message_log = []
        self.message_list = ['Asension 0.0.1 console.']
        self.previous_command = ''
        self.capturer = StringIO.StringIO()
        self.the_real_out = sys.stdout
        sys.stdout = self.capturer 

        self.commands = {'spawn_monster' : self.spawn_monster,
            'spawn_equipment'   :self.spawn_equipment,
            'spawn_consumable'  :self.spawn_consumable,
            'python'            :self.python,
            'teleport_down'     :self.teleport_down,
            'teleport_up'       :self.teleport_up,
            'max_skills'        :self.max_skills,
            'level_up'          :self.level_up,
            
        }

##============================================================================
    def run_console(self):
##============================================================================
        console_closed = False
        while not console_closed:
            self.render()
            console_closed = self.capture_input()

##============================================================================
    def render(self):
##============================================================================
        self.game.gEngine.console_clear(self.console)
        r,g,b = libtcod.white
        self.game.gEngine.console_set_default_foreground(self.console,r,g,b)    
        self.game.gEngine.console_print_frame(self.console,0, 0, self.width, self.height, True,)
        
        temp = []
        for message in self.message_list:            
            msg = textwrap.wrap(message, self.width-2)            
            for mes in msg:
                temp.append(mes)
                self.message_log.append(mes)
        self.message_list = temp
        
        while len(self.message_list) >= self.height - 2:           
            self.message_list.pop(0)
            
        self.game.gEngine.console_set_alignment(self.console,int(libtcod.LEFT)    )
        for i in range (len(self.message_list)):
            self.game.gEngine.console_print(self.console, 1, 1+i,self.message_list[i])
        
        self.game.gEngine.console_print(self.console,1,len(self.message_list)+1,'->:%s'%self.input_string)
        
        self.game.gEngine.console_blit(self.console, 0, 0, self.width, self.height, 0, 1, 1, 1.0, 0.7)
        self.game.gEngine.console_flush()

##============================================================================
    def capture_input(self):
##============================================================================
        ##handling keyboard input and parses it
        key = libtcod.console_check_for_keypress(libtcod.KEY_PRESSED)
        if key.vk is libtcod.KEY_ESCAPE:
            self.input_string = ''
            return True
            
        if key.vk is libtcod.KEY_BACKSPACE:
            if len(self.input_list) > 0:
                self.input_list.pop()
                self.input_string = ''.join(self.input_list)
            return False
            
        if key.vk is libtcod.KEY_ENTER:
            self.message_list.append(self.input_string)
            self.parse_command()
            self.previous_command = self.input_string
            self.input_list = []
            self.input_string = ''
            return False
            
        if key.vk is libtcod.KEY_UP:
            self.input_string = self.previous_command
            return False
            
        if key.vk is libtcod.KEY_DOWN:
            self.input_list = []
            self.input_string = ''
            return False
            
        if key.c:
            self.input_list.append(chr(key.c))
            self.input_string = ''.join(self.input_list)
            return False
            
        if key.vk is libtcod.KEY_SPACE:
            self.input_list.append(' ')
            self.input_string = ''.join(self.input_list)
            return False
            
        return False

##============================================================================
    def parse_command(self):
##============================================================================
        parse = self.input_string.split()
        if len(parse) > 0:
            command = parse.pop(0)
        param = None
        additional_params = None
        if len(parse) > 0:
            param = parse.pop(0)
            if len(parse) > 0:
                additional_params = ' '.join(parse)
                
        if command in self.commands:
            com = self.commands[command]
            ex = None
            try:
                if param is None and additional_params is None:
                    com()
                    return
                if additional_params is None:
                    com(param)
                    return
                else:
                    com(param, additional_params)
                    return
            except ex:
                self.game.message.error_message(ex)

    def level_up(self):
        self.game.player.fighter.level_up()

    def max_skills(self):
        for skill in self.game.player.fighter.skills:
            skill.set_bonus(5)
##============================================================================
    def spawn_monster(self,param=None,add_param=None):
##============================================================================
        ##use the console to spawn a monster at the closest node
        node_distance = 100#set the distance really high so we can get the closest node
        ##thats also in the fov, incase we have 2 or more nodes in fov
        for node in self.game.Map.spawn_nodes:
            if libtcod.map_is_in_fov(self.game.fov_map,node.node.x,node.node.y):
                distance = self.game.player.distance_to(node.node)
                if distance < node_distance:
                    node_distance = distance
                    closest_node = node
                    
        if not param and not add_param:#random mob
            self.game.objects.append(self.game.build_objects.create_monster(self.game,
                closest_node.node.x,closest_node.node.y))
                
        if param and not add_param:#specific mob
            param = param.lower()
            param = param.replace('-',' ')
            self.game.objects.append(self.game.build_objects.create_monster(self.game,
                closest_node.node.x,closest_node.node.y,mob_name=param))
        
        #if param and add_param:#for mob sub-types (not implemented yet)
        
        for object in self.game.objects:
            object.message = self.game.message
            object.objects = self.game.objects 
            
##============================================================================
    def spawn_equipment(self,param=None,add_param=None):
##============================================================================
        #spawns equipment at the players feet
        if not param and not add_param:
            self.game.objects.append(self.game.build_objects.build_equipment(self.game,
                self.game.player.x, self.game.player.y))
                
        if param and not add_param:
            param = param.lower()
            param = param.replace('-',' ')
            self.game.objects.append(self.game.build_objects.build_equipment(self.game,
                self.game.player.x, self.game.player.y,name=param))
                
        if param and add_param:            
            param = param.lower()
            param = param.replace('-',' ')
            
            add_param = add_param.lower()
            add_param = add_param.replace('-',' ')
            
            self.game.logger.log.debug('%s %s'%(param,add_param))
            self.game.objects.append(self.game.build_objects.build_equipment(self.game,
                self.game.player.x, self.game.player.y,name=param,mat=add_param))
                
        for object in self.game.objects:
            object.message = self.game.message
            object.objects = self.game.objects

##============================================================================
    def spawn_consumable(self,param=None,add_param=None):
##============================================================================
        #spawns consumables at the players feet
        if not param and not add_param:
            r = libtcod.random_get_int(0,0,100)
            if r > 50:
                self.game.objects.append(self.game.build_objects.build_potion(self.game,
                    self.game.player.x, self.game.player.y))
            else:
                self.game.objects.append(self.game.build_objects.build_scroll(self.game,
                    self.game.player.x, self.game.player.y))
        
        if param and not add_param:
            param = param.lower()
            if param == 'potion':
                self.game.objects.append(self.game.build_objects.build_potion(self.game,
                    self.game.player.x, self.game.player.y))
            if param == 'scroll':
                self.game.objects.append(self.game.build_objects.build_scroll(self.game,
                    self.game.player.x, self.game.player.y))
                    
        if param and add_param:
            param = param.lower()
            add_param = add_param.lower()
            add_param = add_param.replace('-',' ')
            if param == 'potion':
                self.game.objects.append(self.game.build_objects.build_potion(self.game,
                    self.game.player.x, self.game.player.y,name=add_param))
            if param == 'scroll':
                self.game.objects.append(self.game.build_objects.build_scroll(self.game,
                    self.game.player.x, self.game.player.y,name=add_param))
                    
        for object in self.game.objects:
            object.message = self.game.message
            object.objects = self.game.objects
            
##============================================================================
    def python(self, param=None, add_param=None):
##============================================================================
        ##for the shell commands, only accessable in debug mode
        if self.debug_level == 'debug':
            if param and add_param:
                command = param + ' ' + add_param
                position = self.capturer.tell()
                try:
                    exec(command)
                except:
                    output = ['Command failed']
                else:
                    self.message_list.append('Command accepted')
                    self.capturer.seek(position,0)
                    output = self.capturer.read().split('\n')            
                finally:
                    for line in output:
                        self.message_list.append('>>>'+line)                
            else:
                #self.message_list.append('Not enough parameters passed!')
                command = param
                position = self.capturer.tell()
                try:
                    exec(command)
                except:
                    output = ['Command failed']
                else:
                    self.message_list.append('Command accepted')
                    self.capturer.seek(position,0)
                    output = self.capturer.read().split('\n')
                finally:
                    for line in output:
                        self.message_list.append('>>>'+line)
        
    def teleport_down(self):
        if self.debug_level == 'debug':
            for tile in self.game.objects:
                if tile.misc:
                    if tile.misc.type == 'down':
                        self.game.player.x = tile.x
                        self.game.player.y = tile.y
                        return

    def teleport_up(self):
        if self.debug_level == 'debug':
            for tile in self.game.objects:
                if tile.misc:
                    if tile.misc.type == 'up':
                        self.game.player.x = tile.x
                        self.game.player.y = tile.y
                        return