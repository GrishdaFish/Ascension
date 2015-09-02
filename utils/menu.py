import sys,os,time
sys.path.append(sys.path[0])
import libtcodpy as libtcod
sys.path.append(os.path.join(sys.path[0],'object'))
from object import *
from item import *
from spells import *


class Menus:
##============================================================================
    def __init__(self,game,screen_height,screen_width,width,header,options,
        con=None,bg=None,cl_options=None):
##============================================================================
        self.is_dragging = False
        self.in_drag_zone = False
        self.mouse_highlight = False
        self.game = game
        self.cl_options = cl_options
        self.img = None
        if bg:
            self.img = game.gEngine.image_load(bg)
            
        self.screen_height = screen_height
        self.screen_width = screen_width
        
        self.header = header
        #if len(self.header) == 0:
        #    self.header = '======='
        self.header_o = self.header
        
        self.options = options
        
        height = len(options)
        width+=5
        height+=2
        #self.header_pos = (width//2)-len(header)
        
        self.window = game.gEngine.console_new(width, height)
        
        
        self.game.gEngine.console_set_alignment(self.window,2)
            
        self.width = width
        self.height = height
        self.w_pos = screen_width/2 - width/2
        self.h_pos = screen_height/2 - height/2
        
        self.is_visible = False
        self.can_drag = True
        
        self.last_input = 0
        libtcod.mouse_get_status()#this is to pick up stray mouse input that 
        #shouldnt be picked up.
##============================================================================
    def menu(self):
##============================================================================
        if self.is_visible:
            
            y = 0
            letter_index = ord('a')
            r,g,b = libtcod.white
                
            if self.img:
                self.game.gEngine.image_blit_2x(self.img, 0, 0, 0)
                
            self.game.gEngine.console_set_default_foreground(self.window, r,g,b)
            self.game.gEngine.console_blit(self.window, 0, 0,self.width,
                self.height,0,self.w_pos,self.h_pos,1.0, 1.0)
                
            self.game.gEngine.console_print_frame(self.window,0, 0, 
                self.width, self.height, False)
            
            if self.can_drag:    
                self.game.gEngine.console_print(self.window,self.width/2,0,self.header)
                
            self.game.gEngine.console_print(self.window, 0, 0, chr(254))
            self.game.gEngine.console_print(self.window, self.width-1, 0, chr(158))            
            
            for i in range(len(self.options)):
                text = '(' + chr(letter_index) + ') ' + self.options[i]
                self.game.gEngine.console_print(self.window, self.width/2, y+1, text)
                y+=1
                letter_index += 1
            
            self.game.gEngine.console_flush()
            m_input = self.mouse_input()
            k_input = self.key_input()
            if m_input != -1:
                if m_input == 'close':                    
                    return None
                else:
                    return m_input
                    
            if k_input != -1:
                if k_input == 'close':
                    return None
                else:
                    return k_input
                    
            return -1    
    
##============================================================================
    def destroy_menu(self):
##============================================================================
        if self.img:
            self.game.gEngine.image_delete(self.img)
        self.game.gEngine.console_remove_console(self.window)
        
##============================================================================
    def mouse_input(self):
##============================================================================
        ##Menu Mouse Input
        mouse = libtcod.mouse_get_status()
        mx = mouse.cx -self.w_pos
        my = mouse.cy -self.h_pos
        
        ##for dragging
        if mx >= 2 and mx <= self.width-2 and my == 0:                                   
            self.in_drag_zone = True
            if not self.is_dragging:
                self.header = color_text(self.header_o,libtcod.red)              
        else:
            if not self.is_dragging:
                self.header = color_text(self.header_o,libtcod.white)
                self.in_drag_zone = False

        if mouse.lbutton and not self.is_dragging and self.in_drag_zone:
            self.is_dragging = True            
            self.header = color_text(self.header_o,libtcod.green)
            self.dragx = mx
            self.dragy = my
            
        elif not mouse.lbutton and self.is_dragging:
            self.is_dragging = False
           
        elif self.is_dragging and self.can_drag:
            self.w_pos = mouse.cx - self.dragx
            self.h_pos = mouse.cy - self.dragy
            
        ##For Close button
        if mouse.cx == self.w_pos + self.width-1 and mouse.cy == self.h_pos and not self.is_dragging:
            t = color_text('X',libtcod.red)
            self.game.gEngine.console_print(self.window, self.width-1, 0,t)
            if mouse.lbutton_pressed:
                libtcod.mouse_get_status()
                return 'close'
                
        ##For Menu Options        
        letter_index = ord('a')
        if mouse.cx >= self.w_pos and mouse.cx <= self.w_pos+self.width and not self.is_dragging:
            for i in range(len(self.options)):
                if my == i+1:
                    if self.cl_options is not None:
                        t = '(' + chr(letter_index+i) + ') ' + self.cl_options[i].capitalize()
                    else:
                        t = '(' + chr(letter_index+i) + ') ' + self.options[i].capitalize()
                    text = color_text(t,color_f=libtcod.red)
                    self.game.gEngine.console_print(self.window, self.width/2, i+1, text)
                    self.mouse_highlight = True
                    mouse_choice = i
                    break
                else:
                    self.mouse_highlight = False
                    
        ##bug here, after selecting a choice, the next menu gets "clicked" as well.
        ##FIXED. Just called mouse_get_status() on __init__ and before a return
        ##to pick up unwanted input
        if mouse.lbutton_pressed and self.mouse_highlight and not self.is_dragging:
            if not mouse.lbutton:
                libtcod.mouse_get_status()
                return mouse_choice
        return -1
        
##============================================================================
    def key_input(self):
##============================================================================
        ##Menu Keyboard Input
        key = libtcod.console_check_for_keypress()  
        
        index = key.c - ord('a')
        
        if key.vk == libtcod.KEY_ENTER and key.lalt:
            libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())
            
        if key.vk == libtcod.KEY_ESCAPE:
            libtcod.console_check_for_keypress() 
            return 'close'
            
        if key:
            if index >= 0 and index < len(self.options):
                libtcod.console_check_for_keypress() 
                return index
            
        #if key.vk == libtcod.KEY_DOWN:
        #    current_pick = (current_pick +1) % len(self.options)
               
        #if key.vk == libtcod.KEY_UP:
        #    current_pick = (current_pick -1) % len(self.options)
               
        #if key.vk == libtcod.KEY_ENTER:
        #    return current_pick
        
        return -1
        
class Button:
##============================================================================
    def __init__(self, dest_x=0, dest_y=0,parent=None, label=None, x_pos=None, y_pos=None, type=True, game=None, window=None):
##============================================================================
        self.width = 4 + len(label)
        self.height = 5
        self.x_pos = x_pos
        self.y_pos = y_pos
        if parent is None:
            self.game = game
            self.parent = self
            self.dest_window = window
            self.dest_x = dest_x
            self.dest_y = dest_y
        else:
            self.parent = parent
            self.dest_window = self.parent.window
            self.dest_x = self.parent.x_pos
            self.dest_y = self.parent.y_pos
        self.window = self.parent.game.gEngine.console_new(self.width, self.height)
        self.label = label
        self.label_o = label
        r,g,b = libtcod.white
        self.parent.game.gEngine.console_set_default_foreground(self.window, r,g,b)
        self.parent.game.gEngine.console_set_alignment(self.window,2)
        self.type = type

##============================================================================
    def display(self):
##============================================================================
        self.parent.game.gEngine.console_blit(self.window, 0, 0,self.width,
            self.height,self.dest_window,self.x_pos,self.y_pos,1.0, 1.0)

        self.parent.game.gEngine.console_print_frame(self.window,0, 0, 
            self.width, self.height, False)
            
        self.parent.game.gEngine.console_print(self.window, self.width/2, 
            self.height/2, self.label)    
        self.parent.game.gEngine.console_flush()    
        m = self.mouse_input()
        k = self.key_input()
        return m,k
        
##============================================================================
    def destroy_button(self):
##============================================================================
        self.parent.game.gEngine.console_remove_console(self.window)
        
##============================================================================
    def mouse_input(self):
##============================================================================
        mouse = libtcod.mouse_get_status()
        mx = mouse.cx -(self.x_pos + self.dest_x)
        my = mouse.cy -(self.y_pos + self.dest_y)
        
        if mx >= 0 and mx <= self.width and my >= 0 and my <= self.height:
            self.label = color_text(self.label_o,libtcod.red)
            if mouse.lbutton:
                self.label = color_text(self.label_o,libtcod.green)
                if mouse.lbutton_pressed:
                    if self.type is True:
                        return 1
                    else:
                        return 0
            if mouse.lbutton_pressed:
                if self.type is True:
                    return 1
                else:
                    return 0
        else:
            self.label = color_text(self.label_o, libtcod.white)
            
        return -1
    
    def key_input(self):
        key = libtcod.console_check_for_keypress()  
        
        if key.vk == libtcod.KEY_ENTER or key.vk == libtcod.KEY_SPACE:
            libtcod.console_check_for_keypress() 
            return 1
        if key.vk == libtcod.KEY_ESCAPE:
            libtcod.console_check_for_keypress() 
            return 0
        return -1
        
class DialogBox:
##============================================================================
    def __init__(self,game,width,height,x_pos,y_pos,body_text,type='dialog',
        option_labels=None,con=None):
##============================================================================
        self.game = game
        self.width = width
        self.con = 0#con
        #if con is None:
        #    self.con = 0
        self.height = height
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.buttons = []
        self.body_text = body_text
        self.window = game.gEngine.console_new(self.width,self.height)
        self.body_height = game.gEngine.console_get_height_rect(self.window, 1, 1, 
            self.width, self.height, body_text)
        
        if self.body_height > self.height-2:            
            self.game.gEngine.console_remove_console(self.window)
            self.height = self.body_height+2           
            self.window = game.gEngine.console_new(self.width,self.height)            
        
        if type == None or type == 'dialog':
            self.run = self.dialog_box
            self.option_labels = option_labels
            if option_labels == None:
                self.option_labels = ['Ok']
            self.buttons.append(Button(parent=self,label=self.option_labels[0],
                x_pos=self.width//2-5,y_pos=self.height/2-1,type=True))
            
        elif type == 'option':
            self.run = self.option_box
            self.option_labels = option_labels
            if option_labels == None:
                self.option_labels = ['Yes','No']
            self.buttons.append(Button(parent=self,label=self.option_labels[0],
                x_pos=self.width//6-5,y_pos=self.height/2-1,type=True))
            self.buttons.append(Button(parent=self,label=self.option_labels[1],
                x_pos=self.width//3-5,y_pos=self.height/2-1,type=False))
        self.last_input=0
        libtcod.mouse_get_status()
        
##============================================================================
    def display_box(self):
##============================================================================
        input = -1
        while input == -1:
            input = self.run()
        libtcod.mouse_get_status()
        libtcod.console_check_for_keypress() 
        return input

##============================================================================
    def dialog_box(self):
##============================================================================
        input = [-1,-1]
        
        self.game.gEngine.console_blit(self.window, 0, 0,self.width,
            self.height,self.con,self.x_pos,self.y_pos,1.0, 1.0)        
            
        self.game.gEngine.console_print_frame(self.window,0, 0, 
            self.width, self.height, False)
        
        self.game.gEngine.console_print(self.window, 1, 
            1, self.body_text)            
        
        self.game.gEngine.console_flush()
        input = self.buttons[0].display()
        for i in input:
            if i != -1:
                return 1
        return -1
        
##============================================================================
    def option_box(self):
##============================================================================
        input = [-1,-1]
        
        self.game.gEngine.console_blit(self.window, 0, 0,self.width,
            self.height,self.con,self.x_pos,self.y_pos,1.0, 1.0)        
            
        self.game.gEngine.console_print_frame(self.window,0, 0, 
            self.width, self.height, False)
        
        self.game.gEngine.console_print(self.window, 1, 
            1, self.body_text)
            
        
        self.game.gEngine.console_flush()
        
        input = self.buttons[0].display()
        for i in input:
            if i != -1:
                return i
        
        self.game.gEngine.console_flush()
        
        input = self.buttons[1].display()
        for i in input:
            if i != -1:
                return i
                
        return -1

##============================================================================
    def destroy_box(self):
##============================================================================
        ##UNCOMMENT LATER AFTER THE ENGINE IS FIXED
        #for item in self.buttons:
        #    item.destroy_button()
        if len(self.buttons) == 1:
            self.game.gEngine.console_remove_console(self.buttons[0].window)
        if len(self.buttons) == 2:
            self.game.gEngine.console_remove_console(self.buttons[1].window)
            self.game.gEngine.console_remove_console(self.buttons[0].window)
        self.game.gEngine.console_remove_console(self.window)

##============================================================================
    def mouse_input(self):
##============================================================================
        mouse = libtcod.mouse_get_status()
        mx = mouse.cx -self.x_pos
        my = mouse.cy -self.y_pos
        
##============================================================================
    def key_input(self):
        pass


##============================================================================
def menu(con,header, options, width,SCREEN_HEIGHT,SCREEN_WIDTH,bg=None,game=None,under=None):
##============================================================================
    ##for menus that dont need to have positions tracked
    if len(options) > 26:
        if game:
            game.logger.error('Cannot have a menu with more than 26 options.')
        raise ValueError('Cannot have a menu with more than 26 options.')
        
    if header == '':
        header = '======='
    if bg:
        img = game.gEngine.image_load(bg)
        game.gEngine.image_blit_2x(img, 0, 0, 0)
        
    height = len(options)
    width+=5
    height+=2
    header_pos = (width//2)-len(header)
    
    window = game.gEngine.console_new(width, height)
    
    current_pick = 0
    y = 0
    letter_index = ord('a')
    w_pos = SCREEN_WIDTH/2 - width/2
    h_pos = SCREEN_HEIGHT/2 - height/2    
    
    r,g,b = libtcod.white
    game.gEngine.console_set_default_foreground(window, r,g,b)    
    original_header = header
    is_dragging = False
    in_drag_zone = False
    mouse_highlight = False
    mouse = None
    key = libtcod.console_check_for_keypress()
    first_run = True

    while key.vk is not libtcod.KEY_NONE:
        key = libtcod.console_check_for_keypress(True)

    while not libtcod.console_is_window_closed():
        game.gEngine.console_flush()    
        game.gEngine.console_blit(window, 0, 0,width,height,0,w_pos,h_pos,1.0, 1.0)
        
        game.gEngine.console_clear(window)
        
        game.gEngine.console_print_frame(window,0, 0, width, height, False)
        
        game.gEngine.console_print(window,header_pos,0,header)
        game.gEngine.console_print(window, 0, 0, chr(254))
        game.gEngine.console_print(window, width-1, 0, chr(158))        
        
        for i in range(len(options)):
            text = '(' + chr(letter_index) + ') ' + options[i]
            game.gEngine.console_print(window, 1, y+1, text)
            y+=1
            letter_index += 1
        y = 0
        letter_index = ord('a')
        
        ##Menu Mouse Input
        mouse = libtcod.mouse_get_status()
        mx = mouse.cx -w_pos
        my = mouse.cy -h_pos
        
        ##for dragging
        if mouse.cx >= w_pos+header_pos and mouse.cx <= w_pos+header_pos+len(original_header)-1 and mouse.cy == h_pos:                        
            in_drag_zone = True
            if not is_dragging:
                header = color_text(original_header,libtcod.red)
        else:                
            header = color_text(original_header,libtcod.white)
            in_drag_zone = False

        if mouse.lbutton and not is_dragging and in_drag_zone:
            is_dragging = True            
            header = color_text(original_header,libtcod.green)
            dragx = mx
            dragy = my
            
        elif not mouse.lbutton and is_dragging:
            is_dragging = False
            
        elif is_dragging:
            w_pos = mouse.cx - dragx
            h_pos = mouse.cy - dragy
            
        ##For Close button
        if mouse.cx == w_pos+width-1 and mouse.cy == h_pos:
            t = color_text('X',libtcod.red)
            game.gEngine.console_print(window, width-1, 0,t)
            if mouse.lbutton_pressed:
                if bg:
                    game.gEngine.image_delete(img)
                libtcod.mouse_get_status()
                return None
                
        ##For Menu Options
        if mouse.cx >= w_pos and mouse.cx <= w_pos+width:
            for i in range(len(options)):
                if my == i+1:
                    t = '(' + chr(letter_index+i) + ') ' + options[i].capitalize()
                    text = color_text(t,color_f=libtcod.red)
                    game.gEngine.console_print(window, 1, i+1, text)
                    mouse_highlight = True
                    mouse_choice = i
                    break
                else:
                    mouse_highlight = False
                    
        ##bug here, after selecting a choice, the next menu gets "clicked" as well.
        ##if set to lbutton, only the last option in a list seems to work
        if mouse.lbutton and mouse_highlight:
            if bg:
                game.gEngine.image_delete(img)
            libtcod.mouse_get_status()
            return mouse_choice
      
        ##Menu Keyboard Input
        key = libtcod.console_check_for_keypress(True)
        
        index = key.c - ord('a')
        
        if key.vk == libtcod.KEY_ENTER and key.lalt:
            libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())
            
        if key.vk == libtcod.KEY_ESCAPE:
            game.gEngine.console_remove_console(window)
            if bg:
                game.gEngine.image_delete(img)
            libtcod.console_check_for_keypress() 
            return None
            
        if key:
            if index >= 0 and index < len(options):
                game.gEngine.console_remove_console(window)
                if bg:
                    game.gEngine.image_delete(img)
                libtcod.console_check_for_keypress() 
                return index
            
        if key.vk == libtcod.KEY_DOWN:
            current_pick = (current_pick +1) % len(options)
               
        if key.vk == libtcod.KEY_UP:
            current_pick = (current_pick -1) % len(options)
               
        if key.vk == libtcod.KEY_ENTER:
            game.gEngine.console_remove_console(window)
            if bg:
                game.gEngine.image_delete(img)
            libtcod.console_check_for_keypress() 
            return current_pick
            
        first_run = False


##============================================================================
def msgbox(text, width=50,con=None,SCREEN_HEIGHT=50,SCREEN_WIDTH=80):
##============================================================================
    menu(con,text, [], width,SCREEN_HEIGHT,SCREEN_WIDTH)  #use menu() as a sort of "message box"


#to help reduce overall lines of code for coloring weapon names and such
##============================================================================
def color_text(text,color_f=None,color_b=None,game=None):
##============================================================================
    #changed to not use color codes, as the items were all colored the same
    #this gives the intended effect
    #txt = text.capitalize()
    txt =text
    if color_f:
        rf,gf,bf = color_f
        #make sure none of the rgb vlaues are 0
        if rf == 0:rf=1
        if gf == 0:gf=1
        if bf == 0:bf=1
    if color_b:
        rb,gb,bb = color_b
        #make sure none of the rgb vlaues are 0
        if rb == 0:rb=1
        if gb == 0:gb=1
        if bb == 0:bb=1
    ##if text is colored and we just need background changed (highlighting)
    ##Cant just change the background color here. not working for some stupid reason
    if not color_f and color_b:
        return '%c%c%c%c%s%c'%(libtcod.COLCTRL_BACK_RGB,rb,gb,bb,txt,libtcod.COLCTRL_STOP)
    if color_f and not color_b:
        return '%c%c%c%c%s%c'%(libtcod.COLCTRL_FORE_RGB,rf,gf,bf,txt,libtcod.COLCTRL_STOP)
    if color_f and color_b:
        return "%c%c%c%c%c%c%c%c%s%c"%(libtcod.COLCTRL_FORE_RGB,rf,gf,bf,
            libtcod.COLCTRL_BACK_RGB,rb,gb,bb,txt,libtcod.COLCTRL_STOP)
    

##============================================================================
def equipment_menu(equipment,screen_height,screen_width,game):
##============================================================================
    slots = ['torso',
             'head',
             'hands',
             'legs',
             'feet',
             'arms',
             'shoulders',
             'back']

    options = []
    wielded = equipment[0]
    equip = equipment[1]
    acc = equipment[2]
    equip_option=[]
    
    if wielded[0]:
        item = 'Right hand: '+color_text(wielded[0].name,wielded[0].color)        
    else:
        item = 'Right hand: Empty'
    options.append(item)
    equip_option.append(wielded[0])
    if wielded[1]:
        item = 'Left hand: '+color_text(wielded[1].name,wielded[1].color)         
    else:
        item = 'Left hand: Empty'        
    options.append(item)
    equip_option.append(wielded[1])
    
    for i in range(len(slots)):
        if not equip[i]:
            s =slots[i]
            item = s.capitalize() + ': Empty'
        else:
            s=slots[i].capitalize()
            item = s+ ': '+color_text(equip[i].name,equip[i].color)  
        equip_option.append(equip[i])
        options.append(item)
    width = 6    
    letter_index = ord('a')
    for item in options:
        if len(item) > width:
            width = len(item)
    
    width+=6
    height = 22
    window = game.gEngine.console_new(width,height)
    r,g,b = libtcod.white
    game.gEngine.console_set_default_foreground(window,r,g,b)    
    game.gEngine.console_print_frame(window,0, 0, width, height, True)#,'Equipment')
    #game.gEngine.console_hline(window,1,4,width-2)
    game.gEngine.console_print(window, width//2, 4,'Armor')
    
    for i in range(len(options)):
        if i < 2:
            text = '(' + chr(letter_index) + ') ' + options[i]
            game.gEngine.console_print(window,1,i+1,text)            
        else:
            text = '(' + chr(letter_index) + ') ' + options[i]
            game.gEngine.console_print(window,1,i+4,text)
        letter_index += 1
        
    x = screen_width/2 - width/2
    y = screen_height/2 - height/2
    
    game.gEngine.console_blit(window, 0, 0, width, height, 0, x, y, 1.0, 0.7)
 
    #present the root console to the player and wait for a key-press
    game.gEngine.console_flush()
    
    key = libtcod.console_wait_for_keypress(True)
    index = key.c - ord('a')
    if index >= 0 and index < len(options): 
        if index < 2:##For Weapons
            if equip_option[index]:##If something is equipped on the slot, remove it
                msg = 'Take off '+color_text(equip_option[index].name,equip_option[index].color)+' ?'                
                if confirm_screen(0,msg,screen_height,screen_width,game=game):                    
                    equip_option[index].item.equipment.un_equip(game.player,equip_option[index])
                    if equip_option[index].item.equipment.handed == 2:
                        if index == 0:
                            wielded[1] = None
                        else:
                            wielded[0] = None
                    wielded[index]=None
                    
            else:##otherwise pop into the inventory, to select an item to equip
                msg='Please select a weapon to equip.'
                opt=[]
                for item in game.player.fighter.inventory:##grab only weapons
                    if item.item.equipment:
                        if item.item.equipment.type=='melee':
                            #item = color_text(item.name,item.color)
                            opt.append(item)
                chosen=inventory_menu(0,msg,opt,50,screen_height,screen_width,game=game)
                if chosen:##if one was selected, confirm to equip it
                    if not isinstance(chosen, int):
                        msg = 'Put on '+color_text(chosen.item.owner.name,chosen.item.owner.color)+' ?'
                        if confirm_screen(0,msg,screen_height,screen_width,game=game):
                            chosen.item.use(game.player.fighter.inventory,game.player,game)
                
        else:##Armor, same procedure as weapons
            if equip_option[index]:
                msg = 'Take off '+color_text(equip_option[index].name,equip_option[index].color)+' ?'               
                if confirm_screen(0,msg,screen_height,screen_width,game=game):                    
                    equip_option[index].item.equipment.un_equip(game.player,equip_option[index])
                    equip[index-2]=None
                    
            else:
                msg='Please select a piece of armor to equip.'
                opt=[]
                for item in game.player.fighter.inventory:
                    if item.item.equipment:
                        if item.item.equipment.type=='armor':
                            #item = color_text(item.name,item.color)
                            opt.append(item)
                chosen=inventory_menu(0,msg,opt,50,screen_height,screen_width,game=game)
                if chosen:
                    if not isinstance(chosen, int):
                        msg = 'Put on '+color_text(chosen.item.owner.name, chosen.item.owner.color)+' ?'
                        if confirm_screen(0,msg,screen_height,screen_width,game=game):
                            chosen.item.use(game.player.fighter.inventory,game.player,game)
                        
        game.gEngine.console_remove_console(window)
        return
    game.gEngine.console_remove_console(window)
    return


##============================================================================
def inventory_menu(con,header,inventory,INVENTORY_WIDTH,SCREEN_HEIGHT,
    SCREEN_WIDTH,is_name=False,game=None):
##============================================================================
    #show a menu with each item of the inventory as an option
    if len(inventory) == 0:
        options = ['Inventory is empty.']
    elif not is_name:
        options = [color_text(item.name, item.color) for item in inventory]
    else:
        options = inventory
    index = menu(con, header, options, INVENTORY_WIDTH,SCREEN_HEIGHT,SCREEN_WIDTH,game=game)
    #if an item was chosen, return it
    if index is None or len(inventory) == 0:
        return None
    if not is_name:
        return inventory[index]#.item
    else:
        return index


def inventory(con, player, game, width=80, height=43):
    equip_height = 12
    wield_height = 6
    compare_height = height - (equip_height - wield_height)-(wield_height*2)

    r, g, b = libtcod.white
    equip_y = wield_height
    compare_y = equip_height + wield_height

    inventory_window = game.gEngine.console_new(width/2, height)
    game.gEngine.console_set_default_foreground(inventory_window, r, g, b)
    game.gEngine.console_print_frame(inventory_window, 0, 0, width/2, height, True)

    equipment_window = game.gEngine.console_new(width/2, equip_height)
    game.gEngine.console_set_default_foreground(equipment_window, r, g, b)
    game.gEngine.console_print_frame(equipment_window, 0, 0, width/2, equip_height, True)

    wielded_window = game.gEngine.console_new(width/2, wield_height)
    game.gEngine.console_set_default_foreground(wielded_window, r, g, b)
    game.gEngine.console_print_frame(wielded_window, 0, 0, width/2, wield_height, True)

    compare_window = game.gEngine.console_new(width/2, compare_height)
    game.gEngine.console_set_default_foreground(compare_window, r, g, b)
    game.gEngine.console_print_frame(compare_window, 0, 0, width/2, compare_height, True)

    slots = ['Torso',
             'Head',
             'Hands',
             'Legs',
             'Feet',
             'Arms',
             'Shoulders',
             'Back']
    #self.buttons.append(Button(self, self.option_labels[0], self.width//6-5, self.height/2-1, True))
    exit_button = Button(label='Exit', game=game,x_pos=(width/2)-9, y_pos=height-6, window=inventory_window,
                         dest_x=width/2, dest_y=0)
    if len(player.fighter.inventory) == 0:
        inventory_items = ['Inventory is empty.']
    else:
        inventory_items = [color_text(item.name.capitalize(), item.color) for item in player.fighter.inventory]

    i_header = 'Inventory'
    i_header_size = len(i_header)
    i_header_pos = (width/4)-(i_header_size/2)

    w_header = 'Weapons'
    w_header_size = len(w_header)
    w_header_pos = (width/8) - (w_header_size/2)

    e_header = 'Equipment'
    e_header_size = len(e_header)
    e_header_pos = (width/8) - (e_header_size/2)

    c_header = 'Compare/Examine'
    c_header_size = len(c_header)
    c_header_pos = (width/8) - (c_header_size/2)

    return_item = None
    key = libtcod.console_check_for_keypress(True)
    current_selection = None
    while key.vk != libtcod.KEY_ESCAPE:
        game.gEngine.console_flush()
        # get input just after flush
        key = libtcod.console_check_for_keypress(True)
        mouse = libtcod.mouse_get_status()

        game.gEngine.console_blit(inventory_window, 0, 0, width/2, height, 0, (width/2), 0, 1.0, 0.7)
        game.gEngine.console_blit(wielded_window, 0, 0, width/2, height, 0, 0, 0, 1.0, 0.7)
        game.gEngine.console_blit(equipment_window, 0, 0, width/2, height, 0, 0, equip_y, 1.0, 0.7)
        game.gEngine.console_blit(compare_window, 0, 0, width/2, height, 0, 0, compare_y, 1.0, 0.7)

        game.gEngine.console_clear(inventory_window)
        game.gEngine.console_clear(wielded_window)
        game.gEngine.console_clear(equipment_window)
        game.gEngine.console_clear(compare_window)

        # set up draw screen
        r, g, b = libtcod.white
        game.gEngine.console_set_default_foreground(inventory_window, r, g, b)
        game.gEngine.console_print_frame(inventory_window, 0, 0, width/2, height, True)

        game.gEngine.console_set_default_foreground(equipment_window, r, g, b)
        game.gEngine.console_print_frame(equipment_window, 0, 0, width/2, equip_height, True)

        game.gEngine.console_set_default_foreground(wielded_window, r, g, b)
        game.gEngine.console_print_frame(wielded_window, 0, 0, width/2, wield_height, True)

        game.gEngine.console_set_default_foreground(compare_window, r, g, b)
        game.gEngine.console_print_frame(compare_window, 0, 0, width/2, compare_height, True)


        # ========================================================================
        # print inventory
        # ========================================================================
        game.gEngine.console_print(inventory_window, i_header_pos, 0, i_header)
        letter_index = ord('a')
        y = 1
        for i in range(len(inventory_items)):
            text = '(' + chr(letter_index) + ') ' + inventory_items[i]
            if current_selection == y :
                r, g, b = libtcod.color_lerp(player.fighter.inventory[i].color, libtcod.blue, 0.5)
                game.gEngine.console_set_default_background(inventory_window, r, g, b)
            else:
                game.gEngine.console_set_default_background(inventory_window, 0, 0, 0)
            game.gEngine.console_print_ex(inventory_window, 1, y+2, libtcod.BKGND_SET, libtcod.LEFT, text)
            y += 1
            letter_index += 1
        game.gEngine.console_set_default_background(inventory_window, 0, 0, 0)
        # ========================================================================
        # print equipped weapons
        # ========================================================================
        game.gEngine.console_print(wielded_window, w_header_pos, 0, w_header)
        index = ord('1')
        if player.fighter.wielded[0] is None:
            text = '(' + chr(index) + ') ' + 'Left Hand: ' + 'Empty'
        else:
            t = color_text(player.fighter.wielded[0].name.capitalize(), player.fighter.wielded[0].color)
            text = '(' + chr(index) + ') ' + 'Left Hand: ' + t
        index += 1
        game.gEngine.console_print(wielded_window, 1, 2, text)
        if player.fighter.wielded[1] is None:
            text = '(' + chr(index) + ') ' + 'Left Hand: ' + 'Empty'
        else:
            t = color_text(player.fighter.wielded[1].name.capitalize(), player.fighter.wielded[1].color)
            text = '(' + chr(index) + ') ' + 'Left Hand: ' + t
        index += 1
        game.gEngine.console_print(wielded_window, 1, 3, text)

        # ========================================================================
        # print equipped armor
        # ========================================================================
        game.gEngine.console_print(equipment_window, e_header_pos, 0, e_header)
        i = 0
        for item in player.fighter.equipment:
            text = '(' + chr(index) + ') ' + slots[i] + ': '
            if item is None:
                text += 'Empty'
            else:
                text += color_text(player.fighter.equipment[i].name.capitalize(), player.fighter.equipment[i].color)
            game.gEngine.console_print(equipment_window, 1, i+2, text)
            i += 1
            index += 1
        game.gEngine.console_print(compare_window, c_header_pos, 0, c_header)

        # ========================================================================
        # handle mouse input
        # ========================================================================

        # Inventory input
        if mouse.cx >= width/2 <= width:  # inventory screen dims
            if (mouse.cy-2) < len(inventory_items):
                item = player.fighter.inventory[mouse.cy-2]
                current_selection = mouse.cy-2
                if item.item.equipment:
                    game.gEngine.console_print(compare_window, 1, 2, 'Name:     ' + color_text(item.name.capitalize(), item.color))
                    game.gEngine.console_print(compare_window, 1, 3, 'Type:     ' + item.item.equipment.type.capitalize())
                    if item.item.equipment.type == 'melee':
                        damage = '%dd%d+%d' % (item.item.equipment.damage.nb_dices, item.item.equipment.damage.nb_faces, item.item.equipment.damage.addsub )
                        game.gEngine.console_print(compare_window, 1, 4, 'Damage:   ' + damage)
                        game.gEngine.console_print(compare_window, 1, 5, 'Accuracy: ' + str(item.item.equipment.accuracy))
                    else:
                        game.gEngine.console_print(compare_window, 1, 4, 'Armor:    ' + str(item.item.equipment.bonus))
                        game.gEngine.console_print(compare_window, 1, 5, 'Penalty:  ' + str(item.item.equipment.penalty))
                    game.gEngine.console_print(compare_window, 1, 6, 'Value:    ' + str(item.item.value))
                if item.item.spell:
                    game.gEngine.console_print(compare_window, 1, 2, 'Name:   ' + color_text(item.name.capitalize(), item.color))
                    game.gEngine.console_print(compare_window, 1, 3, 'Type:   ' + item.item.spell.type.capitalize())
                    game.gEngine.console_print(compare_window, 1, 4, 'Power:  ' + str(item.item.spell.min) + '-' + str(item.item.spell.max))
                    game.gEngine.console_print(compare_window, 1, 5, 'Range:  ' + str(item.item.spell.range))
                    game.gEngine.console_print(compare_window, 1, 6, 'Radius: ' + str(item.item.spell.radius))
                    game.gEngine.console_print(compare_window, 1, 7, 'Value:  ' + str(item.item.value))
                if mouse.lbutton_pressed and item.item.spell:
                    i_n = color_text(item.name.capitalize(), item.color)
                    message = 'Do you want to use %s?' % i_n
                    w = len(message)+2
                    d_box = DialogBox(game, w, 10, width/4, height/2, message, type='option', con=inventory_window)
                    confirm = d_box.display_box()
                    if confirm == 1:  # make sure if the player uses a scroll or potion, we exit inventory
                        d_box.destroy_box()
                        # Remember to remove consoles in reverse order of creation to avoid OOB errors
                        return_item = item
                        break
                    else:
                        d_box.destroy_box()
                if mouse.lbutton_pressed and item.item.equipment:
                    i_n = color_text(item.name.capitalize(), item.color)
                    message = 'Do you want to put %s on?' % i_n
                    w = len(message)+2
                    d_box = DialogBox(game, w, 10, width/4, height/2, message, type='option', con=inventory_window)
                    confirm = d_box.display_box()
                    if confirm == 1:
                        item.item.use(game.player.fighter.inventory, game.player, game)
                        d_box.destroy_box()
                        inventory_items = [color_text(item.name.capitalize(), item.color) for item in player.fighter.inventory]
            else:
                current_selection = None
        # game.gEngine.console_set_default_background(inventory_window, 0, 0, 0)
        # Wielded
        if mouse.cx >= 0 and mouse.cx <= width/2:  # inventory screen dims
            if (mouse.cy-2) < len(player.fighter.wielded):
                item = player.fighter.wielded[mouse.cy-2]
                if item is not None:
                    if item.item.equipment:
                        game.gEngine.console_print(compare_window, 1, 2, 'Name:     ' + color_text(item.name.capitalize(), item.color))
                        game.gEngine.console_print(compare_window, 1, 3, 'Type:     ' + item.item.equipment.type.capitalize())
                        damage = '%dd%d+%d' % (item.item.equipment.damage.nb_dices, item.item.equipment.damage.nb_faces, item.item.equipment.damage.addsub )
                        game.gEngine.console_print(compare_window, 1, 4, 'Damage:   ' + damage)
                        game.gEngine.console_print(compare_window, 1, 5, 'Accuracy: ' + str(item.item.equipment.accuracy))
                        game.gEngine.console_print(compare_window, 1, 6, 'Value:    ' + str(item.item.value))

        # Equipment
            elif (mouse.cy-2)-equip_y < len(player.fighter.equipment):
                item = player.fighter.equipment[mouse.cy-2-equip_y]
                if item is not None:
                    if item.item.equipment:
                        game.gEngine.console_print(compare_window, 1, 2, 'Name:     ' + color_text(item.name.capitalize(), item.color))
                        game.gEngine.console_print(compare_window, 1, 3, 'Type:     ' + item.item.equipment.type.capitalize())
                        game.gEngine.console_print(compare_window, 1, 4, 'Armor:    ' + str(item.item.equipment.bonus))
                        game.gEngine.console_print(compare_window, 1, 5, 'Penalty:  ' + str(item.item.equipment.penalty))
                        game.gEngine.console_print(compare_window, 1, 6, 'Value:    ' + str(item.item.value))
            if mouse.lbutton_pressed and item is not None:
                i_n = color_text(item.name.capitalize(), item.color)
                message = 'Do you want to take %s off?' % i_n
                w = len(message)+2
                d_box = DialogBox(game, w, 10, width/4, height/2, message, type='option', con=inventory_window)
                confirm = d_box.display_box()
                if confirm == 1:
                    item.item.equipment.un_equip(game.player, item)
                    d_box.destroy_box()
                    inventory_items = [color_text(item.name.capitalize(), item.color) for item in player.fighter.inventory]
                    i = 0
                    for x in player.fighter.wielded:
                        if x == item:
                            player.fighter.wielded[i] = None
                        i += 1
                    i = 0
                    for x in player.fighter.equipment:
                        if x == item:
                            player.fighter.equipment[i] = None
                        i += 1

        # keyboard input
        # keeps similar feel to old inventory if using the keys
        index = key.c - ord('a')
        if key:
            if index >= 0 < len(inventory_items):
                return_item = player.fighter.inventory[index]
                break
            index = key.c - ord('1')
            '''if index >= 0 <= 1:
                return_item = player.fighter.wielded[index]
                break
            elif index >= 2 <= 10:
                return_item = player.fighter.equipment[index-2]
                break'''
        # ========================================================================
        # handle buttons
        # ========================================================================

        # ========================================================================
        # handle exit button
        # ========================================================================
        exit_input = exit_button.display()
        for i in exit_input:
            if i != -1:
                key.vk = libtcod.KEY_ESCAPE
                break
    # Remember to remove consoles in reverse order of creation to avoid OOB errors
    game.gEngine.console_remove_console(compare_window)
    game.gEngine.console_remove_console(wielded_window)
    game.gEngine.console_remove_console(equipment_window)
    game.gEngine.console_remove_console(inventory_window)

    return return_item


def options_menu(con, header, options, screen_width, screen_height, bg=None):

    key_sets = []
    current_set = ''
    for option in options:
        if option.set_name:
            key_sets.append(option)
        if option.key_set:
            current_set = option.key_set


def help_menu():
    pass


def character_menu(con, header, skill_list, screen_width, screen_height, game, is_name=False ):
    options = []
    if len(skill_list) == 0:
        options = ['No skills to display']
        length = len('No skills to display')
    else:
        length = 0
        for item in skill_list:
            skill = ''
            skill += item.get_name()
            skill += ' Level: ' + str(item.get_bonus())
            options.append(skill)
            l = len(skill)
            if l > length:
                length = l
    length += 2
    index = menu(con, header, options, length, screen_height, screen_width, bg=None, game=game)
    if index is None or len(skill_list) == 0:
        return None
    if not is_name:
        return skill_list[index]
    else:
        return index

##============================================================================
def town_menu(con, header, game, width, screen_height, screen_width):
##============================================================================
    options =  ['The Helm and Buckler',
        "Johan's Weaporium",
        "Fizzilip's Magiteria",
        'Quests',
        'Finished',]
    path = os.path.join(sys.path[0], 'content')
    path = path.replace('library.zip', '')
    backgrounds=[os.path.join(path, 'img', 'bg-arm.png'),
                os.path.join(path, 'img', 'bg-wep.png'),
                os.path.join(path, 'img', 'bg-magic.png'),]
    container=[]
    menus = []
    weapon,armor,consum,quest=[],[],[],[]
    
    for i in range(10):##Need to init objects and message in object creation
        item = game.build_objects.build_equipment(game,0,0,'melee')
        weapon.append(item)
        item = game.build_objects.build_equipment(game,0,0,'armor')
        armor.append(item)
    for i in range(5):
        consume = game.build_objects.build_potion(game,0,0)
        consum.append(consume)
        consume = game.build_objects.build_scroll(game,0,0)
        consum.append(consume)
        
    container.append(armor)    
    container.append(weapon)
    container.append(consum)
    container.append(quest)
    
    bg = os.path.join(path,'img','bg-town.png')
    t_menu = Menus(game,screen_height,screen_width,width,header,options,bg=bg) 
    
    while 1:
        t_menu.is_visible=True
        libtcod.mouse_get_status()
        index = t_menu.menu()    
        if index == len(options)-1 or index is None:
            t_menu.destroy_menu()
            break
            
        if index != (len(options)-1) and index is not None and index != -1:
            game.gEngine.console_clear(0)
            t_menu.is_visible = False
            if index < (len(backgrounds)):
                item=shop(con,options[index],game,width,
                    screen_height,screen_width,container[index],backgrounds[index]) 
            else:
                item=shop(con,options[index],game,width,
                    screen_height,screen_width,container[index]) 
            if item is not None:
                container[index].pop(item)
            t_menu.last_input = 0


##============================================================================
def shop(con, header, game, width, screen_height, screen_width, container, bg=None):
##============================================================================
    options=[]
    cl_options = []
    if bg:
        img = libtcod.image_load(bg)
        libtcod.image_blit_2x(img, 0, 0, 0)
        
    for obj in container:
        obj_text = obj.name
        ob_value = obj.item.value
        opt = '[%s] - Price: (%s) gold'%(obj_text,ob_value)
        cl_options.append(opt)
        
        obj_text = color_text(obj.name,obj.color)
        ob_value = color_text(str(obj.item.value),libtcod.gold)
        opt = '[%s] - Price: (%s) gold'%(obj_text,ob_value)
        options.append(opt)
        
    header = header + ' (' + str(game.player.fighter.money) + ' gold left)'
    shop = Menus(game,screen_height,screen_width,width,header,options,bg=bg,cl_options=cl_options) 
    shop.is_visible=True
    
    while 1:
        shop.is_visible=True
        libtcod.mouse_get_status()#to prevent extra mouse clicks
        item = shop.menu()
        if item is not None and item is not -1:
            if game.player.fighter.money >= container[item].item.value:
                obj_text = color_text(container[item].name,container[item].color)
                ob_value = color_text(str(container[item].item.value),libtcod.gold)
                message = 'Purchase [%s] for (%s) gold?'%(obj_text,ob_value)
                w = len('Purchase ['+container[item].name+'] for ('+str(container[item].item.value)+') gold?')+2
                d_box = DialogBox(game,w,10,20,20,message,type='option',con=shop.window)
                shop.is_visible = False
                confirm = d_box.display_box()
                if confirm == 1:
                    game.logger.log.debug(container[item].objects)
                    game.player.fighter.money-=container[item].item.value
                    game.player.fighter.inventory.append(container[item])
                    d_box.destroy_box()
                    shop.destroy_menu()
                    #game.logger.log.debug(container[item])
                    return item
                else:
                    d_box.destroy_box()
            else:
                message = 'Not enough gold!'                
                d_box = DialogBox(game,len(message)+2,10,20,20,message,con=shop.window)
                confirm = d_box.display_box()
                d_box.destroy_box()
        if item is None:
            shop.destroy_menu()
            return None


##============================================================================
def confirm_screen(con,message,screen_height,screen_width,
        confirm_key_message='Press [y] or [Enter] to confirm.',confirm_keys=[ord('y'),libtcod.KEY_ENTER],height=4,game=None):
##============================================================================
    if len(message) > len(confirm_key_message):width = len(message)+2
    else:width = len(confirm_key_message)+2
    height = height
    window = game.gEngine.console_new(width,height)
    
    r,g,b = libtcod.white
    game.gEngine.console_set_default_foreground(window,r,g,b)    
    game.gEngine.console_print_frame(window,0, 0, width, height,True)
    game.gEngine.console_set_alignment(window,libtcod.CENTER)
    game.gEngine.console_print(window, width/2, 1,message)
    
    
    game.gEngine.console_print(window, width/2, height-1,confirm_key_message)
    
    x = screen_width/2 - width/2
    y = screen_height/2 - height/4
    game.gEngine.console_blit(window, 0, 0, width, height, 0, x, y, 1.0, 1.0)
    game.gEngine.console_flush()
    
    key = libtcod.console_wait_for_keypress(True)
    if key.c in confirm_keys or key.vk in confirm_keys:
        game.gEngine.console_remove_console(window)
        return True
    else:
        game.gEngine.console_remove_console(window)
        return False
    
    
    
    
    
    
    
    
    