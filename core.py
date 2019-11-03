#!/usr/bin/env pypy
import libtcodpy as libtcod
import sys
import os
sys.path.append(os.path.join(sys.path[0],'game'))
from game.game import *
sys.path.append(os.path.join(sys.path[0],'utils'))
from utils.content_parser import *
import utils.utils as utils
import cProfile
import io
import pstats

if __name__ == "__main__":
    #profiler = cProfile.Profile()
    #profiler.enable()
    logger = utils.log_manager()
    logger.log.info('Initializing Logger.')

    ##load up all game assets
    content = []
    #for py2exe, cant create a path in the libray.zip file
    path = os.path.join(sys.path[0], 'content')
    #path = path.replace('library.zip','')
    path = path.replace('core.exe', '')
    p = ContentParser(logger)
    monsters = p.run(os.path.join(path, 'actors', 'monsters.txt'))
    content.append(monsters)

    p = ContentParser(logger)
    equipment = p.run(os.path.join(path, 'items', 'equipment.txt'))
    content.append(equipment)

    p = ContentParser(logger)
    consumables = p.run(os.path.join(path, 'items', 'consumables.txt'))
    content.append(consumables)

    p = ContentParser(logger)
    materials = p.run(os.path.join(path, 'items', 'materials.txt'))
    content.append(materials)

    p = ContentParser(logger)
    path = os.path.join(sys.path[0])
    path = path.replace('core.exe', '')
    game_options = p.run(os.path.join(path, 'options.txt'))
    key_set = None
    for i in xrange(1, len(game_options)):
        if game_options[0].key_set == game_options[i].set_name:
            key_set = game_options[i]
            break
            
    ##start game
    game = Game(content, logger, key_set)
    game.main_menu()
    #profiler.disable()
    #s = io.StringIO()
    #ps = pstats.Stats(profiler, stream=s).sort_stats("cumulative")
    #ps.dump_stats("logs/profiling/profile.dump")

    # convert profiling to human readable format
    #import datetime
    #date_and_time = datetime.datetime.utcnow()

    #out_stream = open("logs/profiling/" + date_and_time.strftime("%y%m%d@%H%M") + ".profile", "w")
    #ps = pstats.Stats("logs/profiling/profile.dump", stream=out_stream)
    #ps.strip_dirs().sort_stats("cumulative").print_stats()
#'''
