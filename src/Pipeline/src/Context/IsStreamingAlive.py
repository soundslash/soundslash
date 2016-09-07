#!/usr/bin/env python

"""
"""

from pydispatch import dispatcher
import time
from bson.objectid import ObjectId
from bson import SON
from mongokit import *
from bson.objectid import ObjectId
import pygst
pygst.require("0.10")
import gst

from Framework.Base import *
from Model.Streaming.Scheduler import Scheduler
from Model.Streaming.EncodedStreamer import EncodedStreamer
from Model.Streaming.EncodedScheduler import EncodedScheduler
from Context.SelectStreamingServer import SelectStreamingServer
from Model.Usecase import Usecase
from Model.Usecase import send
from Model.Db import Db
from Context.StopStreaming import StopStreaming

__author__ = "Michal Bystricky"
__copyright__ = "Copyright 2013, Michal Bystricky"
__status__ = "Prototype"

class IsStreamingAlive(Base):

    def __init__(self, stream_manager, stream_id, streamer):
        super(IsStreamingAlive, self).__init__()

        self.stream_manager = stream_manager
        self.stream_id = stream_id
        self.streamer = streamer


    @asynchronous
    def run(self, respond):

        stream_obj = yield task(self.query, self.db.streams.find_one,
                                {"_id": ObjectId(self.stream_id)}, {"_id": 0, "reencoding": 1})
        # print('!!!!', stream_obj)
        if stream_obj["reencoding"]:

            pipe = self.streamer.pipe
            success, state, pending = pipe.get_state(1)
            result = {}
            if state == gst.STATE_PLAYING:
                result["is_alive"] = "hell_yeah"
            else:
                result["is_alive"] = "no"
                result = yield task(self.call, StopStreaming(self.stream_manager, self.stream_id, streamer=self.streamer).run)

            respond(result)
        else:
            # print('!!!! NO REENC')
            respond({
                "is_alive": "hell_yeah"
            })
