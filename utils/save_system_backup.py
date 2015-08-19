        
##Find out what type is of object the object is
##Build a struct for it and save it
##For loading, parse the struct and rebuild it
##Not saving the Ticker yet
##Need to also save the map
def save(game):
    save_struct=''
    file=open('save','w')
    map_struct = 'object_type "map" {\n'
    map_struct+= 'string type="level_1"\n'
    bitmap = game.Map.return_bitmask_map()
    map_struct+= 'string bitmask_map= "%s"\n}\n'%bitmap
    save_struct+=map_struct
    player_struct = 'object_type "player" {\n'
    player_struct+='string ob_type="player"\n'
    player_struct+=object_to_save(game.player)
    save_struct+=player_struct
    
    for object in game.player.fighter.inventory:
        if object.item:
            if object.item.spell:
                save_struct+='object_type "consumable" {\n'
                save_struct+='string ob_type="consumable"\n'
                save_struct+='bool inventory=true\n'
                save_struct+=object_to_save(object)
            if object.item.equipment:
                if object.item.equipment.type =='armor':
                    save_struct+='object_type "armor" {\n'
                    save_struct+='string ob_type="armor"\n'
                    save_struct+='bool inventory=true\n'
                    save_struct+=object_to_save(object)
                if object.item.equipment.type =='melee':
                    save_struct+='object_type "weapon" {\n'
                    save_struct+='string ob_type="weapon"\n'
                    save_struct+='bool inventory=true\n'
                    save_struct+=object_to_save(object)
        
    for object in game.player.fighter.equipment:
        if object:
            if object.item:
                if object.item.equipment:
                    if object.item.equipment.type =='armor':
                        save_struct+='object_type "armor" {\n'
                        save_struct+='string ob_type="armor"\n'
                        save_struct+='bool equipped=true\n'
                        save_struct+=object_to_save(object)
    i=0    
    for object in game.player.fighter.wielded:
        if object:
            if object.item:
                if object.item.equipment:
                    if object.item.equipment.type =='melee':
                        save_struct+='object_type "weapon" {\n'
                        save_struct+='string ob_type="weapon"\n'
                        save_struct+='int in_hand=%i\n'%i                        
                        i+=1
                        save_struct+=object_to_save(object)
        
    game.objects.remove(game.player)
    
    for object in game.objects:
        if object.ai:
            save_struct+='object_type "monster" {\n'            
            save_struct+='string ob_type="monster"\n'
            save_struct+=object_to_save(object)
        if object.item:
            if object.item.spell:
                save_struct+='object_type "consumable" {\n'
                save_struct+='string ob_type="consumable"\n'
                save_struct+=object_to_save(object)
            if object.item.equipment:
                if object.item.equipment.type =='armor':
                    save_struct+='object_type "armor" {\n'
                    save_struct+='string ob_type="armor"\n'
                    save_struct+=object_to_save(object)
                if object.item.equipment.type =='melee':
                    save_struct+='object_type "weapon" {\n'
                    save_struct+='string ob_type="weapon"\n'
                    save_struct+=object_to_save(object)
        if object.misc:
            save_struct+='object_type "misc" {\n'
            save_struct+='string ob_type="misc"\n'
            save_struct+=object_to_save(object)
    
    
    file.write(save_struct)
    file.close()
    

def load(game):
    p = Parser(game.logger)
    objects=p.run('save')
    game.ticker.schedule.clear()
    game.objects = []
    for object in objects:
        if object.type == 'player':
            fighter_component = Fighter(hp=object.max_hp, defense=object.defense,
                power=object.power, death_function=game.player_death, 
                money=object.money,speed=object.speed,xp_value=object.current_xp)
            game.player = Object(game.con,object.x, object.y,object.char, 
                object.name, object.color, blocks=object.blocks,fighter=fighter_component)
            game.player.fighter.level = object.level
            game.player.fighter.xp_to_next_level=object.xp_to_next_level
            game.player.objects=game.objects
            game.player.message=game.message
            game.objects.append(game.player)
            game.ticker.schedule_turn(0,game.player)
            
        if object.ob_type == 'monster':
            #print object.current_xp
            fighter_component = Fighter(hp=object.hp, defense=object.defense, 
                power=object.power, death_function=monster_death,ticker=game.ticker,
                speed=object.speed,xp_value=object.current_xp)
            ai_component = BasicMonster()

            monster = Object(game.con,object.x, object.y, object.char, object.name, object.color,
                blocks=object.blocks, fighter=fighter_component, ai=ai_component)
                
            monster.fighter.ticker.schedule_turn(monster.fighter.speed, monster)            
            
            game.objects.append(monster)
            monster.objects=game.objects
            monster.message=game.message
            
        if object.ob_type == 'consumable':
            spell_component = Spell(min=object.min,max=object.max,range=object.range,
                        radius=object.targets,ef_type=object.effect_type,ad_eff=object.add_eff,
                        spel_eff=object.spell_eff,eff_col=object.eff_col)
            item_component = Item(spell=spell_component)
     
            item = Object(game.con,object.x, object.y, object.char, object.name, 
                object.color, item=item_component)
            if object.inventory:
                game.player.fighter.inventory.append(item)
            else:
                game.objects.append(item)                
                item.send_to_back(game.objects) 
            item.objects=game.objects
            item.message=game.message #items appear below other objects
            
        if object.ob_type == 'armor':
            equip_component = Equipment(defense=object.defense,type=object.type,location=object.location,
                best_defense_type=object.best_defense_type,worst_defense_type=object.worst_defense_type)
            
            item_component = Item(equipment=equip_component)
            equip = Object(game.con,object.x,object.y,object.char,object.name,
                object.color,item=item_component)
            if object.inventory:
                game.player.fighter.inventory.append(equip)
            elif object.equipment:
                game.player.fighter.defense-=object.defense
                equip.item.equipment.equip(game.player,owner=equip.item.owner)
            else:
                game.objects.append(equip)
            equip.objects=game.objects
            equip.message=game.message
            
        if object.ob_type == 'weapon':
            equip_component = Equipment(min_power=object.min_power,max_power=object.max_power,
                crit_bonus=object.crit_bonus,type=object.type,handed=object.handed,
                dual_wield=object.dual_wield,damage_type=object.damage_type)
            item_component = Item(equipment=equip_component)
            equip = Object(game.con,object.x,object.y,object.char,object.name,
                object.color,item=item_component)
            if object.inventory:
                game.player.fighter.inventory.append(equip)
            elif object.in_hand==0:
                game.player.fighter.wielded[0]=equip
            elif object.in_hand==1:
                game.player.fighter.wielded[1]=equip
            else:
                game.objects.append(equip)   
            equip.objects=game.objects
            equip.message=game.message
            
        if object.ob_type == 'misc':
            m=Misc(type=object.type)
            misc = Object(game.con,object.x,object.y,object.char,
                object.name,object.color,blocks=object.blocks,misc=m)
            game.objects.append(misc)
            misc.objects= game.objects
            misc.message=game.message
            misc.send_to_back(game.objects)
            
        if object.ob_type == 'map':
            temp = string.split(object.bitmap,' ')
            temp_list=[]
            for i in range(len(temp)):
                t=temp[i].strip(',[]')
                temp_list.append(int(t))
                
            game.Map.build_bitmask_map(temp_list)
            
    #print game.objects



def object_to_save(object):
    ob_struct = ''
    ob_struct+='int pos_x=%i\n'%object.x
    ob_struct+='int pos_y=%i\n'%object.y
    ob_struct+="char cell='%c'\n"%object.char
    ob_struct+='string name="%s"\n'%object.name
    ob_struct+='color col="%i,%i,%i"\n'%(object.color[0],object.color[1],object.color[2])
    if object.blocks:
        b='true'
    else:
        b='false'
    ob_struct+='bool blocks=%s\n'%b
    if object.fighter:
        ob_struct+='int max_hp=%i\n'%object.fighter.max_hp
        ob_struct+='int hp=%i\n'%object.fighter.hp
        ob_struct+='int defense=%i\n'%object.fighter.defense
        ob_struct+='int power=%i\n'%object.fighter.power
        ob_struct+='string type="%s"\n'%object.fighter.type
        ob_struct+='int money=%i\n'%object.fighter.money
        ob_struct+='int speed=%i\n'%object.fighter.speed
        ob_struct+='int current_xp=%i\n'%object.fighter.current_xp
        ob_struct+='int xp_to_next_level=%i\n'%object.fighter.xp_to_next_level
        ob_struct+='int level=%i\n'%object.fighter.level
    if object.item:
        if object.item.equipment:
            if object.item.equipment.type == 'armor':
                ob_struct+='int defense=%i\n'%object.item.equipment.defense
                ob_struct+='string location="%s"\n'%object.item.equipment.location
                ob_struct+='string best_defense_type="%s"\n'%object.item.equipment.best_defense_type
                ob_struct+='string worst_defense_type="%s"\n'%object.item.equipment.worst_defense_type
                ob_struct+='string type="%s"\n'%object.item.equipment.type
            if object.item.equipment.type == 'melee': 
                ob_struct+='int max_power=%i\n'%object.item.equipment.max_power
                ob_struct+='int min_power=%i\n'%object.item.equipment.min_power
                ob_struct+='float crit_bonus=%f\n'%object.item.equipment.crit_bonus
                ob_struct+='int handed=%i\n'%object.item.equipment.handed
                if object.item.equipment.dual_wield:
                    d='true'
                else:
                    d='false'
                ob_struct+='bool dual_wield=%s\n'%d
                ob_struct+='string damage_type="%s"\n'%object.item.equipment.damage_type
                ob_struct+='string type="%s"\n'%object.item.equipment.type

        if object.item.spell:
            ob_struct+='int min=%i\n'%object.item.spell.min
            ob_struct+='int max=%i\n'%object.item.spell.max
            ob_struct+='int range=%i\n'%object.item.spell.range
            ob_struct+='int targets=%i\n'%object.item.spell.targets
            ob_struct+='string effect_type="%s"\n'%object.item.spell.effect_type.__name__
            ob_struct+='string additional_effects="%s"\n'%object.item.spell.addition_effects
            ob_struct+='string spell_effects="%s"\n'%object.item.spell.spell_effects
            ob_struct+='color effect_col="%i,%i,%i"\n'%(object.item.spell.effect_color[0],object.item.spell.effect_color[1],object.item.spell.effect_color[2])
            ob_struct+='string type="consumable"\n'
    if object.misc:
        ob_struct+='string type="%s"\n'%object.misc.type
        
        
    ob_struct+='}\n'
    return ob_struct
    







class Parser:
    def __init__(self,logger):
        self.parser = libtcod.parser_new()
        self.object_type = libtcod.parser_new_struct(self.parser,'object_type')
        #libtcod.struct_add_list_property(self.object_type,"bitmask_map",libtcod.TYPE_INT,False)
        self.object_list = []
        self.logger=logger
        self.logger.log.info('Creating save file parser.')
    def run(self,file):
        self.logger.log.info('Parsing save file: %s ...'%file)
        libtcod.parser_run(self.parser,file,Listener(self.object_list,self.logger))        
        return self.object_list
        

class Listener:
    def __init__(self,object_list,logger):
        self.object_list = object_list
        self.logger=logger
    def new_struct(self, struct, name):
        if name == 'map':
            self.object = Map()
            self.struct_type=name
        else:
            self.object = LoadObject()
            self.struct_type=name
        return True
    def new_property(self,name, typ, value):
        self.add_value(name,value)
        return True
    
    def add_value(self,type,value):
        if type == 'ob_type':self.object.ob_type=value
        if self.struct_type == 'map':self.map_parse(type,value)
        if self.struct_type == 'monster':self.monster_parse(type,value)
        if self.struct_type == 'weapon':self.weapon_parse(type,value)
        if self.struct_type == 'armor':self.armor_parse(type,value)
        if self.struct_type == 'consumable':self.consum_parse(type,value)
        if self.struct_type == 'player':self.player_parse(type,value)
        if self.struct_type == 'misc':self.misc_parse(type,value) 
    
    def map_parse(self,type,value):
        if type == 'bitmask_map':self.object.bitmap=value
        if type == 'type':self.object.type=value
        
    def monster_parse(self,type,value):
        if type == 'pos_x':self.object.x=value
        if type == 'pos_y':self.object.y=value
        if type == 'cell':self.object.char=value
        if type == 'name':self.object.name=value
        if type == 'col':self.object.color=value
        if type == 'blocks':self.object.blocks=value
        if type == 'type':self.object.type=value
        if type=='max_hp':self.object.max_hp=value
        if type=='hp':self.object.hp=value
        if type=='defense':self.object.defense=value
        if type=='power':self.object.power=value
        if type=='money':self.object.money=value
        if type=='speed':self.object.speed=value
        if type=='current_xp':self.object.current_xp=value
        
        
    def weapon_parse(self,type,value):
        if type == 'inventory':self.object.inventory=value
        if type == 'in_hand':self.object.in_hand=value
        if type == 'pos_x':self.object.x=value
        if type == 'pos_y':self.object.y=value
        if type == 'cell':self.object.char=value
        if type == 'name':self.object.name=value
        if type == 'col':self.object.color=value
        if type == 'blocks':self.object.blocks=value
        if type == 'type':self.object.type=value
        if type=='max_power':self.object.max_power=value
        if type=='min_power':self.object.min_power=value
        if type=='crit_bonus':self.object.crit_bonus=value
        if type=='handed':self.object.handed=value
        if type=='dual_wield':self.object.dual_wield=value
        if type=='damage_type':self.object.damage_type=value
        
    def armor_parse(self,type,value):
        if type == 'inventory':self.object.inventory=value
        if type == 'equipped':self.object.equipment=value
        if type == 'pos_x':self.object.x=value
        if type == 'pos_y':self.object.y=value
        if type == 'cell':self.object.char=value
        if type == 'name':self.object.name=value
        if type == 'col':self.object.color=value
        if type == 'blocks':self.object.blocks=value
        if type == 'type':self.object.type=value
        if type=='defense':self.object.defense=value
        if type=='location':self.object.location=value
        if type=='best_defense_type':self.object.best_defense_type=value
        if type=='worst_defense_type':self.object.worst_defense_type=value
        
    def consum_parse(self,type,value):
        if type == 'inventory':self.object.inventory=value
        if type == 'pos_x':self.object.x=value
        if type == 'pos_y':self.object.y=value
        if type == 'cell':self.object.char=value
        if type == 'name':self.object.name=value
        if type == 'col':self.object.color=value
        if type == 'blocks':self.object.blocks=value
        if type == 'type':self.object.type=value
        if type=='min':self.object.min=value
        if type=='max':self.object.max=value
        if type=='range':self.object.range=value
        if type=='targets':self.object.targets=value
        if type=='effect_type':self.object.effect_type=value
        if type=='additional_effects':self.object.add_eff=value
        if type=='spell_effects':self.object.spell_eff=value
        if type=='effect_col':self.object.eff_col=value
        
    def player_parse(self,type,value):
        self.object.type='player'
        
        if type == 'pos_x':self.object.x=value
        if type == 'pos_y':self.object.y=value
        if type == 'cell':self.object.char=value
        if type == 'name':self.object.name=value
        if type == 'col':self.object.color=value
        if type == 'blocks':self.object.blocks=value
        if type == 'type':self.object.type=value
        if type=='max_hp':self.object.max_hp=value
        if type=='hp':self.object.hp=value
        if type=='defense':self.object.defense=value
        if type=='power':self.object.power=value
        if type=='money':self.object.money=value
        if type=='speed':self.object.speed=value
        if type=='current_xp':self.object.current_xp=value
        if type=='xp_to_next_level':self.object.xp_to_next_level=value
        if type=='level':self.object.level=value
        
    def misc_parse(self,type,value):
        if type == 'pos_x':self.object.x=value
        if type == 'pos_y':self.object.y=value
        if type == 'cell':self.object.char=value
        if type == 'name':self.object.name=value
        if type == 'col':self.object.color=value
        if type == 'blocks':self.object.blocks=value
        if type == 'type':self.object.type=value
        
    def new_flag(self, name): 
        return True
        
    
        
    def end_struct(self, struct, name):
        self.object_list.append(self.object)
        return True
        
    def error(self,msg):
        self.logger.log.error(msg)
        print 'error : ', msg
        return True
    

class LoadObject:
    def __init__(self):
        self.ob_type=""
        self.x=0
        self.y=0
        self.char=0
        self.name=""
        self.max_hp=0
        self.hp=0
        self.defense=0
        self.power=0
        self.type=""
        self.money=0
        self.speed=0
        self.location=""
        self.best_defense_type=""
        self.worst_defense_type=""
        self.min_power=0
        self.max_power=0
        self.crit_bonus=0.0
        self.handed=0
        self.dual_wield=False
        self.damage_type=""
        self.min=0
        self.max=0
        self.range=0
        self.targets=0
        self.effect_type=""
        self.add_eff=""
        self.spell_eff=""
        self.eff_col=None
        self.color=None
        self.blocks=False
        self.inventory=False
        self.equipment=False
        self.in_hand=None
        self.current_xp=0
        self.xp_to_next_level=0
        self.level=0
        self.strength=0
        self.intel=0
        self.dext=0
class Map:
    def __init__(self):
        self.bitmap=[]
        self.type=""
        self.ob_type="map"
        

    
    
 
global fighter_names_unmask,fighter_name_bit
ob_shift=5
def bitmask_save(game):
    
    bitmap=game.Map.return_bitmask_map()
    fighter_names={}
    fighter_names_unmask={}
    fighter_name_bit=1
    for i in range(len(game.build_objects.monsters)):
        if i > 0:
            fighter_name_bit=i*2
        fighter_names[game.build_objects.monsters[i].name]=fighter_name_bit
        fighter_names_unmask[fighter_name_bit]=game.build_objects.monsters[i].name
    fighter_name_bit*=2
    fighter_names['player']=fighter_name_bit
    fighter_names_unmask[fighter_name_bit]='player'
    fighter_name_bit-=1
    i=0
    ob_save=[]
    for object in game.objects:
        bit_shift=1
        ob_mask=0
        if object.ai:
            ob_mask | 1
            bit_shift=+1
        if object.fighter:
            ob_mask = ob_mask | 1<<(bit_shift-1)
            ob_mask = ob_mask | fighter_names[object.name]<<bit_shift
            #ob_name = fighter_names_unmask[(ob_mask>>bit_shift) & fighter_name_bit]
            size=len(str(object.x))+len(str(object.y))+len(str(object.fighter.hp))+len(str(ob_mask))+5
            print size
            ob='%i\x00%i\x00%i\x00%i\x00%i\x01'%(size,object.x,object.y,object.fighter.hp,ob_mask)
            ob_save.append(ob)
        
        #if object.item.spell:ob_mask | 4
        #if object.item.equipment:ob_mask | 8
        #if object.misc:ob_mask | 16
        i+=1
    file = open('savegame', 'wb')
    for item in ob_save:        
        file.write(item)
    file.close()
        
        
def get_next_int(file,offset):
    i = 0
    num=""
    while True:
        file.seek(i+offset)
        f=file.read(1)
        if f is not '\x00' or f is not '\x01':
            num+=f
        else:
            return int(num)
        i+=1
        
def bitmask_load(game):    
    file = open('savegame','rb')
    file.seek(0)
    if len(file.read(2)
    print read   