#!/usr/bin/env python

"""
This is a single output of music. It will send the stream from tee.
"""

import pygst
pygst.require("0.10")
import gst
import time
import gobject
gobject.threads_init()
import logging
from threading import RLock, Event
from threading import Thread

from Framework.Base import *
from Model.Usecase import send
from Model.Streaming.Loudness import Loudness

__author__ = "Michal Bystricky"
__copyright__ = "Copyright 2013, Michal Bystricky"
__status__ = "Prototype"

class ScaledTailBin(gst.Bin):

    def __init__(self, player, tee, server, sync, init):
        gst.Bin.__init__(self)

        logging.debug("DistributeBin::__init__(): Initializing")

        self.__player = player
        self.server = server
        self.sync = sync
        self.init = init
        self.__tee = tee

        if server is not None:
            self.shout2send = gst.element_factory_make('shout2send')
            self.shout2send.set_property("ip",server["local_ip"])
            self.shout2send.set_property("password",server["streaming"]["password"])
            self.shout2send.set_property("mount",server["streaming"]["mount"])
            self.shout2send.set_property("sync", sync)
            self.shout2send.set_property("async", 1)
        else:
            self.shout2send = gst.element_factory_make("fakesink")
            self.shout2send.set_property("sync", sync)
            self.shout2send.set_property("async", 1)


        # buf_len = 4
        # block_size = 4096
        #
        # self.__shout2send.set_property("blocksize", block_size)
        #
        # self.__shout2send.set_property("preroll-queue-len", buf_len)

        self.__queue = gst.element_factory_make('queue')
        # self.__queue.set_property("min-threshold-buffers", 0)
        self.__preroll_event = Event()
        # self.__queue.set_property("max-size-buffers", 0)
        # self.__queue.set_property("max-size-time", 0)
        # self.__queue.set_property("max-size-bytes", block_size*buf_len)
        # self.__queue.set_property("min-threshold-bytes", block_size*buf_len)


        q = gst.element_factory_make('queue')
        # self.vorbistag = gst.element_factory_make('vorbisparse')
        self.oggmux = gst.element_factory_make('oggmux')

        self.add(self.__queue, self.oggmux, self.shout2send)

        gst.element_link_many(self.__queue, self.oggmux, self.shout2send)

        sink = self.__queue.get_pad("sink")
        self.sink = gst.GhostPad("sink", sink)
        self.add_pad(self.sink)

        # self.__player.pipe.add(self)

        # if not self.init:
        #     self.__player.pipe.set_state(gst.STATE_PLAYING)

        logging.debug("DistributeBin::__init__(): Initialization finished")
        # self.once = True


    # def on_tag(self):
    #     if self.sync == 0 and self.once:
    #         self.once = False
    #         print "ON TAG"
    #         gst.element_unlink_many(self.__queue, self.oggmux, self.shout2send)
    #
    #         self.oggmux = gst.element_factory_make('oggmux')
    #         self.add(self.oggmux)
    #
    #         gst.element_link_many(self.__queue, self.oggmux, self.shout2send)
    #         self.set_state(gst.STATE_PLAYING)
    #         self.__player.pipe.set_state(gst.STATE_PLAYING)


    def set_metadata(self, streamname, description, genre):
        if self.server is not None:
            self.shout2send.set_property("streamname", streamname)
            self.shout2send.set_property("description", description)
            self.shout2send.set_property("genre", genre)

    def link_and_unblock(self):

        logging.debug("DistributeBin::link_and_unblock(): Linking")

        if not self.get_parent():
            logging.debug("DistributeBin::link_and_unblock(): Adding stream to player pipeline")
            self.__player.pipe.add(self)

        logging.debug("DistributeBin::link_and_unblock(): Requesting pad")
        self.__tee_src = self.__tee.get_request_pad("src%d")
        if not self.__tee_src:
            logging.warning("DistributeBin::link_and_unblock(): Could not get __tee_src")
            return False

        # this caused problems in tests
        if not self.init:
            self.__tee_src.set_blocked_async(True, self.__src_blocked_cb)
            self.__preroll_event.wait()
            self.__preroll_event.clear()



        try:
            self.__tee_src.link(self.sink)
            logging.debug("StreamBin::link_and_unblock(): Stream src linked to __tee_src")
        except:
            self.__tee_src = None
            logging.warning("StreamBin::link_and_unblock(): Could not link with __tee_src")
            return False

        # self.__tee_src.set_blocked(False)


        #     self.__preroll_event.wait()
        #     self.__preroll_event.clear()

        if not self.init:
            # self.__queue.set_state(gst.STATE_PAUSED)
            # self.oggmux.set_state(gst.STATE_PAUSED)
            # self.shout2send.set_state(gst.STATE_READY)
            # sr = self.set_state(gst.STATE_PAUSED)
            # print "!!! RESULT CHANGE STATE BIN PAUSED "+str(sr)
            # # if sr == gst.STATE_CHANGE_ASYNC:
            # #     while self.get_state()[1] != gst.STATE_PAUSED:
            # #         pass

            # sr = self.set_state(gst.STATE_NULL)
            # sr = self.set_state(gst.STATE_READY)
            # print "!!! RESULT CHANGE STATE BIN "+str(sr)
            # if sr == gst.STATE_CHANGE_ASYNC:
            #     while self.get_state()[1] != gst.STATE_READY:
            #         pass
            #
            # sr = self.shout2send.set_state(gst.STATE_PAUSED)
            # print "!!! RESULT CHANGE STATE shout "+str(sr)
            sr1 = self.set_state(gst.STATE_PLAYING)
            # print "!!! RESULT CHANGE STATE BIN "+str(sr)
            # if sr == gst.STATE_CHANGE_ASYNC:
            #     while self.get_state()[1] != gst.STATE_PLAYING:
            #         pass
            #
            # sr = self.set_state(gst.STATE_PLAYING)
            # print "!!! RESULT CHANGE STATE BIN "+str(sr)
            # if sr == gst.STATE_CHANGE_ASYNC:
            #     while self.get_state()[1] != gst.STATE_PLAYING:
            #         pass
            # # if sr == gst.STATE_CHANGE_ASYNC:
            # #     sr ,state , pstate = self.get_state(gst.CLOCK_TIME_NONE)
            # #     if sr == gst.STATE_CHANGE_FAILURE:
            # #         print "FAIL FAIL FAIL FAIL FAIL FAIL FAIL FAIL FAIL FAIL FAIL FAIL FAIL "

            sr2 = self.__player.pipe.set_state(gst.STATE_PLAYING)
            # print "!!! RESULT CHANGE STATE BIN "+str(sr)
            # if sr == gst.STATE_CHANGE_ASYNC:
            #     while self.__player.pipe.get_state()[1] != gst.STATE_PLAYING:
            #         pass

            # time.sleep(1)


            self.__tee_src.set_blocked_async(False, self.__src_unblocked_cb_null)

            if sr1 == gst.STATE_CHANGE_ASYNC:
                while self.get_state()[1] != gst.STATE_PLAYING:
                    pass

            if sr2 == gst.STATE_CHANGE_ASYNC:
                while self.get_state()[1] != gst.STATE_PLAYING:
                    pass

        logging.debug("DistributeBin::link_and_unblock(): Linked")

        return True



    def __src_unblocked_cb_null(self, pad, blocked):
        logging.debug("StreamBin::__src_blocked_cb(): StreamBin.src is UNblocked")
        # self.__preroll_event.set()
        pass

    def __src_blocked_cb(self, pad, blocked):

        logging.debug("StreamBin::__src_blocked_cb(): StreamBin.src is blocked")
        self.__queue.set_property("min-threshold-buffers", 0)
        self.__preroll_event.set()



    def unlink_and_dispose(self):

        logging.debug("DistributeBin::unlink_and_dispose(): Unlinking")

        # oldstate, newstate, pending = self.__tee.get_state()
        # if newstate == gst.STATE_PLAYING:
        #     self.__tee_src.set_blocked(True)


        self.__tee_src.unlink(self.sink)
        logging.debug("DistributeBin::unlink_and_dispose(): Disposing")
        self.__tee.release_request_pad(self.__tee_src)

        logging.debug("DistributeBin::unlink_and_dispose(): Removing")

        self.set_state(gst.STATE_NULL)
        self.__player.pipe.remove(self)

        return True
