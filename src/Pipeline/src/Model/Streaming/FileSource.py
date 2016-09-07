#!/usr/bin/env python

"""
FileSource class is GStreamer class to create file source in orde to stream a file.
"""

import pygst
pygst.require("0.10")
import gst
import time
import gobject
gobject.threads_init()
from threading import Thread

from Framework.Base import *

__author__ = "Michal Bystricky"
__copyright__ = "Copyright 2013, Michal Bystricky"
__status__ = "Prototype"

class FileSource(gst.BaseSrc):
    __gsttemplates__ = (
        gst.PadTemplate("src",
                        gst.PAD_SRC,
                        gst.PAD_ALWAYS,
                        gst.caps_new_any()),
    )

    blocksize = 4096
    fd = None

    def __init__(self):
        self.__gobject_init__()
        self.curoffset = 0
        # self.set_name(name)

    def set_property(self, name, value):
        if name == 'location':
            self.fd = open(value, 'r')

    def do_create(self, offset, size):

        if offset != self.curoffset:
            self.fd.seek(offset, 0)

        data = self.fd.read(self.blocksize)

        if data:
            self.curoffset += len(data)
            return gst.FLOW_OK, gst.Buffer(data)
        else:
            return gst.FLOW_UNEXPECTED, None

gobject.type_register(FileSource)
