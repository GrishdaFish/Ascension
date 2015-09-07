__author__ = 'Grishnak'
import libtcodpy as libtcod


class HotBar():
    def __init__(self, x, y, gEngine):
        """
        Container class to hold and control all of the hot bar slots.
        :param x: x position of the container bar
        :param y: y position of the container bar
        :param gEngine: the main game engine object (for rendering)
        :return: Nothing
        """
        self.x = x
        self.y = y
        self.gEngine = gEngine
        self.slots = []
        self.window = gEngine.console_new(32, 5)

    def add_slot(self, slot):
        """
        Adds a slot to the container class
        :param slot: the slot to be added to the container
        """
        self.slots.append(slot)

    def update(self, mouse, keyboard):
        """
        Handles keyboard and mouse input prior to rendering and calls slot.render()
        If activated, calls attached objects use function
        :param mouse: mouse input
        :param key: key input
        :return: Activated? (t/f)
        """
        for slot in self.slots:
            slot.update(mouse, keyboard)
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
        self.gEngine.console_clear(self.window)
        r, g, b = libtcod.white
        self.gEngine.console_set_default_foreground(self.window, r, g, b)
        self.gEngine.console_print_frame(self.window, 0, 0, 32, 5, True)
        self.gEngine.console_blit(self.window, self.x, self.y, 32, 5, 0, 1.0, 1.0)
        for slot in self.slots:
            self.gEngine.console_blit(slot.window, slot.p, 1, 3, 3, self.window, 1.0, 1.0)


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
        self.name = ''
        self.label = label
        self.gEngine = gEngine
        self.window = gEngine.console_new(3, 3)
        self.obj = None

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
        self.name = ''

    def update(self, mouse, key):
        """
        Handles keyboard and mouse input prior to rendering and calls self.render()
        If activated, calls attached objects use function
        :param mouse: mouse input
        :param key: key input
        :return: Activated? (t/f)
        """
        self.render()

    def render(self, hovered=False, pressed=False):
        """
        Renders the Object
        :param hovered: is the mouse hovering or not being pressed?
        :param pressed: is the mouse pressing on the button?
        :return: None
        """
        self.gEngine.console_clear(self.window)
        r, g, b = libtcod.white
        self.gEngine.console_set_default_foreground(self.window, r, g, b)
        self.gEngine.console_print_frame(self.window, 0, 0, 3, 3, True)
        self.gEngine.console_print_char(self.window, 0, 0, self.label)

        #self.gEngine.console_blit(self.window, )