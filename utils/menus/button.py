__author__ = 'Grishnak'
import libtcodpy as libtcod
from dialog_box import *
from check_box import *
from color_text import *


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
    def display(self, mouse=None):
##============================================================================
        self.parent.game.gEngine.console_blit(self.window, 0, 0,self.width,
            self.height,self.dest_window,self.x_pos,self.y_pos,1.0, 1.0)

        self.parent.game.gEngine.console_print_frame(self.window,0, 0,
            self.width, self.height, False)

        self.parent.game.gEngine.console_print(self.window, self.width/2,
            self.height/2, self.label)
        self.parent.game.gEngine.console_flush()
        m = self.mouse_input(mouse)
        k = self.key_input()
        return m,k

##============================================================================
    def destroy_button(self):
##============================================================================
        self.parent.game.gEngine.console_remove_console(self.window)

##============================================================================
    def mouse_input(self, mouse=None):
##============================================================================
        if not mouse:
            mouse = libtcod.mouse_get_status()
        mx = mouse.cx - (self.x_pos + self.dest_x)
        my = mouse.cy - (self.y_pos + self.dest_y)

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

