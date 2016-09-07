#!/usr/bin/env python

"""
Usecase class represent usecase base class. It is adding capability to send and receive signal.
"""

from threading import Thread
import logging
from pydispatch import dispatcher
from Framework.PriorityQueue import PriorityQueue

__author__ = "Michal Bystricky"
__copyright__ = "Copyright 2013, Michal Bystricky"
__credits__ = ["Michal Bystricky", "Samuel Stehlik"]
__status__ = "Prototype"

class Usecase(object):

    def __init__(self):
        pass

    def send(self, signal):
        if not 'sender' in signal:
            signal['sender'] = self
        # print(signal['sender'], ": sending signal ", signal['signal'])
        PriorityQueue.queue.put(signal)

    def connect(self, handler, signal, sender=dispatcher.Any, weak=False):
        dispatcher.connect(receiver=handler, signal=signal, sender=sender, weak=weak)


    @property
    def result(self):

        logging.debug(unicode(self.__class__.__name__)+" response: "+str(self.response))
        return self.response

def send(signal):
    if not 'sender' in signal:
        signal['sender'] = "Unknown"
    # print(signal['sender'], ": sending signal ", signal['signal'])
    PriorityQueue.queue.put(signal)
