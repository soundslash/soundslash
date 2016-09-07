#!/usr/bin/env python

"""
StreamSaver class is GStreamer class to create element that redirects data to database.
"""

import pygst
pygst.require("0.10")
import gst
import gobject
gobject.threads_init()

from Framework.Base import *

__author__ = "Michal Bystricky"
__copyright__ = "Copyright 2013, Michal Bystricky"
__credits__ = ["Michal Bystricky", "Samuel Stehlik"]
__status__ = "Prototype"

class CapsRemover(gst.Element):

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

    def __init__(self, *args, **kwargs):
    #initialise parent class
        gst.Element.__init__(self, *args, **kwargs)

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
        # buf.set_caps(gst.caps_new_any())
        return self.srcpad.push(gst.Buffer(str(buf)))

gobject.type_register(CapsRemover)
