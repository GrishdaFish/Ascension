__author__ = 'Grishnak'
import libtcodpy as libtcod
import button


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

        if type is None or type == 'dialog':
            self.run = self.dialog_box
            self.option_labels = option_labels
            if option_labels is None:
                self.option_labels = ['Ok']
            self.buttons.append(button.Button(parent=self,label=self.option_labels[0],
                x_pos=self.width//2-5,y_pos=self.height/2-1,type=True))

        elif type == 'option':
            self.run = self.option_box
            self.option_labels = option_labels
            if option_labels is None:
                self.option_labels = ['Yes', 'No']
            self.buttons.append(button.Button(parent=self,label=self.option_labels[0],
                x_pos=1 ,y_pos=self.height/2-1,type=True))
            self.buttons.append(button.Button(parent=self,label=self.option_labels[1],
                x_pos=self.width-7,y_pos=self.height/2-1,type=False))
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

        self.game.gEngine.console_blit(self.window, 0, 0, self.width, self.height,
                                       self.con, self.x_pos, self.y_pos, 1.0, 1.0)

        self.game.gEngine.console_print_frame(self.window, 0, 0, self.width,
                                              self.height, False)

        self.game.gEngine.console_print(self.window, 1, 1, self.body_text)


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

