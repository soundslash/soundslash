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
import time
from threading import Thread

from Framework.Base import *
from Model.BaseThreaded import BaseThreaded

__author__ = "Michal Bystricky"
__copyright__ = "Copyright 2013, Michal Bystricky"
__status__ = "Prototype"

class NoDataBinUnlinker(gst.Element):

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

    def __init__(self, unlink, tolerance=1):
    #initialise parent class
        gst.Element.__init__(self)

        self.datawatcher = DataWatcher(unlink, tolerance)
        self.playing = False

        #source pad, outgoing data
        self.srcpad = gst.Pad(self._srctemplate)

        #sink pad, incoming data
        self.sinkpad = gst.Pad(self._sinktemplate)
        self.sinkpad.set_setcaps_function(self._sink_setcaps)
        self.sinkpad.set_chain_function(self._sink_chain)

        #make pads available
        self.add_pad(self.srcpad)
        self.add_pad(self.sinkpad)

    def _sink_setcaps(self, pad, caps):
        #we negotiate our capabilities here, this function is called
        #as autovideosink accepts anything, we just say yes we can handle the
        #incoming data
        return True

    def _sink_chain(self, pad, buf):
        #this is where we do filtering
        #and then push a buffer to the next element, returning a value saying
        # it was either successful or not.
        if not self.playing:
            self.playing = True
            self.datawatcher.start()

        secs = float(buf.duration) / gst.SECOND

        # print "NEW BUFFER "+str(secs)

        if (len(buf)>0):
            self.datawatcher.touch(secs)



        return self.srcpad.push(buf)

class DataWatcher(BaseThreaded):
    def __init__(self, unlink, tolerance):
        super(DataWatcher, self).__init__()
        self.unlink = unlink
        self.tolerance = tolerance
        self.last_buffer = time.time()
        self.paused = False

    def touch(self, add_time):
        self.last_buffer += add_time

    def pause(self):
        self.paused = True

    def play(self):
        self.last_buffer = time.time()
        self.paused = False

    def run(self):
        while time.time()-self.last_buffer <= self.tolerance:
            # print "FROM LAST BUFFER "+str(time.time()-self.last_buffer)
            time.sleep(0.2)
            if self.paused:
                while self.paused:
                    time.sleep(0.2)
        self.unlink.unlink_and_dispose()
        del self.unlink


gobject.type_register(NoDataBinUnlinker)
