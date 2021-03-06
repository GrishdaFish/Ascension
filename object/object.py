import sys
import os
import math
import copy
import logging
sys.path.append(sys.path[0])
import libtcodpy as libtcod
sys.path.append(os.path.join(sys.path[0],'game'))
import game.combat as combat

##I might rewrite this system, the bigger the game gets, the more cumbersome this
##system gets. :(
class Object:
    '''this is a generic object: the player, a monster, an item, the stairs...
    it's always represented by a character on screen.'''
    def __init__(self,con=None,x=None,y=None,char=None,name=None,color=None,
        blocks=False,fighter=None,ai=None,item=None,misc=None,projectile=None):
        
        self.con = con
        self.x = x
        self.y = y
        self.char = char
        self.name = name
        self.color = color
        self.base_color = color
        self.flash_color = None
        self.blocks = blocks
        self.objects = None
        self.message = None
        self.type = None
        self.flashing = False
        self.flash_duration = 0
        self.fighter = fighter
        if self.fighter:
            self.fighter.owner = self
            
        self.ai = ai
        if self.ai:
            self.ai.owner = self
            self.ai.node = None
        self.item = item
        if self.item:
            self.item.owner = self
            
        self.misc = misc
        if self.misc:
            self.misc.owner = self
            
        self.projectile = projectile        
        if self.projectile:
            self.projectile.owner = self
            
    def move(self, dx, dy, map, objects):
        #move by the given amount, if the destination is not blocked
        if not self.is_blocked(self.x + dx, self.y + dy,map,objects):
            self.x += dx
            self.y += dy
 
    def move_towards(self, target_x, target_y,map,objects):
        #vector from this object to the target, and distance
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx ** 2 + dy ** 2)
 
        #normalize it to length 1 (preserving direction), then round it and
        #convert to integer so the movement is restricted to the map grid
        dx = int(round(dx / distance))
        dy = int(round(dy / distance))
        self.move(dx, dy,map,objects)
 
    def distance_to(self, other):
        #return the distance to another object
        if other:
            dx = other.x - self.x
            dy = other.y - self.y
            return math.sqrt(dx ** 2 + dy ** 2)
 
    def distance(self, x, y):
        #return the distance to some coordinates
        return math.sqrt((x - self.x) ** 2 + (y - self.y) ** 2)
 
    def send_to_back(self,objects=None):
        #make this object be drawn first, so all others appear above it if they're in the same tile.
        if objects == None:
            self.objects.remove(self)
            self.objects.insert(0,self)
        else:
            objects.remove(self)
            objects.insert(0, self)
 
    def draw(self, fov_map, gEngine, is_player=False, force_display=False):
        #only show if it's visible to the player
        if force_display:
            h,s,v = gEngine.console_get_char_background(self.con,self.x,self.y)
            #print gEngine.return_color_background(self.con,self.x,self.y)
            col = libtcod.Color(0,0,0)
            libtcod.color_set_hsv(col,h,s,v)
            fr,fg,fb = self.color
            br,bg,bb = col
            gEngine.console_put_char_ex(self.con,self.x,self.y,self.char,fr,fg,fb,br,bg,bb)#self.char,self.color,col)
        elif libtcod.map_is_in_fov(fov_map, self.x, self.y):
            #set the color and then draw the character that represents this object at its position
            h,s,v = gEngine.console_get_char_background(self.con,self.x,self.y)
            col = libtcod.Color(0,0,0)
            libtcod.color_set_hsv(col,h,s,v)
            fr,fg,fb = 0,0,0
            if self.flashing:
                if self.flash_duration == 1:
                    c2 = libtcod.Color(0,0,0)
                    libtcod.color_set_hsv(c2,0,0,255)
                    fr,rg,rb = c2
                    self.flash_duration = 0
                    self.flashing = False
            else:
                fr,fg,fb = self.color
                brightness = gEngine.light_mask.mask[self.x + self.y * gEngine.w]
                fr *= brightness[0]
                fg *= brightness[1]
                fb *= brightness[2]
            br,bg,bb = col
            if is_player:
                gEngine.console_put_char_ex(self.con,gEngine.w/2,gEngine.h/2-6,self.char,int(fr),int(fg),int(fb),br,bg,bb)
            else:
                gEngine.console_put_char_ex(self.con,self.x,self.y,self.char,int(fr),int(fg),int(fb),br,bg,bb)#self.char,self.color,col)
 
    def clear(self,gEngine):
        #erase the character that represents this object
        gEngine.console_set_char(self.con, self.x, self.y, ' ')
        
    def is_blocked(self,x, y,map,objects):
        #first test the map tile
        if map[x][y].blocked:
            return True
     
        #now check for any blocking objects
        for object in objects:
            if object.blocks and object.x == x and object.y == y:
                return True
     
        return False

    def short_flash(self):
        pass

    def long_flash(self):
        pass

    def blink(self):
        pass

class Fighter:
    #combat-related properties and methods (monster, player, NPC).
    def __init__(self, hp, defense, power, death_function=None, Con=10, Str=10, Dex=10, Int=10, money=0,ticker=None,speed=0,xp_value=0):
        self.death_function = death_function
        self.type = 'melee'
        self.money = money
        self.speed = speed
        self.level = 1
        self.current_xp = xp_value
        self.xp_to_next_level = 1000
        self.inventory = []
        self.owner = None
        self.ticker = ticker
        self.stats = [Str, Dex, Int, Con]
        self.unused_skill_points = 2
        self.defense = 0

        self.depth = 0
        self.threat = 0.0

        self.max_hp = combat.hp_bonus(Con)
        hp = self.max_hp
        self.hp = hp

        self.armor_bonus = 0
        self.armor_penalty = 0

        '''self.max_mp = 1 + (2*self.stats[2])
        mp = self.max_mp
        self.mp = mp'''

        self.equipment = [None, None, None, None, None, None, None, None]
        
        #accessories
        self.accessories = [None, None, None]
        
        #weapons/shield
        self.wielded = [None, None]
        self.skills = copy.deepcopy(combat.skill_list)  # skill list needs to have its own copies

    def level_up(self):
        self.xp_to_next_level, sp = combat.next_level(self.level)
        self.unused_skill_points += sp
        self.level += 1
        self.max_hp += combat.hp_bonus(self.stats[3])
        hp = self.max_hp
        self.hp = hp
        self.current_xp = 0

    def apply_skill_points(self, skill):
        if isinstance(skill, basestring):
            skill = self.get_skill(skill)
        self.unused_skill_points = skill.increase_level(self.unused_skill_points)

    def set_armor_bonus(self):
        bonus = 0
        for item in self.equipment:
            if item is not None:
                bonus += item.item.equipment.bonus
        self.armor_bonus = bonus

    def get_armor_bonus(self):
        return self.armor_bonus

    def get_armor_penalty(self):
        return self.armor_penalty

    def set_armor_penalty(self):
        penalty = 0
        for item in self.equipment:
            if item is not None:
                penalty += item.item.equipment.penalty
        penalty -= self.get_skill('Armor').get_bonus()
        self.armor_penalty = penalty

    def get_skill(self, name):
        for skill in self.skills:
            if skill.get_name() == name:
                return skill
        return None

    def attack(self, target, player=False, direction=None,game=None):
        if not player:
            col = 2
        else:
            col = 5

        attack_roll = libtcod.random_get_int(0, 1, 20)
        attack_roll += combat.get_melee_bonus(self.owner)

        evasion_roll = combat.get_evasion_class(target)
        deflection_roll = combat.get_deflection_class(target)
        blocking_roll = combat.get_blocking_class(target)

        #msg = "A: %d, E:%d" % (attack_roll, evasion_roll)
        #self.owner.message.message(msg)
        msg = ''
        if evasion_roll > attack_roll:
            msg = self.owner.name.capitalize() + ' attacks ' + target.name + ' but the attack was evaded!'
        elif deflection_roll > attack_roll:  # need to check for a weapon or something that can deflect
            msg = self.owner.name.capitalize() + ' attacks ' + target.name + ' but the attack was deflected!'
        elif blocking_roll > attack_roll:  # need to check for shield
            msg = self.owner.name.capitalize() + ' attacks ' + target.name + ' but the attack was blocked!'
        else:
            dmg = 0
            if self.wielded[0] is not None:
                skill = self.get_skill(self.wielded[0].item.equipment.damage_type)
                if skill is not None:
                    dmg = skill.get_bonus()
                if dmg is None:
                    dmg = 0
                dmg += self.wielded[0].item.equipment.calc_damage()
                dmg = int(dmg)
            else:
                #For empty slots
                pass
            if dmg > 0:
                if attack_roll < 10 + self.armor_bonus:
                    dmg *= 0.25
                    dmg = int(dmg)
                #make the target take some damage
                msg = self.owner.name.capitalize() + ' attacks ' + target.name + ' for ' + str(dmg) + '!'
                target.fighter.take_damage(dmg, self.owner)
            else:
                if libtcod.random_get_int(0, 0, 100) < 25:  # 25% chance to always do at least 1 damage
                    dmg = 1
                    target.fighter.take_damage(dmg, self.owner)
                    msg = self.owner.name.capitalize() + ' scratches ' + target.name + ' for ' + str(dmg) + '!'
                else:
                    msg = self.owner.name.capitalize() + ' attacks ' + target.name + ' but it has no effect!'

        self.owner.message.message(msg, col)
        #expand on this for different attack patterns, right now its a 1x3 area in front of the player
        if direction and player:
            t=None
            if direction == "north" or direction == 'south':
                t = game.check_for_target(target.x+1, target.y)
                if t:
                    game.player.fighter.attack(t,player=True)
                    t=None
                t = game.check_for_target(target.x-1, target.y)
                if t:
                    game.player.fighter.attack(t,player=True)
            elif direction == "east" or direction == 'west':
                t = game.check_for_target(target.x, target.y+1)
                if t:
                    game.player.fighter.attack(t,player=True)
                    t=None
                t = game.check_for_target(target.x-1, target.y-1)
                if t:
                    game.player.fighter.attack(t,player=True)


    def take_damage(self, damage, attacker):
        #apply damage if possible
        if damage > 0:
            self.hp -= damage
            self.owner.flashing = True
            self.owner.flash_duration =1
            #check for death. if there's a death function, call it
            if self.hp <= 0:
                attacker.fighter.current_xp += self.current_xp
                function = self.death_function
                if function is not None:
                    function(self.owner)
            else:
                pass #flash
    def heal(self, amount):
        #heal by the given amount, without going over the maximum
        self.hp += amount
        if self.hp > self.max_hp:
            self.hp = self.max_hp
            
#x,y offsets for co-ords next to the player
offsets = [(1, 0), (0, 1), (-1, 0), (0, -1),
           (1, 1), (-1, 1), (-1, -1), (1, -1)]


def get_next_to_player(mob, player, map):
    d = 100
    dx,dy = 0,0
    for i in range(len(offsets)):
        px,py = offsets[i]
        if mob.owner.distance(player.x+px, player.y+py) < d:
            if not mob.owner.is_blocked(player.x+px, player.y+py, map, mob.owner.objects):
                dx, dy = player.x+px,player.y+py
                d = mob.owner.distance(player.x+px, player.y+py)
    return dx, dy
class AI_Base:
    def __init__(self):
        self.node = None
        self.owner = None

    def remove_from_node(self):
        self.node.remove_from_group(self.owner)

    def add_node(self,node):
        self.node = node

class BasicMonster(AI_Base):
    #AI for a basic monster.
    def take_turn(self,game):
        #a basic monster takes its turn. if you can see it, it can see you
        self.owner.fighter.ticker.schedule_turn(self.owner.fighter.speed,self.owner)
        if libtcod.map_is_in_fov(game.fov_map, self.owner.x, self.owner.y): 
            #move towards player if far away
            if self.owner.distance_to(game.player) >= 2:
                #we need to get the closest distance from the monster, surrounding the player
                dx,dy = get_next_to_player(self,game.player,game.Map.map)
                #then move to it
                if libtcod.path_compute(game.path,self.owner.x,self.owner.y,dx,dy):
                    x,y = libtcod.path_walk(game.path,True)
                    self.owner.x = x
                    self.owner.y = y                    
            #close enough, attack! (if the player is still alive.)
            elif game.player.fighter.hp > 0:
                self.owner.fighter.attack(game.player)
        else:#start wandering
            self.owner.ai = WanderingMonster(x=self.owner.x,y=self.owner.y)
            self.owner.ai.owner = self.owner


class WanderingMonster(AI_Base):
    #Ai for a monster to randomly wander around when not in the view of the player
    def __init__(self,radius=3,x=0,y=0):
        self.radius = radius
        self.dest = False        
        self.home_x = x
        self.home_y = y
        AI_Base.__init__(self)

    def take_turn(self,game):
        self.owner.fighter.ticker.schedule_turn(self.owner.fighter.speed,self.owner)
        
        if self.dest and self.owner.distance(self.dest_x,self.dest_y) <= 0:
            self.dest = False
            
        if self.dest and self.owner.distance(self.dest_x,self.dest_y) > 0:
            self.owner.move_towards(self.dest_x,self.dest_y,game.Map.map,game.objects)
            
        if not self.dest:
            picked = False
            while not picked:
                min_x,max_x = self.home_x-self.radius,self.home_x+self.radius
                min_y,max_y = self.home_y-self.radius,self.home_y+self.radius    
            
                mx,my = game.Map.MAP_WIDTH,game.Map.MAP_HEIGHT
                
                #make sure min and max values are within the boundaries of the map
                if not min_x <=0 or not min_y <=0 or not max_x >= my or not max_y >= mx:
                    self.dest_x=libtcod.random_get_int(0,min_x+1,max_x-1)
                    self.dest_y=libtcod.random_get_int(0,min_y+1,max_y-1)
                
                    if not game.Map.map[self.dest_x][self.dest_y].blocked and not self.owner.distance(self.dest_x,self.dest_y) == 0:
                        picked = True
                        
            self.owner.move_towards(self.dest_x,self.dest_y,game.Map.map,game.objects)
            
        if libtcod.map_is_in_fov(game.fov_map, self.owner.x, self.owner.y):
            node = self.owner.ai.node
            self.owner.ai = BasicMonster()
            self.owner.ai.owner = self.owner
            self.owner.ai.node = node


class ConfusedMonster(AI_Base):
    #AI for a temporarily confused monster (reverts to previous AI after a while).
    def __init__(self, old_ai, num_turns=3):
        self.old_ai = old_ai
        self.num_turns = num_turns
        self.node = old_ai.node
        AI_Base.__init__(self)

    def take_turn(self,game):
        self.owner.fighter.ticker.schedule_turn(self.owner.fighter.speed,self.owner)
        if self.num_turns > 0:  #still confused...
            #move in a random direction, and decrease the number of turns confused
            self.owner.move(libtcod.random_get_int(0, -1, 1), libtcod.random_get_int(0, -1, 1),game.Map.map,game.objects)
            self.num_turns -= 1
 
        else:#restore the previous AI 
            self.owner.ai = self.old_ai
            self.owner.message.message('The ' + self.owner.name + ' is no longer confused!', 2)


class RangedMonster(AI_Base):
      #AI for a ranged type monster 
      def take_turn(self,game):
          #a mage takes its turn; if you can see it, it can see you. 
          if libtcod.map_is_in_fov(game.fov_map, self.owner.x, self.owner.y):
            
            
            #move towards plaer if far away 
            if self.owner.fighter.type == 'mage':
                if self.owner.distance_to(game.player) >= spell.max_range:
                    self.owner.move_towards(game.player.x, game.player.y,game.Map.map,game.objects)
                else:
                    #cast spell
                    pass
            if self.owner.fighter.type == 'ranged':
                if self.owner.distance_to(game.player) >= weapon.max_range:
                    self.owner.move_towards(game.player.x,game.player.y,game.Map.map,game.objects)
                else:
                    #ranged attack
                    pass
                    

               #close enough, cast spell


        


def monster_death(monster):
    if monster.ai.node:
        monster.ai.remove_from_node()
    #drop all of equipped gear from monsters
    for item in monster.fighter.wielded:
        if item:
            if item.item.equipment.type != 'monster_melee':
                monster.fighter.inventory.append(item)
    for item in monster.fighter.equipment:
        if item:
            monster.fighter.inventory.append(item)
    for item in monster.fighter.inventory:
        item.item.drop(monster.fighter.inventory, monster, False)
        item.send_to_back()
    #Add loot drops
    #Add gore
    monster.fighter.ticker.remove_object(monster)
    monster.message.message(monster.name.capitalize() + ' is dead!', 5)
    monster.char = '%'
    monster.color = libtcod.dark_red
    monster.blocks = False
    monster.fighter = None
    monster.ai = None
    monster.name = 'remains of ' + monster.name
    monster.send_to_back()



