__author__ = 'Grishnak'
import libtcodpy as libtcod
from button import *
from check_box import *
from color_text import *
from dialog_box import *
from inventory import *

def get_centered_text(text, width):
    head = text
    s = len(head)
    pos = width - s/2
    return head, pos

class HotBar():
    def __init__(self, x, y, gEngine, con=0):
        """
        Container class to hold and control all of the hot bar slots.
        :param x: x position of the container bar
        :param y: y position of the container bar
        :param gEngine: the main game engine object (for rendering)
        :return: Nothing
        """
        self.con=con
        self.x = x
        self.y = y
        self.gEngine = gEngine
        self.slots = []
        self.window = gEngine.console_new(32, 5)

    def add_slot(self, slot=None, obj=None):
        """
        Adds a slot to the container class
        :param slot: the slot to be added to the container
        :param obj: the object to attach to a slot
        """
        slot.owner = self
        self.slots.append(slot)

    def update(self, mouse, keyboard, game):
        """
        Handles keyboard and mouse input prior to rendering and calls slot.render()
        If activated, calls attached objects use function
        :param mouse: mouse input
        :param key: key input
        :return: Activated? (t/f)
        """
        self.gEngine.console_clear(self.window)
        r, g, b = libtcod.white
        self.gEngine.console_set_default_foreground(self.window, r, g, b)
        self.gEngine.console_print_frame(self.window, 0, 0, 32, 5, True)
        for slot in self.slots:
            slot.update(mouse, keyboard, game)
        self.render()

    def remove_slot_object(self, slot=None):
        """
        Removes slot object by slot number
        :param slot: The slot number to remove an object
        :return: Nothing
        """
        pass

    def add_slot_object(self, slot, object):
        """
        Add an object to a slot
        :param slot: The slot number to add object to
        :param object: The object to be added
        :return: Nothing
        """
        pass

    def render(self):
        """

        :return:
        """

        for slot in self.slots:
            slot.render()
            self.gEngine.console_blit(slot.window, 0, 0, 3, 3, self.window, slot.position, 1, 1.0, 1.0)
        self.gEngine.console_blit(self.window, 0, 0, 32, 5, self.con, self.x, self.y, 1.0, 1.0)


class HotBarSlot():
    def __init__(self, con, cx, cy, p, label, gEngine):
        """
        Slot that holds a skill or item that the player can quickly use
        :param con: destination console
        :param cx: x position relative to the main screen
        :param cy: y position relative to the main screen
        :param p: position on the bar its self
        :param label: The hotkey for the hotbar (1, 2, 3, etc..)
        :param gEngine: the game engine object (for rendering)
        :return: Nothing
        """
        self.position = p
        self.con = con
        self.cx = cx
        self.cy = cy
        self.name = 'Empty'
        self.label = label
        self.gEngine = gEngine
        self.window = gEngine.console_new(3, 3)
        self.obj = None
        self.owner = None

    def attach_object(self, obj):
        """
        Attaches an object (scrolls, potions, skills, weapons, wands, etc...) to this class
        :param obj: Object to attach
        :return: Success? (t/f)
        """
        self.obj = obj
        self.name = obj.name

    def remove_object(self):
        """
        Removes the attached object
        :return: Success? (t/f)
        """
        self.obj = None
        self.name = 'Empty'

    def use(self, game):
        if self.obj:
            if self.obj.item.spell:
                if self.obj.item.qty <= 1:
                    for slot in self.owner.slots:  # make sure any of the other slots that use this item are also removed
                        if slot.obj == self.obj and slot != self:
                            slot.remove_object()
                    self.obj.item.use(game.player.fighter.inventory, game.player, game)
                    self.remove_object()
                else:
                    self.obj.item.use(game.player.fighter.inventory, game.player, game)
            elif self.obj.equipment:
                pass
            return 'turn-used'
        else:
            chosen_item = inventory(self.con, game.player, self)
            if chosen_item:
                self.attach_object(chosen_item)

    def update(self, mouse, key, game):
        """
        Handles keyboard and mouse input prior to rendering and calls self.render()
        If activated, calls attached objects use function
        :param mouse: mouse input
        :param key: key input
        :return: Activated? (t/f)
        """
        self.gEngine.console_clear(self.window)
        r, g, b = libtcod.white
        if mouse.cx >= self.cx and mouse.cx <= self.cx + 2:
            if mouse.cy >= self.cy and mouse.cy <= self.cy + 2:
                r, g, b = libtcod.green
                t = self.name.capitalize()
                t = chr(libtcod.CHAR_TEEW) + t
                if self.obj:
                    if self.obj.item:
                        t += ' (%d)' % self.obj.item.qty + chr(libtcod.CHAR_TEEE)
                    else:
                        t += chr(libtcod.CHAR_TEEE)
                else:
                    t += chr(libtcod.CHAR_TEEE)
                t, p = get_centered_text(t, 16)
                self.gEngine.console_print(self.owner.window, p, 0, t)
                if mouse.lbutton:
                    r, g, b = libtcod.red
                if mouse.lbutton_pressed:
                    self.use(game)



        self.gEngine.console_set_default_foreground(self.window, r, g, b)
        self.gEngine.console_print_frame(self.window, 0, 0, 3, 3, True)
        self.gEngine.console_print(self.window, 0, 0, self.label)

        if self.obj:
            c = color_text(self.obj.char, self.obj.color)
            self.gEngine.console_print(self.window, 1, 1, c)
        else:
            c = color_text('X', libtcod.red)
            self.gEngine.console_print(self.window, 1, 1, c)

    def render(self, hovered=False, pressed=False):
        """
        Renders the Object
        :param hovered: is the mouse hovering or not being pressed?
        :param pressed: is the mouse pressing on the button?
        :return: None
        """
        pass