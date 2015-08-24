import libtcodpy as libtcod
import sys,os
sys.path.append(os.path.join(sys.path[0],'utils'))
import menu



class Item:
    #an item that can be picked up and used.
    def __init__(self, spell=None,equipment=None):
        self.value=0
        self.spell = spell
        if self.spell:
            self.use_function = self.spell.cast
        self.equipment = equipment
        if self.equipment:
            self.use_function = self.equipment.equip

    def pick_up(self,inventory):
        #add to the player's inventory and remove from the map
        self.owner.x = None
        self.owner.y = None
        if not self.owner.misc:
            if len(inventory) >= 26:
                msg = menu.color_text('Your inventory is full, cannot pick up ',libtcod.yellow)
                msg+= menu.color_text(self.owner.name,self.owner.color)
                msg+= menu.color_text('.',libtcod.yellow)
                self.owner.message.message(msg,0)#'Your inventory is full, cannot pick up ' + self.owner.name + '.', 3)
            else:
                inventory.append(self.owner)
                self.owner.objects.remove(self.owner)
                msg = menu.color_text('You picked up a ',libtcod.yellow)
                msg+= menu.color_text(self.owner.name,self.owner.color)
                msg+= menu.color_text('!',libtcod.yellow)
                self.owner.message.message(msg,0)#'You picked up a ' + self.owner.name + '!',3)
     
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
            self.owner.message.message(msg,0)#owner.name.capitalize()+' dropped a ' + self.owner.name + '.',3)
 
    def use(self,inventory,creature,game,player=True):
        #just call the "use_function" if it is defined
        if player == True:
            if self.use_function is None:
                self.owner.message.message('The ' + self.owner.name + ' cannot be used.')
            else:
                if not self.equipment:
                    if self.use_function(creature,game.player,game=game) != 'cancelled':
                        inventory.remove(self.owner)  #destroy after use, unless it was cancelled for some reason
                else:##equip
                    self.use_function(creature,game=game,owner=self.owner)
        else:##so mobs can use items
            self.use_function(creature,game=game)


class Equipment:
    def __init__(self,min_power=None,max_power=None,crit_bonus=None,defense=None,
                    type=None,location=None,best_defense_type=None,worst_defense_type=None,
                    handed=None,dual_wield=None,damage_type=None,threat_level=None):
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
        
    def calc_damage(self,best_type=None,worst_type=None,damage_type=None,damage=None):
        ##get final damage/damage reduction,before player stats, crits, chance to hit
        if self.type == "melee":
            damage = libtcod.random_get_int(0,self.min_power,self.max_power)
            if self.damage_type == best_type:
                return damage // 2 #rounded down
            elif self.damage_type == worst_type:
                return damage*2
            else:
                return damage
    
    def equip(self,target,game=None,owner=None,slot=0):
        locations= {'torso':0,'head':1,'left_hand':2,'right_hand':3,
                    'legs':4,'right_foot':5,'left_foot':6,'left_arm':7,
                    'right_arm':8,'left_shoulder':9,'right_shoulder':10,'back':11,}
        
        if self.type == 'armor':
            if target.fighter.equipment[locations[self.location]] is None:
                target.fighter.equipment[locations[self.location]] = owner
                if game:
                    game.message.message(owner.name+" equipped.",1)                    
                    target.fighter.inventory.remove(owner)
                target.fighter.defense+=self.defense
                return
            else:
                remove = target.fighter.equipment[locations[self.location]]
                self.un_equip(target,remove)
                target.fighter.equipment[locations[self.location]] = owner
                target.fighter.defense-=remove.item.equipment.defense
                target.fighter.defense+=self.defense
                if game:
                    game.message.message(owner.name+" equipped.",1)
                    target.fighter.inventory.remove(owner)
                return
                
        if self.type == 'melee':
            if self.handed==1:
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
                    if target.fighter.wielded[0]:##something in hand 1
                        self.un_equip(target,target.fighter.wielded[0])
                        self.put_on(target,0,owner,game)
                    else:
                        self.put_on(target,0,owner,game)
                    #something in hand 2
                    if target.fighter.wielded[1]:
                        if target.fighter.wielded[1].item.equipment.type!='armor':
                            self.put_on(target,1,owner,game)
                    return
    
            if self.handed==2:
                if target.fighter.wielded[0]:
                    self.un_equip(target,target.fighter.wielded[0])
                    self.put_on(target,0,owner,game)                    
                    if target.fighter.wielded[1]:
                        self.un_equip(target,target.fighter.wielded[1])
                    return

    def put_on(self,target,slot,owner,game,type='wep'):
        if type == 'wep':
            target.fighter.wielded[slot] = owner
            target.fighter.inventory.remove(owner)
            if game:
                game.message.message(owner.name+" equipped.",1)
        
    def un_equip(self,target,item):
        target.fighter.inventory.append(item)