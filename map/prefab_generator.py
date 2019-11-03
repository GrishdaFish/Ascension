__author__ = 'Grishnak'
from utils import xp_loader
import gzip
import os
import sys


def load_prefab(file):
    f = gzip.open(file)
    data = f.read()
    f.close()
    return xp_loader.load_xp_string(data)

