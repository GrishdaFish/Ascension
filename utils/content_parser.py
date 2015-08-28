import libtcodpy as libtcod
import logging

class ContentParser:
    def __init__(self, logger):
        self.parser = libtcod.parser_new()
        self.object_type = libtcod.parser_new_struct(self.parser, 'object_type')
        self.option_struct = libtcod.parser_new_struct(self.parser, 'option_struct')
        self.object_list = []
        self.logger = logger
        self.logger.log.info('Creating content parser.')

    def run(self, file):
        self.logger.log.info('Parsing %s ...' % file)
        libtcod.parser_run(self.parser, file, Listener(self.object_list, self.logger))
        return self.object_list


class Listener:
    def __init__(self, object_list, logger):
        self.object_list = object_list
        self.logger = logger
        self.object = None

    def new_struct(self, struct, name):
        self.struct_type = name
        if name == 'monster': self.object = Monster()
        if name == 'weapon': self.object = Weapon()
        if name == 'armor': self.object = Armor()
        if name == 'consumable': self.object = Consumable()
        if name == 'currency': self.object = Currency()
        if name == 'material': self.object = Material()
        if name == 'key_set': self.object = KeyControls()
        if name == 'game_options': self.object = GameOptions()
        if name == 'monster_weapon': self.object = MonsterWeapon()
        return True

    def new_flag(self, name):
        return True

    def new_property(self, name, typ, value):
        self.add_value(name, value)
        return True

    def end_struct(self, struct, name):
        self.object_list.append(self.object)
        return True

    def add_value(self, type, value):
        # msg = self.struct_type+' '+type
        # self.logger.log.debug(msg)
        if self.struct_type == 'monster': self.monster_parse(type, value)
        if self.struct_type == 'weapon': self.weapon_parse(type, value)
        if self.struct_type == 'armor': self.armor_parse(type, value)
        if self.struct_type == 'consumable': self.consum_parse(type, value)
        if self.struct_type == 'currency': self.currency_parse(type, value)
        if self.struct_type == 'material': self.material_parse(type, value)
        if self.struct_type == 'key_set': self.key_parse(type, value)
        if self.struct_type == 'game_options': self.option_parse(type, value)
        if self.struct_type == 'monster_weapon': self.monster_weapon(type, value)

    def weapon_parse(self, type, value):
        if type == 'name': self.object.name = value
        if type == 'cell': self.object.cell = value
        if type == 'min_power': self.object.min_power = value
        if type == 'max_power': self.object.max_power = value
        if type == 'type': self.object.type = value
        if type == 'handed': self.object.handed = value
        if type == 'dual_wield': self.object.dual_wield = value
        if type == 'crit_bonus': self.object.crit_bonus = value
        if type == 'base_value': self.object.value = value
        if type == 'damage_type': self.object.damage_type = value
        if type == 'threat_level': self.object.threat_level = value
        if type == 'size': self.object.size = value
        if type == 'damage':
            print value
            self.object.damage = value
        if type == 'accuracy': self.object.accuracy = value

    def armor_parse(self, type, value):
        if type == 'name': self.object.name = value
        if type == 'cell': self.object.cell = value
        if type == 'type': self.object.type = value
        if type == 'defense': self.object.defense = value
        if type == 'location': self.object.location = value
        if type == 'best_defense_type': self.object.best_defense_type = value
        if type == 'worst_defense_type': self.object.worst_defense_type = value
        if type == 'base_value': self.object.value = value
        if type == 'threat_level': self.object.threat_level = value
        if type == 'allowed_materials': self.object.allowed_materials = value
        if type == 'bonus': self.object.bonus = value
        if type == 'penalty': self.object.penalty = value
        if type == 'description': self.object.description = value

    def monster_parse(self, type, value):
        if type == 'name': self.object.name = value
        if type == 'cell': self.object.cell = value
        if type == 'hp': self.object.hp = value
        if type == 'defense': self.object.defense = value
        if type == 'power': self.object.power = value
        if type == 'type': self.object.type = value
        if type == 'threat_level': self.object.threat_level = value
        if type == 'starting_depth': self.object.starting_depth = value
        if type == 'deepest_depth': self.object.deepest_depth = value
        if type == 'speed': self.object.speed = value
        if type == 'strength': self.object.strength = value
        if type == 'dexterity': self.object.dexterity = value
        if type == 'intelligence': self.object.intelligence = value
        if type == 'xp_reward': self.object.xp_value = value
        if type == 'col': self.object.color = value
        if type == 'size': self.object.size = value
        if type == 'can_equip_gear': self.object.can_equip_gear = value

    def consum_parse(self, type, value):
        if type == 'name': self.object.name = value
        if type == 'cell': self.object.cell = value
        if type == 'type': self.object.type = value
        if type == 'min_effect': self.object.min_effect = value
        if type == 'max_effect': self.object.max_effect = value
        if type == 'effect_type': self.object.effect_type = value
        if type == 'additional_effects': self.object.additional_effects = value
        if type == 'spell_effects': self.object.spell_effects = value
        if type == 'effect_color': self.object.effect_color = value
        if type == 'range': self.object.range = value
        if type == 'radius': self.object.radius = value
        if type == 'max_targets': self.object.max_targets = value
        if type == 'col': self.object.color = value
        if type == 'value': self.object.value = value

    def currency_parse(self, type, value):
        if type == 'name': self.object.name = value
        if type == 'cell': self.object.cell = value
        if type == 'worth': self.object.worth = value
        if type == 'is_coin': self.object.is_coin = value
        if type == 'col': self.object.color = value

    def material_parse(self, type, value):
        if type == 'name': self.object.name = value
        if type == 'modifier': self.object.modifier = value
        if type == 'weight': self.object.weight = value
        if type == 'price_mod': self.object.price_mod = value
        if type == 'hardness': self.object.hardness = value
        if type == 'edge': self.object.edge = value
        if type == 'rarity': self.object.rarity = value
        if type == 'can_be_weapon': self.object.can_be_weapon = value
        if type == 'can_be_armor': self.object.can_be_armor = value
        if type == 'col': self.object.color = value
        if type == 'can_be_made_from': self.object.can_be_made_from = value
        if type == 'armor_bonus': self.object.armor_bonus = value
        if type == 'armor_penalty': self.object.armor_penalty = value
        if type == 'weight': self.object.weight = value
        if type == 'sharpness': self.object.sharpness = value
        if type == 'durability': self.object.durability = value

    def key_parse(self, type, value):
        if type == 'set_name': self.object.set_name = value
        if type == 'key_north': self.object.key_north = value
        if type == 'key_east': self.object.key_east = value
        if type == 'key_south': self.object.key_south = value
        if type == 'key_west': self.object.key_west = value
        if type == 'key_inventory': self.object.key_inventory = value
        if type == 'key_pickup': self.object.key_pickup = value
        if type == 'key_equip': self.object.key_equip = value
        if type == 'key_help': self.object.key_help = value
        if type == 'key_drop': self.object.key_drop = value
        if type == 'key_char': self.object.key_char = value

    def option_parse(self, type, value):
        if type == 'key_set': self.object.key_set = value

    def monster_weapon(self, type, value):
        if type == 'name': self.object.name = value
        if type == 'type': self.object.type = value
        if type == 'handed': self.object.handed = value
        if type == 'dual_wield': self.object.dual_wield = value
        if type == 'damage_type': self.object.damage_type = value
        if type == 'damage': self.object.damage = value
        if type == 'accuracy': self.object.accuracy = value

    def error(self, msg):
        self.logger.log.error(msg)
        print 'error : ', msg
        return True


class Consumable:
    def __init__(self):
        self.name = ""
        self.cell = ''
        self.type = ""
        self.min_effect = 0
        self.max_effect = 0
        self.effect_type = ""
        self.additional_effects = ""
        self.spell_effect = ""
        self.effect_color = None
        self.range = 0
        self.radius = 0
        self.max_targets = 0
        self.color = None
        self.value = 0


class Currency:
    def __init__(self):
        self.name = ""
        self.char = ''
        self.worth = 0
        self.is_coin = False
        self.color = None
        self.type = None


class Weapon:
    def __init__(self):
        self.name = ""
        self.cell = ''
        self.min_power = 0
        self.max_power = 0
        self.type = ""
        self.handed = 0
        self.dual_wield = False
        self.damage_type = ""
        self.color = None
        self.crit_bonus = 0.0
        self.value = 0
        self.threat_level = 0.0
        self.size = None
        self.damage = None
        self.accuracy = 0


class Armor:
    def __init__(self):
        self.name = ""
        self.cell = ''
        self.type = ""
        self.defense = 0
        self.location = ""
        self.best_defense_type = ""
        self.worst_defense_type = ""
        self.value = 0
        self.threat_level = 0.0
        self.description = ""
        self.allowed_materials = 0
        self.bonus = 0
        self.penalty = 0


class Monster:
    def __init__(self):
        self.name = ''
        self.cell = ''
        self.hp = 0
        self.defense = 0
        self.power = 0
        self.type = ''
        self.threat_level = 0.0
        self.starting_depth = 0
        self.deepest_depth = 0
        self.speed = 0
        self.strength = 0
        self.dexterity = 0
        self.intelligence = 0
        self.color = None
        self.xp_value = 0
        self.size = None
        self.can_equip_gear = False


class Material:
    def __init__(self):
        self.name = ""
        self.modifier = 0
        self.weight = 0
        self.price_mod = 0.0
        self.hardness = 0
        self.edge = 0
        self.rarity = 0.0
        self.can_be_weapon = None
        self.can_be_armor = None
        self.color = None
        self.armor_bonus = 0
        self.armor_penalty = 0
        self.weight = 0
        self.sharpness = 0
        self.durability = 0
        self.can_be_made_from = 0


class KeyControls:
    def __init__(self):
        self.set_name = ""
        self.key_north = None
        self.key_east = None
        self.key_south = None
        self.key_west = None
        self.key_inventory = None
        self.key_pickup = None
        self.key_equip = None
        self.key_help = None
        self.key_drop = None
        self.key_char = None


class MonsterWeapon:
    def __init__(self):
        self.name = ""
        self.type = ""
        self.handed = 0
        self.dual_wield = False
        self.damage = None
        self.accuracy = 0
        self.damage_type = ''


class GameOptions:
    def __init__(self):
        self.key_set = ""