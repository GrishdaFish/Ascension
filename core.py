import libtcodpy as libtcod
import sys
import os
sys.path.append(os.path.join(sys.path[0],'game'))
from game.game import *
sys.path.append(os.path.join(sys.path[0],'utils'))
from utils.content_parser import *
import utils.utils as utils

if __name__ == "__main__":
    logger = utils.log_manager()
    logger.log.info('Initializing Logger.')

    ##load up all game assets
    content = []
    #for py2exe, cant create a path in the libray.zip file
    path = os.path.join(sys.path[0],'content')
    #path = path.replace('library.zip','')
    path = path.replace('core.exe','')
    p = ContentParser(logger)
    monsters = p.run(os.path.join(path,'actors','monsters.txt'))
    content.append(monsters)

    p = ContentParser(logger)
    equipment = p.run(os.path.join(path,'items','equipment.txt'))
    content.append(equipment)

    p = ContentParser(logger)
    consumables = p.run(os.path.join(path,'items','consumables.txt'))
    content.append(consumables)

    p = ContentParser(logger)
    materials = p.run(os.path.join(path,'items','materials.txt'))
    content.append(materials)

    p = ContentParser(logger)
    path = os.path.join(sys.path[0])
    path = path.replace('core.exe','')
    game_options = p.run(os.path.join(path,'options.txt'))

    for i in xrange(1,len(game_options)):
        if game_options[0].key_set == game_options[i].set_name:
            key_set = game_options[i]
            break
            
    ##start game
    game = Game(content,logger,key_set)
    game.main_menu()
#'''
