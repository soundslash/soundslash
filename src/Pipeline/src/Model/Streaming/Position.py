#!/usr/bin/env python

"""

"""

import pygst
pygst.require("0.10")
import gst
import time
import gobject
gobject.threads_init()
import analyse
import numpy
import StringIO
from threading import Thread

from Framework.Base import *
from Framework.Application import Application

__author__ = "Michal Bystricky"
__copyright__ = "Copyright 2013, Michal Bystricky"
__status__ = "Prototype"

class Position(gst.Element):

    #source pad (template): we send buffers forward through here
    _srctemplate = gst.PadTemplate ('src',
                                    gst.PAD_SRC,
                                    gst.PAD_ALWAYS,
                                    gst.caps_new_any())

    #sink pad (template): we recieve buffers from our sink pad
    _sinktemplate = gst.PadTemplate ('sink',
                                     gst.PAD_SINK,
                                     gst.PAD_ALWAYS,
                                     gst.caps_new_any())

    #register our pad templates
    __gsttemplates__ = (_srctemplate, _sinktemplate)

    def __init__(self, player):
    #initialise parent class
        gst.Element.__init__(self)

        self.player = player

        self.position = 0
        self.time_position = 0
        self.start_time = 0

        self.on_position_arr = []

        #source pad, outgoing data
        self.srcpad = gst.Pad(self._srctemplate)

        #sink pad, incoming data
        self.sinkpad = gst.Pad(self._sinktemplate)
        self.sinkpad.set_setcaps_function(self._sink_setcaps)
        self.sinkpad.set_chain_function(self._sink_chain)

        #make pads available
        self.add_pad(self.srcpad)
        self.add_pad(self.sinkpad)

    def on_position(self, position, callback):
        self.on_position_arr.append({
            'position': position,
            'callback': callback
        })

    def _sink_setcaps(self, pad, caps):
        #we negotiate our capabilities here, this function is called
        #as autovideosink accepts anything, we just say yes we can handle the
        #incoming data
        return True


    def _sink_chain(self, pad, buf):

        #this is where we do filtering
        #and then push a buffer to the next element, returning a value saying
        # it was either successful or not.

        # if self.start_time == 0: self.start_time = long(time.time()*gst.SECOND) + buf.duration
        # self.time_position = long(((time.time()*gst.SECOND) - self.start_time)) + buf.duration

        self.position = buf.timestamp
        if self.on_position_arr:
            for on in list(self.on_position_arr):
                if long(on['position']) <= self.position:
                    d = {
                        "signal": "stream_eos_finish_"+unicode(self.player['_id'])
                    }

                    d.update(on['callback']['args'])
                    del d['respond']
                    try:
                        Base().send(d, callback=on['callback']['args']['respond'], unblock=False)

                    except Exception as e:
                        print(e)

                    print('a')

                    self.on_position_arr.remove(on)

        return self.srcpad.push(buf)

gobject.type_register(Position)
