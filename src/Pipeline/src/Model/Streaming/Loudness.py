#!/usr/bin/env python

"""
Analyze data and change volume according to loudness.
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

__author__ = "Michal Bystricky"
__copyright__ = "Copyright 2013, Michal Bystricky"
__status__ = "Prototype"

class Loudness(gst.Element):

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

    def __init__(self, volume):
    #initialise parent class
        gst.Element.__init__(self)

        self.__volume = volume
        self.queue = []
        self.lvls = {}
        self.lvls["last_lvl"] = [time.time(), 0, 100]

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


        samps = numpy.fromstring(buf, dtype=numpy.int16)
        # Show the volume and pitch
        # -40 - 0
        # -1 very loud
        # -36 silence
        volume = analyse.loudness(samps)
            # , analyse.musical_detect_pitch(samps)
        if volume < -40:
            volume = -40

        volume = (volume + 40) * 2.5




        if len(self.queue) < 20:
            self.queue.append(volume)
        else:
            sum = 0
            count = 0
            for elem in self.queue:
                sum += elem
                count += 1
            avg = sum/count

            lvl = 0

            if avg > 70:
                avg -= 30
                lvl = 1
            elif avg < 10:
                avg = 0
                lvl = 2
            elif avg < 20:
                avg += 340
                lvl = 3
            elif avg < 40:
                avg += 230
                lvl = 4

            if lvl == 0:
                avg = 100

            # 0 volume, force new level
            if (self.lvls["last_lvl"][1] == 2):
                self.lvls["last_lvl"] = [time.time(), lvl, avg]

            if (time.time() - self.lvls["last_lvl"][0] > 2 and self.lvls["last_lvl"][1] != lvl):
                self.lvls["last_lvl"] = [time.time(), lvl, avg]
            else:
                avg = self.lvls["last_lvl"][2]


            if (self.lvls["last_lvl"][1] == lvl):
                self.lvls["last_lvl"][0] = time.time()


            print avg
            self.__volume.set_property("volume", (avg)/100)
            self.queue = self.queue[1:]
            self.queue.append(volume)

        return self.srcpad.push(buf)

gobject.type_register(Loudness)
