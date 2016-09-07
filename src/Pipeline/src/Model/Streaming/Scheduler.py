#!/usr/bin/env python

"""
Channel class handling streams (StreamBin, sources ...).
"""

import time
import pygst
pygst.require("0.10")
import gst
import logging
from multiprocessing.synchronize import BoundedSemaphore
from bson.objectid import ObjectId
from threading import Thread
import functools
import threading

from Framework.Base import *
from Model.BaseThreaded import BaseThreaded
from Model.Streaming.StreamBin import StreamBin
from Model.Streaming.EncodedStreamBin import EncodedStreamBin
from Model.Streaming.GridFSSource import GridFSSource
from Model.Stream import Stream
from Model.Media import Media
from Model.Streaming.Playlist import Buffer
from Model.Streaming.Playlist import RandomPlaylist
from Model.Streaming.Playlist import Playlist
from Model.Streaming.Playlist import History
from Model.Streaming.TracksSelector import TracksSelector
from Model.Db import Db
from Model.Streaming.BaseScheduler import BaseScheduler


__author__ = "Michal Bystricky"
__copyright__ = "Copyright 2013, Michal Bystricky"
__status__ = "Prototype"

class Scheduler(BaseScheduler):

    def __init__(self, player):
        super(Scheduler, self).__init__()
        self.encoded = False
        self.live_bins = []
        stream_id = unicode(player.stream["_id"])
        self.connect(handler= self.stream_eos, signal= "stream_eos_"+stream_id)
        self.connect(handler= self.stop_live, signal= "stop_live_"+stream_id)
        self.connect(handler= self.stream_eos_finish, signal= "stream_eos_finish_"+stream_id)

        # VolumeDisplay(self).start()

    @in_context(["LiveStreaming"])
    def stop_live(self, appsrc, respond):
        for live_bin in self.live_bins:
            if live_bin.get_source() is appsrc:

                self.player.lock.acquire()
                live_bin.unlink_and_dispose()
                self.live_bins.remove(live_bin)
                self.player.lock.release()

                break
        if len(self.live_bins) == 0:
            self.increase_volume(1, self.stream_bin.get_postion())
        respond(None)

    @in_context(["LiveStreaming"])
    def start_live(self, appsrc, loop, respond):

        self.player.lock.acquire()
        self.decrease_volume(1)
        live_bin = StreamBin(self.player, appsrc, self, decodebin = True, nodatabinunlinker = True)
        live_bin.link_and_unblock()
        self.live_bins.append(live_bin)
        self.player.lock.release()

        respond(None)



    @in_context(["NextTrack"])
    def stream_eos(self, sender, fade_out, fade_in, respond):

        prev_vol = self.stream_bin.get_volume()
        if len(self.live_bins) == 0 and prev_vol != 0:
            end_position = self.decrease_volume(fade_out)
        else:
            if self.encoded or fade_out == 0:
                end_position = -1
            else:
                end_position = self.stream_bin.get_postion()

        if end_position == -1:
            self.stream_eos_finish(sender, fade_out, fade_in, respond)
        else:
            self.stream_bin.on_position(end_position, {
                'func': self.stream_eos_finish,
                'args': {'sender':sender, 'fade_out':fade_out, 'fade_in':fade_in, 'respond':respond}
            })

        # respond(None)

    @in_context(["NextTrack"])
    def stream_eos_finish(self, sender, fade_out, fade_in, respond):

        print(threading.current_thread())
        prev_vol = self.stream_bin.get_volume()

        if self.trigger_rescale():

            self.send({
                "signal": 'rescale',
                "stream": self.player.stream["_id"],
                "stop": False
            })

        if not sender.loop_id:


            self.playlist_lock.acquire()
            track = self.buffer.get_track()
            self.playlist_lock.release()
            file_id = track["file_id"]
            # self.__player.set_metadata(track["artist"], track["title"], track["album"])

            filesrc = GridFSSource(file_id)
        else:
            filesrc = GridFSSource(sender.get_next_in_loop())

        sender.new_source(filesrc)

        self.stream_bin.unset_volume_control()

        if len(self.live_bins) != 0 and prev_vol == 0:
            self.stream_bin.set_volume(0, 0)
        else:
            self.increase_volume(fade_in)

        respond(None)
        # callback(None)



    def decrease_volume(self, fade_out):
        if self.encoded or fade_out == 0: return -1

        # volume = kwargs["self"].stream_bin.get_volume()
        volume = 100
        final_volume = 0

        sleep = 0.01
        sleep_duration = fade_out
        position = self.stream_bin.get_postion()

        change_volume = volume-final_volume

        iterations = int(sleep_duration/sleep)
        change_iteration = float(change_volume)/float(iterations)

        for i in range(iterations):
            volume -= change_iteration
            position += sleep*gst.SECOND
            self.stream_bin.set_volume(position, volume)
            # print position, volume

        return position


    def increase_volume(self, fade_in, pos = 0):
        if self.encoded or fade_in == 0: return -1
        volume = 0
        final_volume = 100

        sleep = 0.01
        sleep_duration = fade_in

        change_volume = volume-final_volume

        iterations = int(sleep_duration/sleep)
        change_iteration = float(change_volume)/float(iterations)

        position = pos
        for i in range(iterations):
            volume -= change_iteration
            # print(volume)
            position += sleep*gst.SECOND
            self.stream_bin.set_volume(position, volume)
            print position, volume

        return position



class VolumeDisplay(Thread):

    def __init__(self, scheduler):
        super(VolumeDisplay, self).__init__()
        self.scheduler = scheduler


    def run(self):
        time.sleep(10)
        self.stream_bin = self.scheduler.stream_bin
        while True:
            time.sleep(0.1)
            print(self.stream_bin.get_volume())
