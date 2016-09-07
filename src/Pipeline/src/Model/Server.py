#!/usr/bin/env python

"""
Streamingserver class.
"""

from mongokit import *
import datetime

__author__ = "Michal Bystricky"
__copyright__ = "Copyright 2013, Michal Bystricky"
__credits__ = ["Michal Bystricky", "Samuel Stehlik"]
__status__ = "Prototype"

class Server(Document):

    __collection__ = 'servers'
    __database__ = 'pipeline'

    structure = {
        "type": basestring,
        "user_id": basestring,
        "streaming": {
            "caps": basestring,
            "quality": float,
            "protocol": basestring,
            "mount": basestring,
            "password": basestring,
            "max_listeners": int,
            "listeners": int,
            "streaming": bool,
            "stream": basestring
            },
        "local_ip": basestring,
        "public_ip": basestring,
        "port": int,
        "level": float,
        "created_at": datetime.datetime,
        "down": bool
    }

    default_values = {
        "type": None,
        "user_id": None,
        "streaming": {
            "caps": "audio/x-raw-int, channels=2, endianness=1234, rate=44100, width=16, depth=16, signed=true",
            "quality": float(0.4),
            "protocol": "http",
            "mount": "/example.ogg",
            "password": "hackme",
            "max_listeners": 10,
            "listeners": 0,
            "streaming": False,
            "stream": None
            },
        "local_ip": "127.0.0.1",
        "public_ip": None,
        "port": 8000,
        "level": float(0),
        "created_at": datetime.datetime.utcnow,
        "down": False,
    }
