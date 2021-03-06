import sys
import os
import string
import logging
import zlib
sys.path.append(os.path.join(sys.path[0], 'map'))
sys.path.append(os.path.join(sys.path[0], 'object'))

MAP = None
try:
    import libtcodpy as libtcod
    import map.map as MAP
    import object.object as OBJECT
    import object.misc as MISC
except ImportError:
    pass

PADDING = '****'  # to signify the end of a block of data
END_OF_OBJECT = "&&&&"  # the end of an entire object (player, level, etc..)

MAP_PADDING = '@'  # between each "tile" of the map
END_OF_MAP = '!!!!'  # the end of the map

END_OF_MISC = '####'  # the end of the misc objects in the level
END_MISC = '#---'

END_OF_ITEMS = '$$$$'  # the end of the items in the level
END_ITEM = '$---'

END_OF_MONSTERS = "%%%%"  # the end of the monsters in the level
END_MONSTER = '%---'

END_SKILL = '(---'

END_HOTBAR = ')---'
END_PLAYER = '@---'
END_INVENTORY = '@###'
END_EQUIPMENT = '@$$$$'
END_WIELDED = '@%%%'
END_SKILLS = '@^^^'
END_HOTBARS = '@&&@'


class Object:  # an object we use to hold save information
    def __init__(self, name=None, x=None, y=None, hp=None, max_hp=None):
        self.name = name
        self.x = x
        self.y = y
        self.hp = hp
        self.max_hp = max_hp


def save(game):
    path = os.path.join(sys.path[0],'content')
    path = path.replace('core.exe','')
    if os.path.isfile(os.path.join(path, 'save.sav')):
        pass
    else:
        pass
    save_file = open(os.path.join(path, 'save.sav'), 'wb')

    completed_save = ''
    completed_save += game.version
    completed_save += END_OF_OBJECT

    completed_save += str(len(game.current_dungeon)+1)  # remove +1 after town gets added
    completed_save += END_OF_OBJECT

    completed_save += str(game.depth)
    completed_save += END_OF_OBJECT

    completed_save += save_player(game.player, game)

    for level in game.current_dungeon:
        completed_save += save_level(game, level)

    completed_save = zlib.compress(completed_save)
    save_file.write(completed_save)
    save_file.close()


def save_level(game, level):
    ret = ''
    ret += str(level.depth)
    ret += MAP_PADDING
    ret += save_map(game, level.map)

    mis, it, mob = 0, 0, 0  # tells us how many of each item are in the level for when we load
    for obj in level.objects:
        if obj.misc:
            mis += 1
        if obj.item:
            it += 1
        if obj.fighter and obj.name != game.player.name:  # ignore player
            mob += 1

    #preface object block with number of objects
    #ret += str(mis)
    #ret += PADDING
    for obj in level.objects:
        if obj.misc:
            ret += save_misc(obj)
    ret += END_OF_MISC
    #preface object block with number of objects
    #ret += str(it)
    #ret += PADDING
    for obj in level.objects:
        if obj.item:
            ret += save_item(obj)
    ret += END_OF_ITEMS

    #preface object block with number of objects
    #ret += str(mob)
    #ret += PADDING
    for obj in level.objects:
        if obj.fighter and obj.name != game.player.name:  # ignore player
            ret += save_monster(obj)
    ret += END_OF_MONSTERS
    ret += END_OF_OBJECT
    return ret


def save_monster(mob):
    mob_save = ''

    mob_save += mob.name
    mob_save += PADDING

    mob_save += str(mob.x)
    mob_save += PADDING

    mob_save += str(mob.y)
    mob_save += PADDING

    mob_save += str(mob.fighter.hp)
    mob_save += PADDING

    mob_save += str(mob.fighter.max_hp)
    mob_save += END_MONSTER
    #save mob inventory/equipment

    return mob_save


def save_map(game, mapp):
    ret = ''

    mapp = game.Map.return_bitmask_map(map=mapp)
    for i in mapp:
        ret += str(i)
        ret += MAP_PADDING
    ret += END_OF_MAP
    return ret


def save_item(item):
    ret = ''
    '''if item.x is None and item.y is None:
        pass  # Item is in player inventory, only save name and if its equipped or not
    else:'''
    ret += item.name
    ret += PADDING

    ret += str(item.x)
    ret += PADDING

    ret += str(item.y)
    ret += PADDING

    ret += str(item.item.qty)
    ret += END_ITEM

    return ret


def save_misc(misc):
    ret = ''

    ret += misc.name
    ret += PADDING

    ret += str(misc.x)
    ret += PADDING

    ret += str(misc.y)
    ret += END_MISC

    return ret


def save_skill(skill):
    ret = ''

    ret = skill.get_name()
    ret += PADDING

    ret += str(skill.get_bonus())
    ret += END_SKILL

    return ret


def save_player(player, game):
    player_save = ''
    player_save += player.name
    player_save += PADDING

    player_save += str(player.x)
    player_save += PADDING

    player_save += str(player.y)
    player_save += PADDING

    player_save += str(player.fighter.hp)
    player_save += PADDING

    player_save += str(player.fighter.max_hp)
    player_save += PADDING

    player_save += str(player.fighter.money)
    player_save += PADDING

    player_save += str(player.fighter.level)
    player_save += PADDING

    player_save += str(player.fighter.current_xp)
    player_save += PADDING

    player_save += str(player.fighter.xp_to_next_level)
    player_save += PADDING

    player_save += str(player.fighter.unused_skill_points)
    player_save += PADDING


    player_save += END_PLAYER

    for item in player.fighter.inventory:
        player_save += save_item(item)
    player_save += END_INVENTORY

    for item in player.fighter.equipment:
        if item is not None:
            player_save += save_item(item)
    player_save += END_EQUIPMENT

    for item in player.fighter.wielded:
        if item is not None:
            player_save += save_item(item)
            if item.item.equipment.handed == 2:
                break
    player_save += END_WIELDED

    for item in player.fighter.skills:
        if item is not None:
            player_save += save_skill(item)
    player_save += END_SKILLS

    i = 0
    for slot in game.hotbar.slots:
        player_save += slot.name
        player_save += PADDING
        player_save += str(i)
        player_save += END_HOTBAR
        i += 1
    player_save += END_HOTBARS

    player_save += END_OF_OBJECT
    return player_save


def load(game=None):
    path = os.path.join(sys.path[0],'content')
    path = path.replace('core.exe','')
    if os.path.isfile(os.path.join(path, 'save.sav')):
        save_file = open(os.path.join(path, 'save.sav'), 'rb')
    else:
        return
    s = save_file.read()
    save_file.close()
    s = zlib.decompress(s)
    save_array = string.split(s, END_OF_OBJECT)

    version = save_array.pop(0)
    num_levels = save_array.pop(0)
    current_depth = int(save_array.pop(0))
    p = save_array.pop(0)
    save_array.pop(len(save_array)-1)  # remove this line after town is added.

    if game:
        load_player(game.player, p, game)
        game.depth = current_depth
        for level in save_array:  # only thing left in the save array are individual levels
            game.current_dungeon.append(load_level(level, game))
    else:
        #load_player(Object(), p)
        for level in save_array:  # only thing left in the save array are individual levels
            load_level(level)


def load_player(player, p, game=None):
    p = string.split(p, END_PLAYER) # split player object by end player string
    i = p[1] # get items from the second half of the first split
    # first half of items are in the inventory, second half is the rest of hte player save
    items = string.split(i, END_INVENTORY)  # [0] inventory [1] (Equipment, Wielded, Skills, Hotbar)
    # Then we split out equipment from the rest of the save, including wielded items
    equipment = string.split(items[1], END_EQUIPMENT)  # [0] equipment [1] Wielded, Skills, Hotbar
    # next we separate wielded items out of the second half of equipment
    wielded = string.split(equipment[1], END_WIELDED)  # [0] wielded items, [1] (Skills, Hotbar)
    # then we pull out skills out of the second half of wielded
    skills = string.split(wielded[1], END_SKILLS)  # [0] skills [1] (Hotbar)
    # Pull out hotbar from skills
    hotbar = string.split(skills[1], END_HOTBARS)  # [0] Hotbar [1] (Blank)

    items = string.split(items[0], END_ITEM)  # Split items apart into a list
    hotbar = string.split(hotbar[0], END_HOTBAR)
    skills = string.split(skills[0], END_SKILL)
    equipment = string.split(equipment[0], END_ITEM)
    wielded = string.split(wielded[0], END_ITEM)

    if len(items) > 1:
        items.pop(len(items)-1)
        for item in items:
            player.fighter.inventory.append(load_item(Object(), item, game))
    if len(equipment) > 1:
        equipment.pop()
        for item in equipment:
            i = load_item(Object(), item, game)
            player.fighter.inventory.append(i)
            i.item.use(player.fighter.inventory, player, game, True)
    if len(wielded) > 1:
        wielded.pop()
        for item in wielded:
            i = load_item(Object(), item, game)
            player.fighter.inventory.append(i)
            i.item.use(player.fighter.inventory, player, game, True)

    if len(skills) >1:
        skills.pop()
        for skill in skills:
            skill = string.split(skill, PADDING)
            s = player.fighter.get_skill(skill[0])
            s.set_bonus(int(skill[1]))

    if len(hotbar) >1:
        hotbar.pop()
        for slot in hotbar:
            slot = string.split(slot, PADDING)
            for item in player.fighter.inventory:
                if slot[0] == item.name:
                    game.hotbar.add_slot_object(int(slot[1]), item)


    p = string.split(p[0], PADDING)
    player.name = p[0]
    player.x = int(p[1])
    player.y = int(p[2])
    player.fighter.hp = int(p[3])
    player.fighter.max_hp = int(p[4])
    player.fighter.money = int(p[5])
    player.fighter.level = int(p[6])
    player.fighter.current_xp = int(p[7])
    player.fighter.xp_to_next_level = int(p[8])
    player.fighter.unused_skill_points = int(p[9])


def load_level(level, game=None):
    level = string.split(level, END_OF_MAP)
    objects = level[1]
    misc = string.split(objects, END_OF_MISC)
    items = string.split(misc[1], END_OF_ITEMS)
    monsters = string.split(items[1], END_OF_MONSTERS)
    misc = string.split(misc[0], END_MISC)
    items = string.split(items[0], END_ITEM)
    monsters = string.split(monsters[0], END_MONSTER)

    mapp = string.split(level[0], MAP_PADDING)
    depth = int(mapp.pop(0))
    #build fov maps

    misc_obs = []
    if len(misc) > 1:
        misc.pop(len(misc)-1)
        for m in misc:
            misc_obs.append(load_misc(Object(), m, game))
    item_obs = []
    if len(items) > 1:
        items.pop(len(items)-1)
        for item in items:
            item_obs.append(load_item(Object(), item, game))
    mon_obs = []
    if len(monsters) > 1:
        monsters.pop(len(monsters)-1)  # pop out the last, empty object
        for monster in monsters:
            mon_obs.append(load_monster(Object(), monster, game))  # return monster, then build from name and assign position
            # add monster to objects for this level
    if game:
        if MAP:
            level = MAP.Level()
            level.map, level.spawn_nodes = load_map(mapp, game)
            level.depth = depth
            level.objects = []
            for item in item_obs:
                level.objects.append(item)
            for item in mon_obs:
                level.objects.append(item)
            for item in misc_obs:
                level.objects.append(item)
            return level
    load_map(mapp)


def load_monster(monster, m, game):
    m = string.split(m, PADDING)
    monster.name = m[0]
    monster.x = int(m[1])
    monster.y = int(m[2])
    monster.hp = int(m[3])
    monster.max_hp = int(m[4])
    m = game.build_objects.create_monster(game, monster.x, monster.y, mob_name=monster.name)
    m.fighter.hp = monster.hp
    return m


def load_map(mapp, game=None):
    if not game:
        return
    i = 0
    m = []
    for item in mapp:
        if item == '':
            m.append(259)
            pass
        else:
            m.append(int(item))
        i += 1
    return game.Map.build_bitmask_map(m, game), game.Map.return_spawn_nodes()


def load_misc(misc, m, game):
    m = string.split(m, PADDING)
    misc.name = m[0]
    misc.x = int(m[1])
    misc.y = int(m[2])
    if misc.name == 'set of stairs going up':
        m = MISC.Misc(type='up')
        return OBJECT.Object(game.con, misc.x, misc.y, '<', misc.name, libtcod.white, blocks=False, misc=m)
    elif misc.name == 'set of stairs going down':
        m = MISC.Misc(type='down')
        return OBJECT.Object(game.con, misc.x, misc.y, '>', misc.name, libtcod.white, blocks=False, misc=m)


def load_item(item, i, game=None):
    i = string.split(i, PADDING)
    item.name = i[0]
    if i[1] == 'None':
        item.x = None
    else:
        item.x = int(i[1])
    if i[2] == 'None':
        item.x = None
    else:
        item.y = int(i[2])
    #add a case for each type of item
    if 'potion of ' in item.name:
        item.name = string.split(item.name, 'potion of ')
        item.name = item.name[1]
        if game:
            it = game.build_objects.build_potion(game, item.x, item.y, item.name)
            it.item.qty = int(i[3])
            return it
    elif 'scroll of ' in item.name:
        item.name = string.split(item.name, 'scroll of ')
        item.name = item.name[1]
        if game:
            it = game.build_objects.build_scroll(game, item.x, item.y, item.name)
            it.item.qty = int(i[3])
            return it
    elif ' gold' in item.name:
        pass
    else:
        for equip in game.build_objects.equipment:
            if equip.name in item.name:
                n = equip.name
                m = string.split(item.name, n)
                m = string.rstrip(m[0])
                equipment = game.build_objects.build_equipment(game, item.x, item.y, type=equip.type, name=n, mat=m)
                return equipment
        pass


def get_next_object(start, file):
    file.seek(start)
    t = ''
    while True:
        t += file.read(1)
        if PADDING in t:
            t = t.rstrip(PADDING)
            return t, file.tell()


if __name__ == "__main__":
    #pass
    load()