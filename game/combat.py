__author__ = 'Grishnak'
import sys
sys.path.append(sys.path[0])
import libtcodpy as libtcod
import logging

class Skill:
    def __init__(self, category, name, description):
        self.category = category
        self.name = name
        self.level = 0
        self.description = description

    def increase_level(self, skill_points):
        if skill_points >= self.level+1:
            if self.level == 5:
                return skill_points
            else:
                skill_points -= self.level +1
                self.level += 1
                return skill_points
        else:
            return skill_points

    def set_bonus(self, level):
            self.level = level

    def get_bonus(self):
        return self.level

    def get_name(self):
        return self.name

    def get_category(self):
        return self.category

    def get_description(self):
        return self.description

skill_list = [
    Skill('Discipline', 'One-Handed', 'Mastery of one handed weapons.'),
    Skill('Discipline', 'Two-Handed', 'Mastery of two handed weapon, or one handed weapon wielded in two hands.'),
    Skill('Discipline', 'Dual-Wield', 'Mastery of wielding two weapons at once.'),
    Skill('Discipline', 'Ranged',     'Mastery of ranged weapons.'),

    Skill('Discipline', 'Dodge',      'Ability to dodge incoming attacks.'),
    Skill('Discipline', 'Armor',      'Skill in reducing the penalties of wearing armor.'),
    Skill('Discipline', 'Shield',     'Proficiency at using shields.'),
    Skill('Discipline', 'Parry',      'Ability to deflect incoming attacks with weapons.'),

    Skill('Weapon', 'Knives', 'Mastery in the use of small, pointed weapons.'),
    Skill('Weapon', 'Straightsword', 'Mastery in the use of straight edged weapons.'),
    Skill('Weapon', 'Curvesword', 'Mastery in the use of swords with curved edges.'),
    Skill('Weapon', 'Axe', 'Mastery in the use of axes.'),
]
basic_levels = [  # Total xp: Skill Points
    (1000,   2),
    (3000,   2),
    (6000,   3),
    (10000,  3),
    (15000,  3),
    (21000,  4),
    (28000,  4),
    (36000,  4),
    (45000,  4),
    (55000,  5),
    (66000,  5),
    (78000,  5),
    (91000,  5),
    (105000, 5),
    (120000, 6),
    (136000, 6),
    (153000, 6),
    (171000, 6),
    (190000, 6),
    (210000, 6)
]


def hp_bonus(con):
    return 15 + (get_stat_bonus(con) * 2)


def next_level(level):
    return basic_levels[level]


def get_stat_bonus(stat):
    return (stat / 2) - 5


def get_armor_penalty(creature):
    return creature.fighter.get_armor_penalty()


def get_armor_class(creature):
    return creature.fighter.get_armor_bonus()


def get_blocking_class(creature):
    if creature.fighter.wielded[1] is not None:
        if creature.fighter.wielded[1].item.equipment.type == 'shield':
            roll = libtcod.random_get_int(0, 1, 20)
            roll += get_stat_bonus(creature.fighter.stats[0])
            roll += creature.fighter.get_skill('Shield').get_bonus()
            roll -= get_armor_penalty(creature)*2
            return roll
    return 0


def get_deflection_class(creature):
    hands = creature.fighter.wielded
    roll = 0
    if hands[1] is not None:
        if hands[1].item.equipment.type != 'melee':
            return roll
    if hands[0] is not None:
        if hands[0].item.equipment.type == 'melee':
            if hands[0] != hands[1]:  # make sure its not a 2-h weap
                roll = libtcod.random_get_int(0, 1, 20)
                roll += get_stat_bonus(creature.fighter.stats[1])
                roll += creature.fighter.get_skill('Parry').get_bonus()
                roll -= get_armor_penalty(creature)*2
                return roll
    return roll


def get_evasion_class(creature):
    roll = libtcod.random_get_int(0, 1, 20)
    roll += get_stat_bonus(creature.fighter.stats[2])
    roll += creature.fighter.get_skill('Dodge').get_bonus()
    roll -= get_armor_penalty(creature)*2
    return roll


def get_melee_bonus(creature):
    roll = 0
    for weapon in creature.fighter.wielded:
        if weapon is not None:
            roll += weapon.item.equipment.accuracy
            if weapon.item.equipment.handed == 2:
                break
    return roll

