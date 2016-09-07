#!/usr/bin/env python

"""
Baset class can be used to extend object in order to send and receive messages.
"""

from threading import Thread
from pydispatch import dispatcher
from Framework.PriorityQueue import PriorityQueue

__author__ = "Michal Bystricky"
__copyright__ = "Copyright 2013, Michal Bystricky"
__credits__ = ["Michal Bystricky", "Samuel Stehlik"]
__status__ = "Prototype"

class BaseThreaded(Thread):

    def __init__(self):
        Thread.__init__(self)

    def send(self, signal):
        if not 'sender' in signal:
            signal['sender'] = self
        # print(signal['sender'], ": sending signal ", signal['signal'])
        PriorityQueue.queue.put(signal)

    def connect(self, handler, signal, sender=dispatcher.Any, weak=False):
        dispatcher.connect(receiver=handler, signal=signal, sender=sender, weak=weak)
