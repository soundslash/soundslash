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
import random
from mongokit import *
from multiprocessing.synchronize import BoundedSemaphore

from Framework.Base import *
from Model.BaseThreaded import BaseThreaded
# from Model.Streaming.StreamBin import StreamBin
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
__credits__ = ["Michal Bystricky", "Samuel Stehlik"]
__status__ = "Prototype"

class EncodedScheduler(BaseScheduler):

    def __init__(self, player):
        super(EncodedScheduler, self).__init__()
        self.encoded = True

        self.connect(handler= self.stream_eos, signal= "stream_eos_"+unicode(player.stream["_id"]))

    @asynchronous
    def stream_eos(self, sender, respond, fade_out=0, fade_in=0):

        if self.trigger_rescale():
            if self.observers.length() == 0:
                stop = True
            else:
                stop = False
            self.send({
                    "signal": 'rescale',
                    "stream": self.player.stream["_id"],
                    "stop": stop
            })

        track = self.buffer.get_track()
        file_id = track["file_id"]

        filesrc = GridFSSource(file_id)
        sender.new_source(filesrc)

        respond(None)
