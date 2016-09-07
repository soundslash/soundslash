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
from threading import RLock
from functools import partial
import logging
import random
from multiprocessing.synchronize import BoundedSemaphore
from threading import Thread

from Framework.Base import *
from Model.BaseThreaded import BaseThreaded
from Model.Streaming.FileSource import FileSource
from Model.Streaming.QuietSource import QuietSource
from Model.Streaming.EncodedScheduler import EncodedScheduler
from Model.Streaming.ScaledTailBin import ScaledTailBin
from Model.Streaming.ScaledStreamer import ScaledStreamer
from Model.Streaming.Streamer import MainLoop

__author__ = "Michal Bystricky"
__copyright__ = "Copyright 2013, Michal Bystricky"
__status__ = "Prototype"

# default_quality = 64

class EncodedStreamer(Base, Thread, ScaledStreamer):

    caps = gst.caps_from_string("audio/x-raw-int, channels=2, endianness=1234, rate=44100, width=16, depth=16, signed=true")

    def __init__(self, stream, server):
        super(EncodedStreamer, self).__init__()

        self.lock = BoundedSemaphore(value=1)

        self.mainloop_thread = MainLoop()
        self.mainloop_thread.start()

        self.stream = stream
        self.servers = {}
        self.tailbins = []
        self.playing = False

        self.streamname = stream["name"]
        self.description = stream["description"]
        self.genre = ", ".join(stream["genres"])
        # self.default_quality = default_quality

        logging.debug("Streamer::__init__(): Constructing pipeline")
        pipe = gst.Pipeline()


        # threads
        queue = gst.element_factory_make("queue")

        # tee

        # self.oggdemux = gst.element_factory_make('oggdemux')
        self.vorbisparse = gst.element_factory_make('vorbisparse')
        # self.oggdemux.connect("pad-added", partial(self.__on_dynamic_pad, link = self.vorbisparse))

        tee = gst.element_factory_make('tee')
        # self.typefind = gst.element_factory_make('typefind')
        pipe.add(self.vorbisparse, tee)
        gst.element_link_many(self.vorbisparse, tee)






        # fakesink = gst.element_factory_make("fakesink")
        # fakesink.set_property("sync", 1)
        # pipe.add(fakesink)
        # gst.element_link_many(tee, fakesink)

        self.tee = tee
        self.pipe = pipe

        # only one quality, because this is encoded (no reencoding is done)
        # self.tees = {default_quality:tee}

        logging.debug("Streamer::__init__(): Running distribute")

        self.scale(server, sync=1, init=True)

        self.queue = queue

        logging.debug("Streamer::__init__(): Running EncodedChannel")

        self.bus = pipe.get_bus()
        self.bus.add_signal_watch()
        self.bus.connect('message::state-changed', self.on_message_state_changed)
        self.bus.connect('message::eos', self.on_eos)


    def __on_dynamic_pad(self, demuxer, pad, link = None):
        self.lock.acquire()
        if pad.is_linked():
            pad.unlink(link.get_pad("sink"))
        pad.link(link.get_pad("sink"))
        self.lock.release()


    def on_message_state_changed(self, bus, message):
        if message.src != self.tee:
            return

        old_state, new_state, pending = message.parse_state_changed()

        if new_state == gst.STATE_PLAYING and not self.playing:
            self.playing = True
            self.send({
                "signal":'streamer_initialized',
                "streamer": self
            })


    def on_eos(self, bus, message):

        logging.debug("Streamer::run(): End of stream")
        self.send({
            "signal": "eos"
        })


    def run(self):

        logging.debug("Streamer::run(): Starting pipeline")

        # The MainLoop
        self.mainloop = gobject.MainLoop()


        # And off we go!
        self.pipe.set_state(gst.STATE_PLAYING)

        self.mainloop.run()
