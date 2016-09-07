#!/usr/bin/env python

"""
Media class. Data structure to select tracks to playlist.
"""

from mongokit import *
import datetime
import random
from collections import OrderedDict
from Queue import Queue
import time
from multiprocessing.synchronize import BoundedSemaphore

from Model.BaseThreaded import BaseThreaded

__author__ = "Michal Bystricky"
__copyright__ = "Copyright 2013, Michal Bystricky"
__credits__ = ["Michal Bystricky", "Samuel Stehlik"]
__status__ = "Prototype"

class Media(Document):

    __collection__ = 'media'
    __database__ = 'pipeline'

    structure = {
                  "stream_id" : basestring,
                  "artist" : basestring,
                  "user_id" : basestring,
                  "original_filename" : basestring,
                  "tags" : { },
                  "title" : basestring,
                  "size" : int,
                  "file_id" : basestring,
                  "played": int,
                  "random": float,
                  "groups":[
                      {
                          "id": basestring,
                          "weight": int
                      }
                  ]}
