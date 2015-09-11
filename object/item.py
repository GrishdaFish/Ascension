import libtcodpy as libtcod
import sys,os
sys.path.append(os.path.join(sys.path[0],'utils'))
import utils.menu as menu



class Item:
    #an item that can be picked up and used.
    def __init__(self, spell=None, equipment=None):
        self.owner = None
        self.value=0
        self.spell = spell
        self.stackable = False
        self.qty = 1
        if self.spell:
            self.use_function = self.spell.cast
            self.stackable = True
        self.equipment = equipment
        if self.equipment:
            self.use_function = self.equipment.equip

    def pick_up(self,inventory):
        #add to the player's inventory and remove from the map
        self.owner.x = None
        self.owner.y = None
        if not self.owner.misc:
            for item in inventory:
                if item.item:
                    if item.item.check_stackable() and item.name == self.owner.name:
                        item.item.stack(self.qty)
                        if self.owner.objects:
                            if self.owner in self.owner.objects:
                                self.owner.objects.remove(self.owner)
                        if self.owner.message:
                            msg = menu.color_text('You picked up a ', libtcod.yellow)
                            msg+= menu.color_text(self.owner.name, self.owner.color)
                            msg+= menu.color_text('!', libtcod.yellow)
                            self.owner.message.message(msg, 0)
                        return

            if len(inventory) >= 26:
                if self.owner.message:
                    msg = menu.color_text('Your inventory is full, cannot pick up ',libtcod.yellow)
                    msg+= menu.color_text(self.owner.name,self.owner.color)
                    msg+= menu.color_text('.',libtcod.yellow)
                    self.owner.message.message(msg,0)
            else:
                inventory.append(self.owner)
                if self.owner.objects:
                    if self.owner in self.owner.objects:
                        self.owner.objects.remove(self.owner)
                if self.owner.message:
                    msg = menu.color_text('You picked up a ',libtcod.yellow)
                    msg+= menu.color_text(self.owner.name,self.owner.color)
                    msg+= menu.color_text('!',libtcod.yellow)
                    self.owner.message.message(msg,0)

    def check_stackable(self):
        return self.stackable

    def stack(self, qty):
        self.qty += qty

    def drop(self,inventory, owner, mes=True):
        #add to the map and remove from the owners inventory. 
        #also, place it at the owners coordinates
        self.owner.objects.append(self.owner)
        inventory.remove(self.owner)
        self.owner.x = owner.x
        self.owner.y = owner.y
        #only display a message if the player dropped it, or if its special
        if mes:
            msg = menu.color_text('%s dropped a '%owner.name.capitalize(),libtcod.yellow)
            msg+= menu.color_text(self.owner.name,self.owner.color)
            msg+= menu.color_text('.',libtcod.yellow)
            self.owner.message.message(msg,0)

    def use(self,inventory,creature,game,player=True):
        #just call the "use_function" if it is defined
        if player == True:
            if self.use_function is None:
                self.owner.message.message('The ' + self.owner.name + ' cannot be used.')
            else:
                if not self.equipment:
                    if self.use_function(creature,game.player,game=game) != 'cancelled':
                        if self.check_stackable():
                            if self.qty > 1:
                                self.qty -= 1
                            else:
                                inventory.remove(self.owner)  #destroy after use, unless it was cancelled for some reason
                        else:
                            inventory.remove(self.owner)
                else:##equip
                    self.use_function(creature,game=game,owner=self.owner)
        else:##so mobs can use items
            self.use_function(creature,game=game)


class Equipment:
    def __init__(self,min_power=0, max_power=0, crit_bonus=0, defense=0,
                    type='',location='',best_defense_type='',worst_defense_type='',
                    handed=0,dual_wield=None,damage_type='',threat_level=0,
                    allowed_materials=0, bonus=0, penalty=0, description='', accuracy=0, damage=None):
        self.min_power=min_power
        self.max_power=max_power
        self.crit_bonus=crit_bonus
        self.defense=defense
        self.type=type
        self.location=location
        self.best_defense_type=best_defense_type
        self.worst_defense_type=worst_defense_type
        self.handed=handed
        self.dual_wield=dual_wield
        self.damage_type=damage_type
        self.threat_level=threat_level
        self.allowed_materials = allowed_materials
        self.bonus = bonus
        self.penalty = penalty
        self.description = description
        self.accuracy = accuracy
        self.damage = damage
        
    def calc_damage(self):
        total_damage = 0
        if self.damage is not None:
            num_dice = self.damage.nb_dices
            sides = self.damage.nb_faces
            multiplier = self.damage.multiplier
            bonus = self.damage.addsub
            for i in range(num_dice):
                total_damage += libtcod.random_get_int(0, 1, sides)
            total_damage = (total_damage * multiplier) + bonus
        return total_damage
    
    def equip(self, target, game=None, owner=None, slot=0):
        locations = {
                    'torso':    0,
                    'head':     1,
                    'hands':    2,
                    'legs':     3,
                    'feet':     4,
                    'arms':     5,
                    'shoulders': 6,
                    'back':     7
        }
        
        if self.type == 'armor':
            if target.fighter.equipment[locations[self.location]] is None:
                target.fighter.equipment[locations[self.location]] = owner
                if game:
                    game.message.message(owner.name+" equipped.",1)                    
                    target.fighter.inventory.remove(owner)
                #target.fighter.defense+=self.defense
                target.fighter.set_armor_bonus()
                target.fighter.set_armor_penalty()
                return
            else:
                remove = target.fighter.equipment[locations[self.location]]
                self.un_equip(target,remove)
                target.fighter.equipment[locations[self.location]] = owner
                #target.fighter.defense-=remove.item.equipment.defense
                #target.fighter.defense+=self.defense
                target.fighter.set_armor_bonus()
                target.fighter.set_armor_penalty()
                if game:
                    game.message.message(owner.name+" equipped.",1)
                    target.fighter.inventory.remove(owner)

                return
                
        if self.type == 'melee':
            if self.handed==1:
                if target.fighter.wielded[1]is not None:
                    if target.fighter.wielded[1].item.equipment.handed == 2:
                        target.fighter.wielded[1] = None
                if not self.dual_wield:
                    if target.fighter.wielded[0]:
                        self.un_equip(target,target.fighter.wielded[0])
                        self.put_on(target,0,owner,game)
                        if target.fighter.wielded[1]:
                            self.un_equip(target,target.fighter.wielded[1])
                            return
                    else:
                        self.put_on(target,0,owner,game)
                        return
                        
                ##Non dual wielding 1 handed weapons   
                else:
                    if target.fighter.wielded[0]: # something in hand 1
                        self.un_equip(target,target.fighter.wielded[0])
                        self.put_on(target,0,owner,game)
                    else:
                        self.put_on(target,0,owner,game)
                    #something in hand 2
                    if target.fighter.wielded[1]:
                        if target.fighter.wielded[1].item.equipment.type!='armor':
                            self.put_on(target,1,owner,game)
                    return
    
            if self.handed == 2:
                if target.fighter.wielded[0]:
                    self.un_equip(target, target.fighter.wielded[0])
                    self.put_on(target, 0, owner, game)
                    if target.fighter.wielded[1]:
                        self.un_equip(target, target.fighter.wielded[1])
                    target.fighter.wielded[1] = owner
                    #self.put_on(target, 1, owner, game)
                else:
                    self.put_on(target, 0, owner, game)
                    if target.fighter.wielded[1]:
                        self.un_equip(target, target.fighter.wielded[1])
                    target.fighter.wielded[1] = owner
                    #self.put_on(target, 1, owner, game)


    def put_on(self,target,slot,owner,game,type='wep'):
        if type == 'wep':
            target.fighter.wielded[slot] = owner
            target.fighter.inventory.remove(owner)
            if game:
                game.message.message(owner.name+" equipped.",1)
        
    def un_equip(self,target,item):
        target.fighter.inventory.append(item)