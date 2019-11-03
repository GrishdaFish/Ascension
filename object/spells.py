import libtcodpy as libtcod
import object
import sys
import os
sys.path.append(os.path.join(sys.path[0],'utils'))
import utils.spell_effects as spell_effects

class Spell:
    def __init__(self,min=0,max=0,range=0,radius=0,targets=0,ef_type=None,ad_eff=None,spel_eff=None,eff_col=None):
        self.min=min
        self.max=max
        self.range=range
        self.radius=radius
        self.targets=targets
        self.type = ef_type
        self.effect_type=spells[ef_type]
        
        self.addition_effects=ad_eff
        self.spell_effects=spel_eff
        self.effect_color=eff_col
        
    def cast(self,target,player,game=None):
        if self.effect_type:
            return self.effect_type(self.min,self.max,self.range,self.radius,self.targets,target,player,game)
        
        
def heal(min,max,range,radius,targets,target,player,game):
    #heal the player
    if player==True:
        if target.fighter.hp == target.fighter.max_hp:
            target.message.message('You are already at full health.', libtcod.red)
            return 'cancelled'
     
        game.message.message('Your wounds start to feel better!', libtcod.light_violet)
    HEAL_AMOUNT = libtcod.random_get_int(0,min,max)
    target.fighter.heal(HEAL_AMOUNT)


def fireball(min,max,range,radius,targets,target,player,game):
    #ask the player for a target tile to throw a fireball at
    game.message.message('Left-click a target tile for the fireball, or right-click to cancel.', libtcod.light_cyan)
    (x, y) = target_tile(game,range)
    if x is None:
        game.message.message('You cancelled the spell!', libtcod.orange)
        return 'cancelled'
    game.message.message('The fireball explodes, burning everything within ' + str(radius) + ' tiles!', libtcod.orange)
    game.gEngine.particle_explosion(15, x, y, b=True, color=libtcod.red)
    FIREBALL_DAMAGE = libtcod.random_get_int(0,min,max)
    for obj in game.objects:  #damage every fighter in range, including the player
        if obj.distance(x, y) <= radius and obj.fighter:
            game.message.message('The ' + obj.name + ' gets burned for ' + str(FIREBALL_DAMAGE) + ' hit points.', libtcod.orange)
            obj.fighter.take_damage(FIREBALL_DAMAGE,player)


def lightning(min,max,range,radius,targets,target,player,game):
    #find closest enemy (inside a maximum range) and damage it
    monster = closest_monster(game,range)
    if monster is None:  #no enemy found within maximum range
        game.message.message('No enemy is close enough to strike.', libtcod.red)
        return 'cancelled'
 
    #zap it!
    LIGHTNING_DAMAGE = libtcod.random_get_int(0,min,max)
    game.message.message('A lighting bolt strikes the ' + monster.name + 
        ' with a loud thunder! The damage is '
        + str(LIGHTNING_DAMAGE) + ' hit points.', libtcod.light_blue)
        
    monster.fighter.take_damage(LIGHTNING_DAMAGE,player)
    #draw the effect
    spell_effects.path_effect(game,player.x,player.y,monster.x,monster.y,5)
    
    
def confuse(min,max,range,radius,targets,target,player,game):
    #ask the player for a target to confuse
    game.message.message('Left-click an enemy to confuse it, or right-click to cancel.', libtcod.light_cyan)
    monster = target_monster(game,range)
    if monster is None:
        game.message.message('You cancelled the spell!', libtcod.orange)
        return 'cancelled'
    
    numturns=libtcod.random_get_int(0,min,max)
    #replace the monster's AI with a "confused" one; after some turns it will restore the old AI
    old_ai = monster.ai
    monster.ai = object.ConfusedMonster(old_ai,num_turns=numturns)
    monster.ai.owner = monster  #tell the new component who owns it
    game.message.message('The eyes of the ' + monster.name + ' look vacant, as he starts to stumble around!', libtcod.light_green)  
 
spells = {
        'heal'       : heal,
        'fireball'   : fireball,
        'lightning'  : lightning,
        'confusion'  : confuse,
        'confuse'    : confuse,
        'none'       : None, 
        }   
        
##Targeting for spells
def target_monster(game,max_range=None):
    #returns a clicked monster inside FOV up to a range, or None if right-clicked
    while True:
        (x, y) = target_tile(game,max_range)
        if x is None:  #player cancelled
            return None
 
        #return the first clicked monster, otherwise continue looping
        for obj in game.objects:
            if obj.x == x and obj.y == y and obj.fighter and obj != game.player:
                return obj
 
def closest_monster(game,max_range):
    #find closest enemy, up to a maximum range, and in the player's FOV
    closest_enemy = None
    closest_dist = max_range + 1  #start with (slightly more than) maximum range
 
    for object in game.objects:
        if object.fighter and not object == game.player and libtcod.map_is_in_fov(game.fov_map, object.x, object.y):
            #calculate distance between this object and the player
            dist = game.player.distance_to(object)
            if dist < closest_dist:  #it's closer, so remember it
                closest_enemy = object
                closest_dist = dist
    return closest_enemy

def target_tile(game,max_range=None):
    #return the position of a tile left-clicked in player's FOV (optionally in a range), or (None,None) if right-clicked.
    while True:
        #render the screen. this erases the inventory and shows the names of objects under the mouse.
        game.render_all()
        libtcod.console_flush()
 
        key = libtcod.console_check_for_keypress()
        mouse = libtcod.mouse_get_status()  #get mouse position and click status
        (x, y) = (mouse.cx, mouse.cy)
 
        if mouse.rbutton_pressed or key.vk == libtcod.KEY_ESCAPE:
            return (None, None)  #cancel if the player right-clicked or pressed Escape
 
        #accept the target if the player clicked in FOV, and in case a range is specified, if it's in that range
        if (mouse.lbutton_pressed and libtcod.map_is_in_fov(game.fov_map, x, y) and
            (max_range is None or game.player.distance(x, y) <= max_range)):
            return (x, y)
            
def line_listener(x,y):
    pass
    
def path_listener(x,y):
    pass
        
        
        