#!/usr/bin/env python

"""
QuietSource class is GStreamer class to create source that generates silence. This is used to maintain persistent
connection to streaming server.
"""

import pygst
pygst.require("0.10")
import gst
import time
import gobject
gobject.threads_init()
import math, numpy, struct
from threading import Thread

from Framework.Base import *

__author__ = "Michal Bystricky"
__copyright__ = "Copyright 2013, Michal Bystricky"
__status__ = "Prototype"

class QuietSource(gst.BaseSrc):
    __gsttemplates__ = (
        gst.PadTemplate("src",
                        gst.PAD_SRC,
                        gst.PAD_ALWAYS,
                        gst.caps_new_any()),
    )

    def __init__(self, caps):
        self.__gobject_init__()
        self.caps = caps

        values = [0 for a in numpy.arange(0.0, 12*math.pi, 0.06)]
        data = struct.pack('<' + 'h'*len(values), *values)
        self.buf = gst.Buffer(data)
        caps = gst.caps_from_string('audio/x-raw-int, rate=8000, endianness=1234, channels=1, width=16, depth=16, signed=true')

        self.buf.set_caps(caps)

    def do_create(self, offset, size):
        return gst.FLOW_OK, self.buf

gobject.type_register(QuietSource)
