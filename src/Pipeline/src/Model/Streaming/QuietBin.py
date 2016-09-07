#!/usr/bin/env python

"""
This is a single stream of music. It will get mixed into the AudioPlayer's adder when
the song starts and removed after the song has ended.
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
from Model.Streaming.QuietSource import QuietSource

__author__ = "Michal Bystricky"
__copyright__ = "Copyright 2013, Michal Bystricky"
__status__ = "Prototype"

class QuietBin(gst.Bin):

    def __init__(self, player):
        gst.Bin.__init__(self)

        self.__player = player

        source = QuietSource(self.__player.caps)
        audioconverter = gst.element_factory_make("audioconvert")
        audiofilter = gst.element_factory_make("capsfilter")
        audiofilter.set_property("caps", self.__player.caps)
        audioresample = gst.element_factory_make("audioresample")
        audiorate = gst.element_factory_make("audiorate")
        queue = gst.element_factory_make("queue")

        self.add(source, audioconverter, audioresample, audiofilter, audiorate, queue)

        logging.debug("Streamer::link_quiet_source(): Linking quiet source")
        gst.element_link_many(source, audioconverter, audioresample, audiofilter, audiorate, queue)

        src = queue.get_pad("src")
        self.src = gst.GhostPad("src", src)
        self.add_pad(self.src)

        self.__player.pipe.add(self)
