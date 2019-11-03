__author__ = 'Grishnak'
import component
import event


class Undead(component.Component):
    def __init__(self, owner):
        component.Component.__init__(self, owner)
        self.name = 'undead'
        self.hp_multiplier = 0.75
        self.s_mod = 0.75
        self.i_mod = 0.75
        self.c_mod = 0.75
        self.d_mod = 0.75
        self.xp_mod = 1.2
        self.base_type = 'undead'
        self.depth_mod = 1.0
        self.threat_mod = 1.5

    def process_event(self):
        for event in self.events:
            if event.get_id() == 'start-up':
                self.owner.name = self.name.capitalize() + ' ' + self.owner.name
                self.owner.hp = int(self.owner.hp * self.hp_multiplier)
                self.owner.strength = int(self.owner.strength * self.s_mod)
                self.owner.intelligence = int(self.owner.intelligence * self.i_mod)
                self.owner.constitution = int(self.owner.constitution * self.c_mod)
                self.owner.dexterity = int(self.owner.dexterity * self.d_mod)
                self.owner.xp = int(self.owner.xp * self.xp_mod)
            self.events.remove(event)


class Zombie(Undead):
    def __init__(self, owner):
        Undead.__init__(self, owner)
        self.name = 'zombie'
        self.hp_multiplier = 1.25
        self.s_mod = 1.25
        self.c_mod = 1.25


class Skeleton(Undead):
    def __init__(self, owner):
        Undead.__init__(self, owner)
        self.name = 'skeleton'
        self.hp_multiplier = 0.65
        self.s_mod = 0.6




