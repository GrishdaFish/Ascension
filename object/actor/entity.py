__author__ = 'Grishnak'
import sys
sys.path.append('..')
import component
import event


class Entity:
    def __init__(self, hp=0, x=0, y=0, name='', char='', color=None, s=10, i=10, c=10, d=10, w=10, cha=10, xp=0,
                 size="medium", speed=10):
        self.components = []
        self.x = x
        self.y = y
        self.hp = hp
        self.name = name
        self.char = char
        self.color = color
        self.strength = s
        self.intelligence = i
        self.constitution = c
        self.dexterity = d
        self.wisdom = w
        self.charisma = cha
        self.xp = xp
        self.speed = speed
        self.size = size

    def send_event(self, event):
        for component in self.components:
            component.receive_event(event)
            component.clear()  # clear components so that we dont get extra messages sent from comps down the chain

    def add_component(self, component):
        self.components.append(component)

    def convert(self, object):  # this is to convert this new style of creature to the old style objects
        # until I completely convert over everything, as to not break anything
        object.name = self.name
        object.x = self.x
        object.y = self.y
        object.color = self.color
        object.fighter.hp = self.hp
        object.fighter.max_hp = self.hp
        object.fighter.current_xp = self.xp
        s, i, c, d = self.strength, self.intelligence, self.constitution, self.dexterity
        object.fighter.stats[0] = s
        object.fighter.stats[1] = d
        object.fighter.stats[2] = i
        object.fighter.stats[3] = c
        return object

if __name__ == "__main__":
    i = 1
    for x in range(52):
        i = i + x+20

    print i