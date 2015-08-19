import sys,os
sys.path.append(sys.path[0])
import libtcodpy as libtcod
sys.path.append(os.path.join(sys.path[0],'object'))

import cEngine as gEngine

SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50
LIMIT_FPS = 60 

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
        return '%c%c%c%c%s%c'%(libtcod.COLCTRL_BACK_RGB,rb,gb,bb,
            txt,libtcod.COLCTRL_STOP)
    if color_f and not color_b:
        return '%c%c%c%c%s%c'%(libtcod.COLCTRL_FORE_RGB,rf,gf,bf,
            txt,libtcod.COLCTRL_STOP)
    if color_f and color_b:
        return "%c%c%c%c%c%c%c%c%s%c"%(libtcod.COLCTRL_FORE_RGB,rf,gf,bf,
            libtcod.COLCTRL_BACK_RGB,rb,gb,bb,txt,libtcod.COLCTRL_STOP)
            
class Menus:
##============================================================================
    def __init__(self,game,screen_height,screen_width,width,header,options,
        con=None,bg=None):
##============================================================================
        self.is_dragging = False
        self.in_drag_zone = False
        self.mouse_highlight = False
        self.game = game
        
        self.img = None
        if bg:
            self.img = game.gEngine.image_load(bg)
            
        self.screen_height = screen_height
        self.screen_width = screen_width
        
        self.header = header
        if len(self.header) == 0:
            self.header = '======='
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
                return 'close'
                
        ##For Menu Options        
        letter_index = ord('a')
        if mouse.cx >= self.w_pos and mouse.cx <= self.w_pos+self.width and not self.is_dragging:
            for i in range(len(self.options)):
                if my == i+1:
                    t = '(' + chr(letter_index+i) + ') ' + self.options[i].capitalize()
                    text = color_text(t,color_f=libtcod.red)
                    self.game.gEngine.console_print(self.window, self.width/2, i+1, text)
                    self.mouse_highlight = True
                    mouse_choice = i
                    break
                else:
                    self.mouse_highlight = False
                    
        ##bug here, after selecting a choice, the next menu gets "clicked" as well.
        if mouse.lbutton_pressed and self.mouse_highlight and not self.is_dragging:
            if not mouse.lbutton:
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
            return 'close'
            
        if key:
            if index >= 0 and index < len(self.options):
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
    def __init__(self,parent,label,x_pos,y_pos):
##============================================================================
        self.width = 4 + len(label)
        self.height = 5
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.parent = parent
        self.window = parent.game.gEngine.console_new(self.width,self.height)
        self.label = label
        self.label_o = label
        r,g,b = libtcod.white
        self.parent.game.gEngine.console_set_default_foreground(self.window, r,g,b)
        self.parent.game.gEngine.console_set_alignment(self.window,2)

##============================================================================
    def display(self):
##============================================================================
        self.parent.game.gEngine.console_blit(self.window, 0, 0,self.width,
            self.height,self.parent.window,self.x_pos,self.y_pos,1.0, 1.0)

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
        mx = mouse.cx -(self.x_pos + self.parent.x_pos)
        my = mouse.cy -(self.y_pos + self.parent.y_pos)
        
        if mx >= 0 and mx <= self.width and my >= 0 and my <= self.height:
            self.label = color_text(self.label_o,libtcod.red)
            if mouse.lbutton:
                self.label = color_text(self.label_o,libtcod.green)
                if mouse.lbutton_pressed:
                    return 1
            if mouse.lbutton_pressed:
                return 1
                '''else:
                    self.label = color_text(self.label_o,libtcod.white)
            else:
                self.label = color_text(self.label_o,libtcod.white)'''
        else:
            self.label = color_text(self.label_o,libtcod.white)
            
        return -1
    
    def key_input(self):
        key = libtcod.console_check_for_keypress()  
        
        if key.vk == libtcod.KEY_ENTER or key.vk == libtcod.KEY_SPACE:
            return 1
        #if key.vk == libtcod.KEY_ESCAPE:
        #    return None
        return -1
        
class DialogBox:
##============================================================================
    def __init__(self,game,width,height,x_pos,y_pos,body_text,type='dialog',
        option_labels=None):
##============================================================================
        self.game = game
        self.width = width
        if self.width < len(body_text):
            self.width = len(body_text)+2
            print len(body_text)
        self.height = height
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.buttons = []
        self.body_text = body_text
        self.window = game.gEngine.console_new(self.width,self.height)
        self.body_height = game.gEngine.console_get_height_rect(self.window, 1, 1, 
            self.width, self.height, body_text)
        #self.game.gEngine.console_set_alignment(self.window,2)
        
        if self.body_height > self.height-2:            
            self.game.gEngine.console_remove_console(self.window)
            self.height = self.body_height+2           
            self.window = game.gEngine.console_new(self.width,self.height)
            
        #self.game.gEngine.console_print_rect(self.window, 1, 1, self.width, 
        #   self.height, self.body_text)
        if type == None or type == 'dialog':
            self.run = self.dialog_box
            self.option_labels = option_labels
            if option_labels == None:
                self.option_labels = ['Ok']
            self.buttons.append(Button(self,self.option_labels[0],
                self.width//2-5,self.height/2-1))
            
        elif type == 'option':
            self.run = self.option_box
            self.option_labels = option_labels
            if option_labels == None:
                self.option_labels = ['Yes','No']
            self.buttons.append(Button(self,self.option_labels[0],
                self.width//6-5,self.height/2-1))
            self.buttons.append(Button(self,self.option_labels[1],
                self.width//3-5,self.height/2-1))

##============================================================================
    def display_box(self):
##============================================================================
        input = -1
        while input == -1:
            input = self.run()
        return input

##============================================================================
    def dialog_box(self):
##============================================================================
        input = [-1,-1]
        
        self.game.gEngine.console_blit(self.window, 0, 0,self.width,
            self.height,0,self.x_pos,self.y_pos,1.0, 1.0)        
            
        self.game.gEngine.console_print_frame(self.window,0, 0, 
            self.width, self.height, False)
        
        self.game.gEngine.console_print(self.window, 1, 
            1, self.body_text)
            
        input = self.buttons[0].display()
        self.game.gEngine.console_flush()
        
        for i in input:
            if i != -1:
                return 1
        return -1
        
##============================================================================
    def option_box(self):
##============================================================================
        input = [-1,-1]
        
        self.game.gEngine.console_blit(self.window, 0, 0,self.width,
            self.height,0,self.x_pos,self.y_pos,1.0, 1.0)        
            
        self.game.gEngine.console_print_frame(self.window,0, 0, 
            self.width, self.height, False)
        
        self.game.gEngine.console_print(self.window, 1, 
            1, self.body_text)
            
        input = self.buttons[0].display()
        self.game.gEngine.console_flush()        
        for i in input:
            if i != -1:
                return 1
        
        input = self.buttons[1].display()
     
        for i in input:
            if i != -1:
                return 0
                
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
##============================================================================
        key = libtcod.console_check_for_keypress()  
        
if __name__ == "__main__":
    class Game:
        def __init__(self):            
            self.gEngine = gEngine.gEngine(SCREEN_WIDTH,SCREEN_HEIGHT,
                'Ascension 0.0.1a',False,LIMIT_FPS)
                
    m_items =  ['Dialog Box', 
                'Option Box', 
                'Quit']
                
    game = Game()
    m_menu = Menus(game,SCREEN_HEIGHT/2+22,SCREEN_WIDTH,24,'Menu Testing',m_items)
    m_menu.is_visible = True
    
    while not libtcod.console_is_window_closed():
        game.gEngine.console_clear(0)
        choice = m_menu.menu()
        game.gEngine.console_flush()
        
        if choice == 0:
            x_pos = SCREEN_WIDTH/4
            y_pos = SCREEN_HEIGHT/4
            body_text = 'This is a testing dialog box with one button.'
            d_box = DialogBox(game,10,10,x_pos,y_pos,body_text)
            d_box.display_box()
            d_box.destroy_box()
            choice = -1
            
        if choice == 1:
            x_pos = SCREEN_WIDTH/4
            y_pos = SCREEN_HEIGHT/4
            body_text = 'This is a testing option box with two buttons.'
            d_box = DialogBox(game,10,10,x_pos,y_pos,body_text,type='option')
            d_box.display_box()
            d_box.destroy_box()
            choice = -1           
        
        if choice == 2 or choice == None:  #quit
            break
                