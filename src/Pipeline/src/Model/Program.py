#!/usr/bin/env python

"""
Program class.
"""

from mongokit import *
import datetime

__author__ = "Michal Bystricky"
__copyright__ = "Copyright 2013, Michal Bystricky"
__credits__ = ["Michal Bystricky", "Samuel Stehlik"]
__status__ = "Prototype"

class Program(Document):

    __collection__ = 'programs'
    __database__ = 'pipeline'

    structure = {
        "name": basestring,
        "selection": basestring,
        "groups": [],
        "start": datetime.datetime,
        "end": datetime.datetime,
        "force_start": bool,
        "repeating": basestring,
        "jukebox": bool,
        }
