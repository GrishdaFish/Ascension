import libtcodpy as libtcod
from item import *
from object import *
from misc import *
from spells import *
import logging

class GameObjects:
##============================================================================
    def __init__(self,content):
##============================================================================
        self.monsters = content[0]
        self.equipment = content[1]
        self.consumables = content[2]
        self.materials = content[3]
        #Need to sort all of the different content
        #for the object builders
        self.sort_threat_levels()
        self.sort_consumables()
        self.sort_materials()

##============================================================================
    def sort_materials(self):
##============================================================================
        self.armor_mats = []
        self.weapon_mats= []
        self.armor_mat_rarity = {}
        self.weapon_mat_rarity = {}
        log = logging.getLogger('main')
        for item in self.materials:
            log.debug(item.name)
            if item.can_be_made_from == 1 or item.can_be_made_from == 3:
                log.debug('%s added to weapons' % item.name)
                self.weapon_mats.append(item)
                '''if item.rarity >= 1.0:
                    self.weapon_mat_rarity.setdefault(1.0, []).append(item.name)
                elif item.rarity > 0.75 and item.rarity < 1.0:
                    pass
                elif item.rarity > 0.5 and item.rarity < 0.75:
                    pass '''
            if item.can_be_made_from == 2 or item.can_be_made_from == 3:
                log.debug('%s added to armor' % item.name)
                self.armor_mats.append(item)

##============================================================================
    def sort_consumables(self):
##============================================================================
        self.potions = []
        self.scrolls = []
        for item in self.consumables:
            if item.type == 'potion':
                self.potions.append(item)
            if item.type == 'scroll':
                self.scrolls.append(item)

##============================================================================
    def sort_threat_levels(self):
##============================================================================
        self.threat_list = []
        lvl1=[]
        lvl2=[]
        lvl3=[]
        lvl4=[]
        for object in self.monsters:
            if object.threat_level <= 1.0:lvl1.append(object.name)
            if object.threat_level > 1.0 and object.threat_level <= 2.0:lvl2.append(object.name)
            if object.threat_level > 2.0 and object.threat_level <= 3.0:lvl3.append(object.name)
            if object.threat_level > 3.0 and object.threat_level <= 4.0:lvl4.append(object.name)
        self.threat_list.append(lvl1)
        self.threat_list.append(lvl2)
        self.threat_list.append(lvl3)
        self.threat_list.append(lvl4)

##============================================================================
    def build_potion(self,game,x,y,name=None):
##============================================================================
        if name:
            pot = self.get_pot_from_name(name)
        if not name:
            pot = self.potions[libtcod.random_get_int(0,0,(len(self.potions)-1))]
            
        spell_component = Spell(min=pot.min_effect,max=pot.max_effect,range=pot.range,
            radius=pot.radius,ef_type=pot.effect_type,ad_eff=pot.additional_effects,
            spel_eff=pot.spell_effect,eff_col=pot.effect_color)
        item_component = Item(spell=spell_component)
        item_component.value = int(pot.value)
        name = "potion of %s"%pot.name
        item = Object(game.con,x, y, pot.cell, name, pot.color, item=item_component)
        return item

##============================================================================
    def build_scroll(self,game,x,y,name=None):
##============================================================================
        if name:
            scroll = self.get_scroll_from_name(name)
        if not name:
            scroll = self.scrolls[libtcod.random_get_int(0,0,(len(self.scrolls)-1))]
            
        spell_component = Spell(min=scroll.min_effect,max=scroll.max_effect,range=scroll.range,
            radius=scroll.radius,ef_type=scroll.effect_type,ad_eff=scroll.additional_effects,
            spel_eff=scroll.spell_effect,eff_col=scroll.effect_color)
        item_component = Item(spell=spell_component)
        item_component.value = int(scroll.value)
        name = "scroll of %s"%scroll.name
        item = Object(game.con,x, y, scroll.cell, name, scroll.color, item=item_component)
        return item

##============================================================================
    def get_pot_from_name(self,name):
##============================================================================
        for pot in self.potions:
            if pot.name == name:
                return pot
        return None

##============================================================================
    def get_scroll_from_name(self,name):
##============================================================================
        for scroll in self.scrolls:
            if scroll.name == name:
                return scroll
        return None

##============================================================================
    def get_mat_from_name(self,name):
##============================================================================
        for mat in self.armor_mats:
            if mat.name == name:
                return mat
        for mat in self.weapon_mats:
            if mat.name == name:
                return mat
        return None

##============================================================================
    def get_mat_from_rarity(self,type):
##============================================================================
        r = libtcod.random_get_float(0, 0.00000, 1.00000)
        mat = None
        rarity = 1.0
        if type == 'melee':
            for mats in self.weapon_mats:
                if mats.rarity >= r:
                    if mats.rarity <= rarity:
                        rarity = mats.rarity
                        mat = mats
            return mat
        if type == 'armor':
            for mats in self.armor_mats:
                if mats.rarity >= r:
                    if mats.rarity <= rarity:
                        rarity = mats.rarity
                        mat = mats
            return mat
            
##============================================================================
    def get_equip_from_name(self,name):
##============================================================================
        for equip in self.equipment:
            if equip.name == name:
                return equip
        return None
        
##============================================================================
    def build_equipment(self, game, x, y, type=None, name=None, mat=None):
##============================================================================
        #for getting base equipments, no special effects or unique/legendary
        
        #if mat or name return None, random mats or equipments are used
        if mat:
            mat = self.get_mat_from_name(mat)
        eq = None
        if name:
            eq = self.get_equip_from_name(name)
            if eq:
                type = eq.type
            
        if not type:
            r = libtcod.random_get_int(0, 0, (len(self.equipment)-1))
            eq = self.equipment[r]
            type = eq.type
    
        if type == 'melee':
            if not name:
                picked = False
                while not picked:
                    r = libtcod.random_get_int(0, 0, (len(self.equipment)-1))
                    if self.equipment[r].type == 'melee':
                        eq = self.equipment[r]
                        picked = True
            if not mat:
                mat = self.get_mat_from_rarity(type)
                #mat = self.weapon_mats[libtcod.random_get_int(0,0,(len(self.weapon_mats)-1))]

            #eq.min_power += mat.modifier
            #eq.max_power += mat.modifier
            eq.threat_level += mat.modifier
            equip_component = Equipment(type=eq.type, handed=eq.handed, dual_wield=eq.dual_wield,
                                        threat_level=eq.threat_level, accuracy=eq.accuracy, damage=eq.damage,
                                        damage_type=eq.damage_type)
            '''equip_component = Equipment(min_power=eq.min_power,max_power=eq.max_power,
                crit_bonus=eq.crit_bonus,type=eq.type,handed=eq.handed,
                dual_wield=eq.dual_wield,damage_type=eq.damage_type,threat_level=eq.threat_level, accuracy=eq.accuracy)
            '''
                    
        if type == 'armor':
            if not name:
                picked = False
                while not picked:
                    r = libtcod.random_get_int(0,0,(len(self.equipment)-1))
                    if self.equipment[r].type == 'armor':
                        eq = self.equipment[r]
                        
                        picked = True
            if not mat:
                mat = self.get_mat_from_rarity(type)
                #mat = self.armor_mats[libtcod.random_get_int(0,0,(len(self.armor_mats)-1))]
                
            eq.bonus+=mat.armor_bonus
            eq.penalty += mat.armor_bonus
            eq.threat_level+=mat.modifier
            
            equip_component = Equipment(defense=eq.defense,type=eq.type,location=eq.location,
                best_defense_type=eq.best_defense_type,worst_defense_type=eq.worst_defense_type,
                threat_level=eq.threat_level+mat.modifier)
        
        
        item_component = Item(equipment=equip_component)
        item_component.value = int(eq.value*mat.price_mod)
        name = mat.name+" "+eq.name
        equip = Object(game.con,x,y,eq.cell,name,mat.color,item=item_component)
        
        equip.message = game.message
        equip.objects = game.objects
        
        #equip.send_to_back(game.objects)
        return equip
        
##============================================================================
    def get_monster(self,name):
##============================================================================
        #returns a monster object with the same name supplied
        #if no monsters are found, returns None
        for object in self.monsters:
            if object.name == name:
                return object
        return None
        
##============================================================================
    def create_monster(self,game,x,y,threat_level=None,mob_name=None):
##============================================================================
        #creates monsters either randomly, by threat level, or by name
        #returns Object
        if not mob_name:
            mob = None
            while mob == None:
                if threat_level:
                    mob = self.get_monster(self.get_mob_from_threat(threat_level))
                else:
                    mob = self.monsters[libtcod.random_get_int(0,0,len(self.monsters)-1)]
        else:
            mob = self.get_monster(mob_name)
            if mob is None:##incase the name supplied is not in the monsters, get a random mob
                mob = self.monsters[libtcod.random_get_int(0,0,len(self.monsters)-1)]
        
                
        fighter_component = Fighter(hp=mob.hp, defense=mob.defense, power=mob.power, 
            death_function=monster_death,ticker=game.ticker,speed=mob.speed,
            Str=mob.strength,Dex=mob.dexterity,Int=mob.intelligence,xp_value=mob.xp_value)
        ai_component = WanderingMonster(x=x,y=y)#BasicMonster()
        
        monster = Object(game.con,x, y, mob.cell, mob.name, mob.color,
            blocks=True, fighter=fighter_component, ai=ai_component)
        monster.fighter.ticker.schedule_turn(monster.fighter.speed, monster)
        if mob.can_equip_gear:
            r = libtcod.random_get_int(0,0,100)
            if r < 50:
                monster.fighter.wielded[0] = self.build_equipment(game,x,y,type="melee")
        return monster    

##============================================================================
    def get_threat_from_mob(self,mob_name):
##============================================================================
        ##returns the threat level of a mob based on its name
        for obj in self.monsters:
            if obj.name == mob_name:
                return obj.threat_level
        return False

##============================================================================
    def get_mob_from_threat(self,threat_level=None):##basic setup
##============================================================================
        if threat_level is None:
            if libtcod.random_get_int(0,0,100) < 80: #80% chance of threat level less than 4
                if libtcod.random_get_int(0,0,100) < 30:#30% chance of getting lvl 3
                    tl = self.threat_list[2]
                    return tl[libtcod.random_get_int(0,0,(len(tl)-1))]
                if libtcod.random_get_int(0,0,100) < 50:#50% chance of getting lvl 2
                    tl = self.threat_list[1]
                    return tl[libtcod.random_get_int(0,0,(len(tl)-1))]
                if libtcod.random_get_int(0,0,100) < 80:#80% chance of getting lvl 1
                    tl = self.threat_list[0]
                    return tl[libtcod.random_get_int(0,0,(len(tl)-1))]
            else:
                tl = self.threat_list[3]
                return tl[libtcod.random_get_int(0,0,(len(tl)-1))]
        else:
            if threat_level-1 >= len(self.threat_list):
                threat_level = len(self.threat_list)
            if threat_level-1 < 0:
                threat_level = 0
            tl = self.threat_list[threat_level-1]
            return tl[libtcod.random_get_int(0,0,(len(tl)-1))]
