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
from multiprocessing.synchronize import BoundedSemaphore
from threading import Thread

from Framework.Base import *
# from Model.Scalable import Scalable
from Model.Streaming.FileSource import FileSource
from Model.Streaming.QuietSource import QuietSource
from Model.Streaming.ScaledStreamer import ScaledStreamer
from Model.Streaming.Scheduler import Scheduler
from Model.Streaming.EncodeBin import EncodeBin
from Model.Streaming.QuietBin import QuietBin
from Model.Streaming.PipeBridge import PipeBridge

__author__ = "Michal Bystricky"
__copyright__ = "Copyright 2013, Michal Bystricky"
__status__ = "Prototype"

class Streamer(Base, ScaledStreamer):

    caps = gst.caps_from_string("audio/x-raw-int, channels=2, endianness=1234, rate=44100, width=16, depth=16, signed=true")

    def link_quiet_source(self):
        """
        Link silet stream to adder. This works also with vorbisenc and oggmux.
        """
        source = QuietSource(Streamer.caps)
        audioconverter = gst.element_factory_make("audioconvert")
        audiofilter = gst.element_factory_make("capsfilter")
        audiofilter.set_property("caps", Streamer.caps)
        audioresample = gst.element_factory_make("audioresample")
        audiorate = gst.element_factory_make("audiorate")
        queue = gst.element_factory_make("queue")
        self.pipe.add(source, audioconverter, audioresample, audiofilter, audiorate, queue)

        logging.debug("Streamer::link_quiet_source(): Linking quiet source")
        gst.element_link_many(source, audioconverter, audioresample, audiofilter, audiorate, queue, self.adder)

    def __init__(self, stream):
        super(Streamer, self).__init__()

        logging.debug("Streamer::__init__(): Constructing pipeline")

        pipe = gst.Pipeline("pipeline")

        self.lock = BoundedSemaphore(value=1)

        self.mainloop_thread = MainLoop()
        self.mainloop_thread.start()

        self.stream = stream
        self.servers = {}
        self.tees = {}
        self.encodebins = {}
        self.quality_tee_srcs = {}
        self.tailbins = []
        self.playing = False
        self.streamname = stream["name"]
        self.description = stream["description"]
        self.genre = ", ".join(stream["genres"])


        # mix audio
        adder = gst.element_factory_make("adder")
        self.quality_tee = gst.element_factory_make("tee")
        # queue = gst.element_factory_make("queue")


        pipe.add(adder, self.quality_tee)
        gst.element_link_many(adder, self.quality_tee)

        self.pipe = pipe
        self.bus = pipe.get_bus()
        self.bus.add_signal_watch()
        self.bus.connect('message::state-changed', self.on_message_state_changed)
        self.bus.connect('message::eos', self.on_eos)
        self.bus.connect('message::error', self.on_error)
        self.bus.connect("message::tag", self.on_tag)
        # self.bus.connect('message', self.on_message)
        self.adder = adder

        quietbin = QuietBin(self)
        sink = self.adder.get_request_pad("sink%d")
        quietbin.get_pad("src").link(sink)

        for quality in stream["quality"]:
            # this has to be to ensure double from database work as expected and key is found
            quality = float(quality)

            # if quality == min(stream["quality"]):
            eb = EncodeBin(self, quality)

            quality_tee_src = self.quality_tee.get_request_pad("src%d")
            quality_tee_src.link(eb.get_pad("sink"))

            self.quality_tee_srcs[quality] = quality_tee_src

            tee = gst.element_factory_make("tee")
            pipe.add(tee)


            sink = tee.get_pad("sink")
            src = eb.get_pad("src")
            src.link(sink)

            self.tees[quality] = tee
            self.encodebins[quality] = eb

            if quality == min(stream["quality"]):
                self.tee = tee


            self.scale(None, quality, sync=1, init=True)



    def __on_dynamic_pad(self, demuxer, pad, link = None):
        pad.link(link.get_pad("sink"))

    # def on_message(self, bus, message):
    #
    #     print message

    def on_tag(self, bus, message):
        pass
        # if self.playing:
        #
        #     self.lock.acquire()
        #     # self.encodebins[float(1)].on_tag()
        #     # for tailbin in self.tailbins:
        #     #     tailbin.on_tag()
        #     self.lock.release()


    def set_metadata(self, artist=" ", title=" ", album=" "):
        pass
        return
        # print "setting metadata "+artist+" "+title+" "+album
        #
        # self.tags = gst.TagList()
        #
        # self.tags[gst.TAG_ARTIST] = artist
        # self.tags[gst.TAG_TITLE] = title
        # self.tags[gst.TAG_ALBUM] = album
        #
        # event = gst.event_new_tag(self.tags)
        # self.pipe.send_event(event)

    def on_error(self, bus, message):
        if message.src.get_name().startswith("shout2send"):
            # print "ON ERROR"
            self.lock.acquire()
            for server in self.servers:
                if self.servers[server].shout2send == message.src:
                    tailbin = self.servers[server]
                    server_id = unicode(tailbin.server["_id"])
                    res = tailbin.unlink_and_dispose()
                    if res:
                        del self.servers[server_id]
                    break

            self.lock.release()

    def on_message_state_changed(self, bus, message):
        old_state, new_state, pending = message.parse_state_changed()
        # print str(message.src.get_name())+": "+str(old_state)+" ---> "+str(new_state)

        if message.src != self.tees.itervalues().next():
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


class MainLoop(Base, Thread):

    def run(self):
        logging.debug("Streamer::run(): Starting pipeline")
        self.mainloop = gobject.MainLoop()
        self.mainloop.run()
        logging.debug("Streamer::run(): ENDED")
