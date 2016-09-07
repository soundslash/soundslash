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
from noconflict import classmaker

from Framework.Base import *
from Model.Streaming.Loudness import Loudness
from Model.Streaming.VorbisDecodeBin import VorbisDecodeBin
from Context.NextTrack import NextTrack
from Model.Streaming.NoDataBinUnlinker import NoDataBinUnlinker
from Model.Streaming.Position import Position
from Model.Streaming.GridFSSource import GridFSSource

__author__ = "Michal Bystricky"
__copyright__ = "Copyright 2013, Michal Bystricky"
__status__ = "Prototype"


class StreamBin(Base, gst.Bin):

    __metaclass__=classmaker()

    def __init__(self, player, source, originator, decodebin = False, nodatabinunlinker = False):
        super(StreamBin, self).__init__()
        gst.Bin.__init__(self)



        self.__player = player
        self.__originator = originator
        self.__source = source

        self.linked = False
        self.is_nodatabinunlinker = nodatabinunlinker
        self.state = None

        self.__adder_sink = None
        self.src_blocked = False
        self.emitted_playing_message = False
        self.__decoder_linked = False
        self.__error = None
        self.__error_id = None

        self.loop_id = None


        if decodebin:
            self.__decodebin = gst.element_factory_make("decodebin", None)
            self.__decodebin.connect("new-decoded-pad", self.__new_decodebin_pad_cb)
        else:
            self.__decodebin = VorbisDecodeBin()

        # oggdemux ! vorbisdec
        # self.__oggdemux = gst.element_factory_make("oggdemux", None)
        # self.__oggdemux.connect("pad-added", self.demuxer_callback)
        # self.__sourcequeue = gst.element_factory_make("queue", None)
        # self.__vorbisdec = gst.element_factory_make("vorbisdec", None)

        self.__audioconvert = gst.element_factory_make("audioconvert", None)
        if nodatabinunlinker:
            self.__nodatabinunlinker = NoDataBinUnlinker(unlink=self, tolerance=1)

        self.__audioresample = gst.element_factory_make("audioresample", None)
        self.__capsfilter = gst.element_factory_make("capsfilter", None)
        self.pos = Position(self.__player.stream)

        self.__volume = gst.element_factory_make("volume", None)
        self.__volume_control = gst.Controller(self.__volume, "volume")
        self.__volume_control.set_interpolation_mode("volume", gst.INTERPOLATE_LINEAR)
        # self.__loudness = Loudness(volume = self.__volume)

        self.__preroll = gst.element_factory_make("queue", None)



        self.__capsfilter.set_property("caps", self.__player.caps)
        self.__preroll.set_property("min-threshold-buffers", 10)


        self.add(self.__source, self.__decodebin, self.__audioconvert, self.__audioresample, self.__capsfilter,
                 self.pos, self.__volume, self.__preroll)
        if nodatabinunlinker:
            self.add(self.__nodatabinunlinker)
        # self.__source.link(self.__decodebin)
        # gst.element_link_many(self.__source, self.__sourcequeue, self.__oggdemux)
        if decodebin:
            gst.element_link_many(self.__source, self.__decodebin)
            if nodatabinunlinker:
                gst.element_link_many(self.__audioconvert, self.__audioresample, self.__capsfilter,
                                      self.__nodatabinunlinker, self.__preroll, self.pos, self.__volume)
            else:
                gst.element_link_many(self.__audioconvert, self.__audioresample, self.__capsfilter,
                                      self.__preroll, self.pos, self.__volume)
        else:
            if nodatabinunlinker:
                gst.element_link_many(self.__source, self.__decodebin, self.__audioconvert, self.__audioresample,
                                      self.__capsfilter, self.__nodatabinunlinker, self.__preroll, self.pos, self.__volume)
            else:
                gst.element_link_many(self.__source, self.__decodebin, self.__audioconvert, self.__audioresample,
                                      self.__capsfilter, self.__preroll, self.pos, self.__volume)

        preroll_src = self.__volume.get_pad("src")
        self.src = gst.GhostPad("src", preroll_src)
        self.add_pad(self.src)

        # Add a padprobe to the src to catch the OES and other events
        self.src.add_event_probe(self.__src_event_cb)

        # Share the bus with the player
        self.set_bus(self.__player.pipe.get_bus())

    def unset_volume_control(self):

        self.__volume_control.unset_all("volume")


    def demuxer_callback(self, demuxer, pad):
        print "DEMUX CALLBACK CALLED"
        pad.link(self.__vorbisdec.get_pad("sink"))
        self.__decoder_linked = True

    def get_next_in_loop(self):
        self.loop_ip = self.loop[(self.loop_position % len(self.loop))-1]
        self.loop_position += 1
        return self.loop_id

    def loop(self, loop):
        self.loop_position = 0
        self.loop = loop
        self.loop_id = self.get_next_in_loop()
        source = GridFSSource(self.loop_id)
        self.new_source(source)

    @asynchronous
    def stop_loop(self):
        self.loop_pos = 0
        self.loop = None
        self.loop_id = None
        if len(self.__player.scheduler.live_bins) == 0:
            result = yield task(self.call, NextTrack(
                streamer=self.__player).run, unblock=False)



    def pause(self):
        self.__player.lock.acquire()

        if self.state != "paused":
            if self.is_nodatabinunlinker:
                self.__nodatabinunlinker.datawatcher.pause()

            self.unlink_and_dispose()


            self.state = "paused"
        self.__player.lock.release()

    def play(self):
        self.__player.lock.acquire()
        # if self.state != "playing":
        #     self.link_and_unblock()
        #     if self.is_nodatabinunlinker:
        #         self.__nodatabinunlinker.datawatcher.play()
        #     self.state = "playing"
        self.__player.lock.release()

    def reset(self):
        self.set_state(gst.STATE_NULL)
        self.set_state(gst.STATE_PLAYING)


    def new_source(self, source):
        self.__player.lock.acquire()
        self.set_state(gst.STATE_NULL)
        gst.element_unlink_many(self.__source, self.__decodebin)
        self.remove(self.__source)
        self.__decodebin.new_source()
        self.__source = source
        self.add(self.__source)
        gst.element_link_many(self.__source, self.__decodebin)
        # self.__source.set_state(gst.STATE_PLAYING)
        self.set_state(gst.STATE_PLAYING)
        # self.__player.pipe.set_state(gst.STATE_PLAYING)
        self.__player.lock.release()


    def start(self):
        logging.debug("StreamBin::start(): Starting stream")
        result = self.link_and_unblock()

        return result

    def get_postion(self):
        return self.pos.position
        # return self.__player.pipe.query_position(gst.FORMAT_TIME)[0]

    def get_time_postion(self):
        return self.pos.time_position

    def on_position(self, position, callback):
        self.pos.on_position(position, callback)

    def set_volume(self, position, volume):
        #
        # pos = self.__player.pipe.query_position(gst.FORMAT_TIME)[0]-(5*gst.SECOND)
        # if pos < 0:
        #     pos = self.__player.pipe.query_position(gst.FORMAT_TIME)[0]
        # print pos
        self.__volume_control.set("volume", position, volume/100)
        # self.__volume.set_property("volume", volume/100)

    def get_volume(self):
        return float(self.__volume.get_property("volume"))*100

    def get_source(self):
        return self.__source


    def link_and_unblock(self):
        if self.linked: return
        logging.debug("StreamBin::link_and_unblock(): Linking and unblocking stream")
        if self.__adder_sink: return True

        # self.__player.sink_lock.acquire()
        # self.__player.sink_start()
        # self.__player.sink_lock.release()

        if not self.get_parent():
            logging.debug("StreamBin::link_and_unblock(): Adding stream to player pipeline")
            self.__player.pipe.add(self)

        self.__adder_sink = self.__player.adder.get_request_pad("sink%d")
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

        logging.debug("StreamBin::link_and_unblock(): Play")
        # self.src.set_blocked_async(False, self.__src_unblocked_cb_null)

        self.set_state(gst.STATE_PLAYING)
        self.__player.pipe.set_state(gst.STATE_PLAYING)

        self.linked = True
        self.state = "playing"

        return True

    # def unlink_and_dispose(self):
    #     print self.set_state(gst.STATE_NULL)
    #     print self.src.unlink(self.__adder_sink)
    #     print self.__adder_sink.get_parent().release_request_pad(self.__adder_sink)
    #     print self.__player.pipe.remove(self)
    #     print self.__player.pipe.set_state(gst.STATE_PLAYING)

    def link_and_unblock2(self):
        self.set_state(gst.STATE_NULL)
        # self.src.unlink(self.__adder_sink)
        # self.__adder_sink = self.__player.adder.get_request_pad("sink%d")
        self.src.link(self.__adder_sink)
        self.set_state(gst.STATE_PLAYING)
        self.__player.pipe.set_state(gst.STATE_PLAYING)

    def unlink_and_dispose2(self):
        self.set_state(gst.STATE_NULL)
        self.src.unlink(self.__adder_sink)
        # self.__adder_sink.get_parent().release_request_pad(self.__adder_sink)

        self.set_state(gst.STATE_PLAYING)
        self.__player.pipe.set_state(gst.STATE_PLAYING)

    def unlink_and_dispose(self):
        if not self.linked: return
        logging.debug("StreamBin::unlink_and_dispose(): Unlinking and disposing stream")

        sr = self.set_state(gst.STATE_NULL)
        if sr == gst.STATE_CHANGE_ASYNC:
            logging.debug("StreamBin::unlink_and_dispose(): Setting stream to STATE_NULL in async")
            self.get_state(gst.CLOCK_TIME_NONE)
        logging.debug("StreamBin::unlink_and_dispose(): STATE_NULL set")

        if self.__adder_sink:
            self.src.unlink(self.__adder_sink)
            self.__adder_sink.get_parent().release_request_pad(self.__adder_sink)
            self.__adder_sink = None
        logging.debug("StreamBin::unlink_and_dispose(): Unlinked")

        if self.get_parent() and self.get_parent() == self.__player.pipe:
            self.__player.pipe.remove(self)
        logging.debug("StreamBin::unlink_and_dispose(): Removed from pipeline")

        self.__player.pipe.set_state(gst.STATE_PLAYING)

        self.linked = False

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
        self.start()

    def __src_unblocked_cb_null(self, pad, blocked):
        pass

    @asynchronous
    def __src_event_cb(self, pad, event):
        if event.type == gst.EVENT_EOS:
            result = yield task(self.call, NextTrack(
                streamer=self.__player).run, unblock=True)


    def destruct(self):
        """
        This has to be called from another thread.
        """
        logging.debug("StreamBin::destruct(): Destructing stream")
        self.unlink_and_dispose()
        self.remove_many(self.__source, self.__oggdemux, self.__audioconvert, self.__audioresample, self.__capsfilter,
                         self.__preroll)
        del self.__player
        # del self.uri
        del self.__adder_sink
        del self.src_blocked
        del self.emitted_playing_message
        del self.__source
        del self.__oggdemux
        del self.__audioconvert
        del self.__audioresample
        del self.__capsfilter
        del self.__preroll
        del self.src
