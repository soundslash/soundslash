#!/usr/bin/env python

"""
Worker class, wait for event and dispatch it.
"""

from threading import Thread
from pydispatch import dispatcher
import time
import logging

__author__ = "Michal Bystricky"
__copyright__ = "Copyright 2013, Michal Bystricky"
__status__ = "Prototype"



class Worker(Thread):
    def __init__(self, queue):
        Thread.__init__(self)
        self.queue = queue
        self.stop = False

    def run(self):
        while not self.stop:
            i = self.queue.get()
            # print i["sender"]
            logging.getLogger('system').debug(self.id+" dispatching message "+str(i["signal"])+" from "+str(i["sender"].id))
            if i is not None:
                dispatcher.send(**i)
            # time.sleep(0.1)
            # print "a"

    @property
    def id(self):
        return self.__class__.__name__+"_"+str(id(self))
