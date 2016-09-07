#!/usr/bin/env python

"""
This is a single stream of music. It will get mixed into the AudioPlayer's adder when
the song starts and removed after the song has ended.
"""

import pygst
pygst.require("0.10")
import gst
import gobject
gobject.threads_init()
from noconflict import classmaker

from Framework.Base import *
from Model.Usecase import send
from Model.Streaming.CapsRemover import CapsRemover

__author__ = "Michal Bystricky"
__copyright__ = "Copyright 2013, Michal Bystricky"
__credits__ = ["Michal Bystricky", "Samuel Stehlik"]
__status__ = "Prototype"

class EncodeBin(Base, gst.Bin):

    __metaclass__=classmaker()

    def __init__(self, player, quality):
        gst.Bin.__init__(self)
        self.__player = player
        self.quality = quality

        self.audioconvert = gst.element_factory_make("audioconvert")

        # threads
        queue = gst.element_factory_make("queue")

        self.vorbisenc = gst.element_factory_make("vorbisenc")
        self.vorbisenc.set_property("quality", self.quality)

        self.vorbisparse = gst.element_factory_make('vorbisparse')

        self.add(queue, self.audioconvert, self.vorbisenc, self.vorbisparse)

        sink = queue.get_pad("sink")
        self.sink = gst.GhostPad("sink", sink)
        self.add_pad(self.sink)

        gst.element_link_many(queue, self.audioconvert, self.vorbisenc, self.vorbisparse)

        src = self.vorbisparse.get_pad("src")
        self.src = gst.GhostPad("src", src)
        self.add_pad(self.src)

        self.__player.pipe.add(self)
