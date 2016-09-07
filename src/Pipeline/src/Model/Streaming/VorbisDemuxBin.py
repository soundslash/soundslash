#!/usr/bin/env python

"""

"""

import pygst
pygst.require("0.10")
import gst
import time
import gobject
gobject.threads_init()
import logging
from threading import Thread

from Framework.Base import *
from Model.Usecase import send
from Model.Streaming.CapsRemover import CapsRemover

__author__ = "Michal Bystricky"
__copyright__ = "Copyright 2013, Michal Bystricky"
__status__ = "Prototype"

class VorbisDemuxBin(gst.Bin):

    def __init__(self):
        gst.Bin.__init__(self)

        self.oggdemux = gst.element_factory_make("oggdemux", None)
        self.oggdemux.connect("pad-added", self.oggdemux_callback)
        self.sourcequeue = gst.element_factory_make("queue", None)
        # vorbisdec = gst.element_factory_make("vorbisdec", None)

        self.add(self.oggdemux, self.sourcequeue)

        sink = self.oggdemux.get_pad("sink")
        self.sink = gst.GhostPad("sink", sink)
        self.add_pad(self.sink)

        # gst.element_link_many(self.sourcequeue, vorbisdec)

        src = self.sourcequeue.get_pad("src")
        self.src = gst.GhostPad("src", src)
        self.add_pad(self.src)

    def new_source(self):
        self.oggdemux.unlink(self.sourcequeue)
        self.remove_pad(self.sink)
        self.remove(self.oggdemux)
        del self.oggdemux

        self.oggdemux = gst.element_factory_make("oggdemux", None)
        self.oggdemux.connect("pad-added", self.oggdemux_callback)
        self.add(self.oggdemux)

        sink = self.oggdemux.get_pad("sink")
        self.sink = gst.GhostPad("sink", sink)
        self.add_pad(self.sink)

    def oggdemux_callback(self, oggdemux, pad):
        sink = self.sourcequeue.get_pad("sink")
        pad.link(sink)
