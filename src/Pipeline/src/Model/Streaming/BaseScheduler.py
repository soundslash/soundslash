#!/usr/bin/env python

"""
Channel class handling streams (StreamBin, sources ...).
"""

import time
import pygst
pygst.require("0.10")
import gst
import logging
from scikits.audiolab import Sndfile
from bson.objectid import ObjectId
import random, time
from mongokit import *
from multiprocessing.synchronize import BoundedSemaphore

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

__author__ = "Michal Bystricky"
__copyright__ = "Copyright 2013, Michal Bystricky"
__credits__ = ["Michal Bystricky", "Samuel Stehlik"]
__status__ = "Prototype"


class UpdateObservers(Base):

    def __init__(self):
        super(UpdateObservers, self).__init__()
        self.observers = []


    def register(self, observer):
        self.observers.append(observer)

    def unregister(self, observer):
        try:
            self.observers.remove(observer)
        except:
            pass


    @asynchronous
    def notify(self, message, respond):
        for observer in self.observers:
            if observer is not None:
                observer.write_message(message)
        respond(None)

    def length(self):
        return len(self.observers)



class BaseScheduler(Base):

    @asynchronous
    def init(self, player, respond=None):
        super(BaseScheduler, self).__init__()

        self.playing = True
        self.player = player
        self.last_artist = None
        self.last_stop_unused = time.time()

        self.observers = UpdateObservers()

        # db = Db()
        # self.db = db

        self.tracks_selector = TracksSelector(self.player.stream["_id"])
        self.history = History(observers=self.observers)
        self.program_id = unicode(self.player.stream["default_program_id"])

        self.groups = yield task(self.call, self.get_default_group_ids, program_id=self.program_id)

        self.fade = yield task(self.call, self.get_fade_length, program_id=self.program_id)

        self.playlist_lock = BoundedSemaphore(value=1)
        self.playlist_lock.acquire()
        selection = yield task(self.call, self.get_selection, program_id=self.program_id)

        if selection  == "shuffle":
            tracks = yield task(self.call, self.tracks_selector.select_by_groups, groups=self.groups, sorted=False)
            print tracks
            self.playlist = RandomPlaylist(tracks, observers=self.observers)
            self.playlist.apply_history(self.history)
        else:
            tracks = yield task(self.call, self.tracks_selector.select_by_groups, groups=self.groups, sorted=True)
            self.playlist = Playlist(tracks, observers=self.observers)

        self.buffer = Buffer(self.player.stream["_id"], self.history, self.playlist, observers=self.observers)

        self.playlist_lock.release()


        track = self.buffer.get_track()
        file_id = track["file_id"]


        filesrc = GridFSSource(file_id)
        if self.__class__.__name__ == "EncodedScheduler":
            self.stream_bin = EncodedStreamBin(self.player, filesrc, self)
        else:
            self.stream_bin = StreamBin(self.player, filesrc, self)


        self.stream_bin.link_and_unblock()

        respond("bitch, yo!")


    @asynchronous
    def playlist_update(self, group, respond):
        if group in self.groups:

            self.playlist_lock.acquire()
            selection = yield task(self.call, self.get_selection, program_id=self.program_id)

            if selection  == "shuffle":
                tracks = yield task(self.call, self.tracks_selector.select_by_groups, groups=self.groups, sorted=False)
                self.playlist = RandomPlaylist(tracks, observers=self.observers)
                self.playlist.apply_history(self.history)
            else:
                try:
                    current_track = self.playlist.current_track
                except:
                    current_track = 0
                tracks = yield task(self.call, self.tracks_selector.select_by_groups, groups=self.groups, sorted=True)
                self.playlist = Playlist(tracks, observers=self.observers)
                self.playlist.set_current_track_if_possible(current_track)
            if hasattr(self.buffer, 'current_track_serialized'):
                current_track_serialized = self.buffer.current_track_serialized
            else:
                current_track_serialized = None
            self.buffer = Buffer(self.player.stream["_id"], self.history, self.playlist, observers=self.observers)
            if current_track_serialized is not None:
                self.buffer.current_track_serialized = current_track_serialized
            self.playlist_lock.release()

        respond({"msg": "OK"})

    @asynchronous
    def register_updates_observer(self, handler, respond):

        self.playlist_lock.acquire()
        self.observers.register(handler)
        yield task(self.call, self.buffer.notify_current_track, unblock=True)
        yield task(self.call, self.buffer.notify_buffer_update, unblock=True)
        yield task(self.call, self.history.notify_previous_update, unblock=True)
        self.playlist_lock.release()

        respond({"msg": "Registering observer", "server_time": int(time.time())})

    @asynchronous
    def unregister_updates_observer(self, handler, respond):
        self.observers.unregister(handler)
        handler = None
        respond({"msg": "Unregistering observer"})

    @asynchronous
    def update_buffer(self, buffer, respond):

        self.playlist_lock.acquire()
        tracks = yield task(self.call, self.tracks_selector.select_by_ids, ids=buffer["buffer"])
        self.buffer.update(tracks)

        yield task(self.call, self.buffer.notify_buffer_update, unblock=True)
        yield task(self.call, self.history.notify_previous_update, unblock=True)

        self.playlist_lock.release()

        respond({"msg": "OK"})

    @asynchronous
    def change_selection(self, respond):

        selection = yield task(self.call, self.get_selection, program_id=self.program_id)

        if selection == "shuffle":
            selection = "sequence"
        else:
            selection = "shuffle"

        yield task(self.query, self.db.programs.update, {  "_id": ObjectId(self.program_id) },
                                               {  "$set": {"selection": selection} })

        yield task(self.call, self.playlist_update, group=self.groups[0])
        yield task(self.call, self.buffer.notify_buffer_update, unblock=True)
        respond({"msg": "OK"})


    def next(self):
        self.__stream_eos(self.stream_bin)
        return {"msg": "OK"}

    def trigger_rescale(self):
        t = time.time()-self.last_stop_unused
        trig_mins = 5
        # 1 minute
        if t > (60*trig_mins):
            self.last_stop_unused = time.time()
            return True
        else:
            return False

    def is_stoped(self):
        return not self.playing

    @asynchronous
    def get_selection(self, program_id, respond):
        program = yield task(self.query, self.db.programs.find_one, {  "_id": ObjectId(program_id) },
                                                {  "_id": 0,  "selection": 1  })

        if program is not None and "selection" in program:
            respond(program["selection"])
        else:
            respond("sequence")


    @asynchronous
    def get_fade_length(self, program_id, respond):
        group = yield task(self.query, self.db.programs.find_one, {  "_id": ObjectId(program_id) },
                             {  "_id": 0,  "fade_in": 1,  "fade_out": 1  })

        if group is not None:
            respond(group)
        else:
            respond("sequence")

    @asynchronous
    def get_default_group_ids(self, program_id, respond):

        program = yield task(self.query, self.db.programs.find_one, {  "_id": ObjectId(program_id) },
                             {  "_id": 0,  "groups": 1  })

        respond(program["groups"])



    def print_playlist(self):

        self.buffer.show()
        self.playlist.show()

        return {"msg": "OK"}
