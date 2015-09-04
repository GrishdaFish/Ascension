import libtcodpy as libtcod
import textwrap
import logging
import sys,os,traceback
from menu import *

class Ticker:
    def __init__(self):
        self.ticks = 0  # current ticks--sys.maxint is 2147483647
        self.schedule = {}  # this is the dict of things to do 
                            #{ticks: [obj1, obj2, ...], ticks+1: [...], ...}

    def clear_ticker(self):
        self.ticks = 0
        self.schedule = {}

    def schedule_turn(self, interval, obj):
        self.schedule.setdefault(self.ticks + interval, []).append(obj)

    def next_turn(self,game):
        things_to_do = self.schedule.pop(self.ticks, [])
        ##SORT THE LIST TO HAVE THE PLAYER TAKE HIS TURN FIRST
        ##Need to check for lists in thing_to_do
        ##if they are lists pop objects from them
        ##until we find the player, then pop the player
        ##and append the rest of the monsters back to the schedule
        ##and then schedule a new turn for the player
        player=False
        for obj in things_to_do:
            if obj != game.player:
                if obj.ai:
                    ##Simulate monsters until the players turn
                    obj.ai.take_turn(game)
                else:
                    obj.use(game)
            else:
                ##when its the players turn, confirm, 
                ##then apply the rest of the monsters
                player= True
        ##at the moment, monsters get priority for taking turns over the player.
        ##need to tweak this a bit more to get the turn
        return player
        
    def remove_object(self,object):
        ##Remove monsters that get killed before they get a turn
        for val in self.schedule.values():
            for obj in val: 
                if obj == object:
                    val.remove(object)
                    break
                    
    def get_next_tick(self):
        ##For getting the next tick with a turn, to skip past empty ticks
        ticks=self.schedule.keys()
        next_tick=ticks[0]
        for tick in ticks:
            if tick < next_tick:
                next_tick=tick
        self.ticks=next_tick
                
class log_manager:
    def __init__(self):
        self.log = logging.getLogger('main')
        self.log.setLevel(logging.DEBUG)
        #for py2exe, cant create a path in the libray.zip file
        path = os.path.join(sys.path[0],'debug')
        #path = path.replace('library.zip','')
        path = path.replace('core.exe','')
        if not os.path.exists(path):            
            os.makedirs(path)
            open(os.path.join(path,'debug.txt'),'w').close()
            open(os.path.join(path,'error.txt'),'w').close()
            open(os.path.join(path,'info.txt'),'w').close()
            
        
        formatter = logging.Formatter("[%(asctime)s] - %(name)s.%(levelname)s - [%(module)s.%(funcName)s():%(lineno)d] - %(message)s")        
        
        file_path = os.path.join(path,'debug.txt')        
        handler = logging.FileHandler(file_path,"w")
        handler.setFormatter(formatter)
        handler.setLevel(logging.DEBUG)        
        self.log.addHandler(handler)
        
        file_path = os.path.join(path,'error.txt')
        handler = logging.FileHandler(file_path,"w")
        handler.setFormatter(formatter)
        handler.setLevel(logging.ERROR)        
        self.log.addHandler(handler)
        
        file_path = os.path.join(path,'info.txt')
        handler = logging.FileHandler(file_path,"w")
        handler.setFormatter(formatter)
        handler.setLevel(logging.INFO)        
        self.log.addHandler(handler)
        
class Message:
##===============================================================================
    def __init__(self,message_console,MESSAGE_SCREEN_HEIGHT,MESSAGE_SCREEN_WIDTH,MSG_X,logger,debug):
##===============================================================================
        self.message_list = []
        self.message_log = []
        self.message_console = message_console
        self.MESSAGE_SCREEN_HEIGHT = MESSAGE_SCREEN_HEIGHT
        self.MESSAGE_SCREEN_WIDTH  = MESSAGE_SCREEN_WIDTH-MSG_X
        self.MSG_X = MSG_X
        self.logger=logger
        self.debug_level=debug
        
##===============================================================================    
    def message(self,message="",code=4):
##===============================================================================
        ##Add support for custom colored strings (code 0)
        ##Color Coding for messages
        colors = {1:(100,100,100),#grey
                2:(255,1,1),#red
                3:(255,255,1),#yellow
                4:(255,255,255),#white
                5:(255,127,1),#orange
            }
        
        self.logger.log.debug(message)
        msg = textwrap.wrap(message, self.MESSAGE_SCREEN_WIDTH)
        
        if code > len(colors):
            code = 4
            
        if code == 0:#arranging the message, with custom color coding            
            for mes in msg:
                self.message_log.append(mes)
                self.message_list.append(mes)
                
        else:##arranging the message, with no custom color coding            
            r,g,b = colors[code]
            for mes in msg:
                mes = ("%c%c%c%c%s%c"%(libtcod.COLCTRL_FORE_RGB,r,g,b,mes,libtcod.COLCTRL_STOP))
                self.message_list.append(mes)
                self.message_log.append(mes)
        
        ##If there are more messages than room to display them, drop the top one to give the scrolling effect
        while len(self.message_list) >= self.MESSAGE_SCREEN_HEIGHT - 1:
            self.message_list.pop(0)
            
        
##===============================================================================
    def flush_messages(self,gEngine):
##===============================================================================
        gEngine.console_set_alignment(self.message_console,libtcod.LEFT)
        for i in range (len(self.message_list)):
            gEngine.console_print(self.message_console, self.MSG_X, 1+i,self.message_list[i])
            
##===============================================================================
    def error_message(self,err,game):
##===============================================================================
        self.logger.log.exception(err)
        i=4
        if self.debug_level == 'debug':        
            mes = traceback.format_exc(err)
            msg=''
            mes = textwrap.wrap(mes,50)
            i=2
            for m in mes:
                msg+=m+'\n'
                i+=1
        elif self.debug_level == 'release':
            msg = 'Error! Details in debug/error.txt. Please submit a bug report.'
        confirm='Press any key to continue.'
        confirm_screen(0,msg,50,80,confirm,height=i,game=game)
        
        
class StatusBar:
##===============================================================================
    def __init__(self,owner,size,full,empty,con,type='hp',gEngine=None):
##===============================================================================
        self.bar = gEngine.image_new(size*2,2)
        self.full = full
        self.empty = empty
        self.owner = owner
        self.size = size*2
        self.con = con
        self.type = type

##===============================================================================
    def render(self,px,py,gEngine=None):
##===============================================================================
        maximum, value = 0, 0
        if self.type == 'hp':
            value = self.owner.hp
            maximum = self.owner.max_hp            
        if self.type == 'mp':
            pass            
        if self.type == 'xp':
            value = self.owner.current_xp
            maximum = self.owner.xp_to_next_level        
        if self.type == 'status':##for status ailments or buffs like poison, stun or regen
            pass

        if maximum <= 0:
            maximum = 0.1

        msg = self.type.capitalize() +': ' + str(value) + '/' +str(maximum)    
        
        if value <= 0:
            bar = int(float((self.size)) / (maximum / 0.1))
        else:
            bar = int(float((self.size)) / (float(maximum)/float(value)))

        if bar > self.size:
            bar = self.size
        r,g,b = self.empty
        gEngine.image_clear(self.bar,r,g,b)
        r,g,b = self.full
        for i in range(bar):
            gEngine.image_put_pixel(self.bar,i,0,r,g,b)
            gEngine.image_put_pixel(self.bar,i,1,r,g,b)
            
        gEngine.image_blit_2x(self.bar,self.con,px,py)
        r,g,b = libtcod.white
        gEngine.console_set_default_foreground(self.con,r,g,b)
        gEngine.console_set_alignment(self.con,int(libtcod.CENTER))
        gEngine.console_print(self.con, px + self.size / 4, py,msg)
        
##===============================================================================
    def remove_bar(self,bars):
##===============================================================================
        pass
            