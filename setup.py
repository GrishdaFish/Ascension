from distutils.core import setup
import py2exe
import os,sys

includes = [
    "core",
    "libtcodpy",
    'cEngine',
    'content_parser',
    'menu',
    'spell_effects',
    'utils',
    'vector',
    'console',
    'save_system',
    'build_objects',
    'item',
    'misc',
    'object',
    'spells',
    'map',
    'gEngine',
    'game',
    ]
    
    
    
setup(name='Ascension',
    options = {"py2exe": {"includes" : includes}},
    windows  = ["core.py"])