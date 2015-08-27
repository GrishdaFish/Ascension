import sys
import os
import math
sys.path.append(sys.path[0])
import libtcodpy as libtcod
sys.path.append(os.path.join(sys.path[0],'game'))
import combat

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
        self.blocks = blocks
        self.objects = None
        self.message = None
        self.type = None
        
        self.fighter = fighter
        if self.fighter:
            self.fighter.owner = self
            
        self.ai = ai
        if self.ai:
            self.ai.owner = self
 
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
 
    def draw(self, fov_map, gEngine, force_display=False):
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
            fr,fg,fb = self.color
            br,bg,bb = col
            gEngine.console_put_char_ex(self.con,self.x,self.y,self.char,fr,fg,fb,br,bg,bb)#self.char,self.color,col)
 
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


class Fighter:
    #combat-related properties and methods (monster, player, NPC).
    def __init__(self, hp, defense, power, death_function=None, Con=10, Str=10,Dex=10,Int=10,money=0,ticker=None,speed=0,xp_value=0):
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
        self.unused_skill_points = 0
        self.defense = 0

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

        self.skills = combat.skill_list

    def level_up(self):
        self.xp_to_next_level, sp = combat.next_level(self.level)
        self.unused_skill_points += sp
        self.level += 1
        self.max_hp += combat.hp_bonus(self.stats[3])
        hp = self.max_hp
        self.hp = hp

    def apply_skill_points(self):
        pass

    def set_armor_bonus(self):
        bonus = 0
        for item in self.equipment:
            if item is not None:
                bonus += item.item.equipment.bonus
        self.armor_bonus = bonus

    def set_armor_penalty(self):
        penalty = 0
        for item in self.equipment:
            if item is not None:
                penalty += item.item.equipment.penalty
        self.armor_penalty = penalty

    def get_skill(self, name):
        for skill in self.skills:
            if skill.get_name() == name:
                return skill
        return None

    def attack(self, target, player=False):
        if not player:
            col = 2
        else:
            col = 5

        attack_roll = libtcod.random_get_int(0, 1, 20)
        attack_roll += combat.get_melee_bonus(self.owner)

        evasion_roll = combat.get_evasion_class(target)
        deflection_roll = combat.get_deflection_class(target)
        blocking_roll = combat.get_blocking_class(target)

        msg = 'A: %d, E: %d, D: %d, B: %d ' % (attack_roll, evasion_roll, deflection_roll, blocking_roll)
        #self.owner.message.message(msg)
        if evasion_roll > attack_roll:
            msg += '...Evaded'
        elif deflection_roll > attack_roll:  # need to check for a weapon or something that can deflect
            msg += '...Deflected'
        elif blocking_roll > attack_roll:  # need to check for shield
            msg += '...Blocked'
        else:
            dmg = 0
            if self.wielded[0] is not None:
                skill = self.get_skill(self.wielded[0].item.equipment.damage_type)
                dmg = skill.get_bonus()
                if dmg is None:
                    dmg = 0
                dmg += self.wielded[0].item.equipment.calc_damage()
                dmg = int(dmg)
                msg += '...Successful. Hit for %d damage!' % dmg
                self.owner.message.message(msg, col)
            else:
                #For dual wielding
                pass
            if dmg > 0:
                if attack_roll < 10 + self.armor_bonus:
                    dmg *= 0.25
                    dmg = int(dmg)
                #make the target take some damage
                self.owner.message.message(self.owner.name.capitalize() + ' attacks ' + target.name + ' for ' + str(dmg) + ' hit points.',col)
                target.fighter.take_damage(dmg, self.owner)

            else:
                if libtcod.random_get_int(0, 0, 100) < 25:  # 25% chance to always do at least 1 damage
                    target.fighter.take_damage(1, self.owner)
                else:
                    self.owner.message.message(self.owner.name.capitalize() + ' attacks ' + target.name + ' but it has no effect!', col)
            #else:
            #    self.owner.message.message(self.owner.name.capitalize()+' misses ' + target.name +'.',col)

        '''#get the attackers chance to hit, 5% chance at least to hit
        to_hit = libtcod.random_get_float(0,5.00,100.00)
        to_hit+=self.base_attack_bonus
        
        #base 5% chance to miss
        to_miss = libtcod.random_get_float(0,5.00,100.00)
        to_miss+=target.fighter.base_defense_bonus
            
        if to_hit > to_miss:
            if not self.wielded[0] and not self.wielded[1]:
                damage = self.power - target.fighter.defense
            else:
                wep = self.wielded[0].item.equipment
                if not target.fighter.equipment[0]:
                    damage = self.power + wep.calc_damage(damage_type=wep.damage_type) - target.fighter.defense
                else:
                    bdt=target.fighter.equipment[0].item.equipment.best_defense_type
                    wdt=target.fighter.equipment[0].item.equipment.worst_defense_type
                    damage = self.power + wep.calc_damage(damage_type=wep.damage_type,best_type=bdt,worst_type=wdt) - target.fighter.defense
                    
                crit = libtcod.random_get_float(0,0,100.00)
                if crit <= (self.base_crit_bonus+wep.crit_bonus):
                    self.owner.message.message('CRIT',3)
                    damage = damage*2
                    #damage = damage**damage <-- LOL
                    #CRIT
                    #Player attacks troll for 437,893,890,380,859,375 hit points.
                    
            if damage > 0:
                #make the target take some damage
                self.owner.message.message(self.owner.name.capitalize() + ' attacks ' + target.name + ' for ' + str(damage) + ' hit points.',col)
                target.fighter.take_damage(damage,self.owner)
            else:
                if libtcod.random_get_int(0,0,100) < 25:#25% chance to always do at least 1 damage
                    target.fighter.take_damage(1,self.owner)
                else:
                    self.owner.message.message(self.owner.name.capitalize() + ' attacks ' + target.name + ' but it has no effect!',col)
        else:
            self.owner.message.message(self.owner.name.capitalize()+' misses ' + target.name +'.',col)'''

    def take_damage(self, damage, attacker):
        #apply damage if possible
        if damage > 0:
            self.hp -= damage
 
            #check for death. if there's a death function, call it
            if self.hp <= 0:
                attacker.fighter.current_xp += self.current_xp
                function = self.death_function
                if function is not None:
                    function(self.owner)
 
    def heal(self, amount):
        #heal by the given amount, without going over the maximum
        self.hp += amount
        if self.hp > self.max_hp:
            self.hp = self.max_hp
            
#x,y offsets for co-ords next to the player
offsets = [(1,0),(0,1),(-1,0),(0,-1),
           (1,1),(-1,1),(-1,-1),(1,-1)]


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
        
class BasicMonster:
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
            
class WanderingMonster:
    #Ai for a monster to randomly wander around when not in the view of the player
    def __init__(self,radius=3,x=0,y=0):
        self.radius = radius
        self.dest = False        
        self.home_x = x
        self.home_y = y
        
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
            self.owner.ai = BasicMonster()
            self.owner.ai.owner = self.owner
            
class ConfusedMonster:
    #AI for a temporarily confused monster (reverts to previous AI after a while).
    def __init__(self, old_ai, num_turns=3):
        self.old_ai = old_ai
        self.num_turns = num_turns
 
    def take_turn(self,game):
        self.owner.fighter.ticker.schedule_turn(self.owner.fighter.speed,self.owner)
        if self.num_turns > 0:  #still confused...
            #move in a random direction, and decrease the number of turns confused
            self.owner.move(libtcod.random_get_int(0, -1, 1), libtcod.random_get_int(0, -1, 1),game.Map.map,game.objects)
            self.num_turns -= 1
 
        else:#restore the previous AI 
            self.owner.ai = self.old_ai
            self.owner.message.message('The ' + self.owner.name + ' is no longer confused!', 2)
 
class RangedMonster:
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
    #drop all of equipped gear from monsters
    for item in monster.fighter.wielded:
        if item:
            monster.fighter.inventory.append(item)
    for item in monster.fighter.equipment:
        if item:
            monster.fighter.inventory.append(item)
    for item in monster.fighter.inventory:
        item.item.drop(monster.fighter.inventory,monster,False)
        item.send_to_back()
        
    monster.fighter.ticker.remove_object(monster)
    monster.message.message(monster.name.capitalize() + ' is dead!', 5)
    monster.char = '%'
    monster.color = libtcod.dark_red
    monster.blocks = False
    monster.fighter = None
    monster.ai = None
    monster.name = 'remains of ' + monster.name
    monster.send_to_back()



