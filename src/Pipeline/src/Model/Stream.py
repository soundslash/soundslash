#!/usr/bin/env python

"""
Stream class.
"""

from mongokit import *
import datetime

__author__ = "Michal Bystricky"
__copyright__ = "Copyright 2013, Michal Bystricky"
__credits__ = ["Michal Bystricky", "Samuel Stehlik"]
__status__ = "Prototype"

class Stream(Document):

    __collection__ = 'streams'
    __database__ = 'pipeline'

    structure = {
        "genres": [basestring],
        "images": [{
            "data": basestring,
            "filename": basestring
        }],
        "size": int,
        "max_size": int,
        "name": basestring,
        "reencoding": bool,
        "status": basestring,
        "user_id": basestring,
        "default_program_id": basestring
    }

    default_values = {
        "genres": [],
        "images": [],
        "size": 0,
        "max_size": 50000000,
        "name": None,
        "reencoding": False,
        "status": "ready",
        "user_id": None,
        }
