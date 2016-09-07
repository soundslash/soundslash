#!/usr/bin/env python

"""
Group class.
"""

from mongokit import *
import datetime

__author__ = "Michal Bystricky"
__copyright__ = "Copyright 2013, Michal Bystricky"
__credits__ = ["Michal Bystricky", "Samuel Stehlik"]
__status__ = "Prototype"

class Group(Document):

    __collection__ = 'groups'
    __database__ = 'pipeline'

    structure = {
        "stream_id": [basestring],
        "user_id": [basestring],
        }
