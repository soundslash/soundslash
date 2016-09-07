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
from noconflict import classmaker

from Framework.Base import *
from Model.Usecase import send
from Model.Streaming.VorbisDemuxBin import VorbisDemuxBin
from Context.NextTrack import NextTrack

__author__ = "Michal Bystricky"
__copyright__ = "Copyright 2013, Michal Bystricky"
__status__ = "Prototype"

class EncodedStreamBin(Base, gst.Bin):

    __metaclass__=classmaker()

    def __init__(self, player, source, originator):
        super(EncodedStreamBin, self).__init__()
        gst.Bin.__init__(self)

        self.__player = player
        self.__originator = originator
        # self.uri = uri
        self.source = source

        self.__demux = VorbisDemuxBin()

        self.__adder_sink = None
        self.src_blocked = False
        self.emitted_playing_message = False
        self.__decoder_linked = False
        self.__error = None
        self.__error_id = None


        self.add(self.source, self.__demux)
        gst.element_link_many(self.source, self.__demux)

        preroll_src = self.__demux.get_pad("src")
        self.src = gst.GhostPad("src", preroll_src)
        self.add_pad(self.src)

        # Add a padprobe to the src to catch the OES and other events
        self.src.add_event_probe(self.__src_event_cb)

        # Share the bus with the player
        # self.set_bus(self.__player.pipe.get_bus())

    def new_source(self, source):
        self.__player.lock.acquire()
        self.set_state(gst.STATE_NULL)
        # self.unlink_and_dispose()

        gst.element_unlink_many(self.source, self.__demux)
        self.remove(self.source)
        self.__demux.new_source()
        self.source = source
        self.add(self.source)
        gst.element_link_many(self.source, self.__demux)

        self.set_state(gst.STATE_PLAYING)
        self.__player.lock.release()



    def reset(self):
        self.__player.lock.acquire()
        self.set_state(gst.STATE_NULL)
        self.set_state(gst.STATE_PLAYING)
        self.__player.lock.release()



    def link_and_unblock(self):
        """
        This is used only at start changing source is done by new_source()
        """
        logging.debug("StreamBin::link_and_unblock(): Linking and unblocking stream")
        if self.__adder_sink: return True

        # self.__player.sink_lock.acquire()
        # self.__player.sink_start()
        # self.__player.sink_lock.release()

        if not self.get_parent():
            logging.debug("StreamBin::link_and_unblock(): Adding stream to player pipeline")
            self.__player.pipe.add(self)

        # 64 is default quality
        self.__adder_sink = self.__player.vorbisparse.get_pad("sink")
        if not self.__adder_sink:
            logging.warning("StreamBin::link_and_unblock(): Could not get adder_sink")
            return False

        try:
            self.src.link(self.__adder_sink)
            logging.debug("StreamBin::link_and_unblock(): Stream src linked to adder_sink")
        except:
            self.__adder_sink = None
            logging.warning("StreamBin::link_and_unblock(): Could not link with adder_sink")
            return False

        logging.debug("StreamBin::link_and_unblock(): Unblocking src")
        self.src.set_blocked_async(False, self.__src_unblocked_cb_null)

        # self.set_state(gst.STATE_PLAYING)
        # self.__player.pipe.set_state(gst.STATE_PLAYING)

        return True

    def unlink_and_dispose(self):
        logging.debug("StreamBin::unlink_and_dispose(): Unlinking and disposing stream")

        sr = self.set_state(gst.STATE_NULL)
        if sr == gst.STATE_CHANGE_ASYNC:
            logging.debug("StreamBin::unlink_and_dispose(): Setting stream to STATE_NULL in async")
            self.get_state(gst.CLOCK_TIME_NONE)
        logging.debug("StreamBin::unlink_and_dispose(): STATE_NULL set")

        if self.__adder_sink:
            self.src.unlink(self.__adder_sink)
            # self.__adder_sink.get_parent().release_request_pad(self.__adder_sink)
            self.__adder_sink = None
        logging.debug("StreamBin::unlink_and_dispose(): Unlinked")

        if self.get_parent() and self.get_parent() == self.__player.pipe:
            self.__player.pipe.remove(self)
        logging.debug("StreamBin::unlink_and_dispose(): Removed from pipeline")

        # self.__player.pipe.set_state(gst.STATE_PLAYING)

        # logging.debug("StreamBin::unlink_and_dispose(): Acquiring streams lock")
        # self.__player.streams_lock.acquire()
        # self.__player.streams.remove(self)
        # self.__player.streams_lock.release()
        # logging.debug("StreamBin::unlink_and_dispose(): Streams lock released. Removed from streams list.")

    def __new_decodebin_pad_cb(self, dbin, pad, islast):
        pad.link(self.__audioconvert.get_pad("sink"))
        self.__decoder_linked = True

    def __src_blocked_cb(self, pad, blocked):
        self.__preroll.set_property("min-threshold-buffers", 0)
        # self.start()

    def __src_unblocked_cb_null(self, pad, blocked):
        pass

    @asynchronous
    def __src_event_cb(self, pad, event):
        if event.type == gst.EVENT_EOS:
            result = yield task(self.call, NextTrack(streamer=self.__player).run, unblock=True)


    def destruct(self):
        """
        This has to be called from another thread.
        """
        logging.debug("StreamBin::destruct(): Destructing stream")
        self.unlink_and_dispose()
