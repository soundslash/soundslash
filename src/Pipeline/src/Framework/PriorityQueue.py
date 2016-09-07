#!/usr/bin/env python

"""
Priority queue wrap Queue.PriorityQueue in order to provide easy access.
"""

# Python 3 import queue
import Queue
import sys
import struct
import time
import datetime
from noconflict import classmaker

from Framework.Singleton import Singleton

__author__ = "Michal Bystricky"
__copyright__ = "Copyright 2013, Michal Bystricky"
__status__ = "Prototype"

class PriorityQueue(Singleton):

    __metaclass__=classmaker()

    def __init__(self):
        self.default_priority = int(2 ** (struct.Struct('i').size * 8 - 1) - 1)
        self.queue = Queue.PriorityQueue()
        PriorityQueue.queue = self

    def put_with_priority(self, priority, value):
        self.queue.put([priority, value])

    def put(self, value):
        # now = datetime.datetime.now()
        # self.default_value = int(time.mktime(now.timetuple())*1e3 + now.microsecond/1e3 * 1000)
        self.queue.put([self.default_priority, value])

    def get(self):
        try:
            priority, value = self.queue.get(True)
        except Queue.Empty:
            priority, value = None, None
        return value
