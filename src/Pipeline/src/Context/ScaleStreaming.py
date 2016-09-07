#!/usr/bin/env python

"""
"""

from pydispatch import dispatcher
import time
from bson.objectid import ObjectId
from bson import SON
from mongokit import *
from bson.objectid import ObjectId

from Framework.Base import *
from Model.Streaming.Scheduler import Scheduler
from Model.Streaming.EncodedStreamer import EncodedStreamer
from Model.Streaming.EncodedScheduler import EncodedScheduler
from Context.SelectStreamingServer import SelectStreamingServer
from Model.Usecase import Usecase
from Model.Usecase import send
from Model.Db import Db

__author__ = "Michal Bystricky"
__copyright__ = "Copyright 2013, Michal Bystricky"
__status__ = "Prototype"

class ScaleStreaming(Base):

    def __init__(self, stream_id, quality, streamer):
        super(ScaleStreaming, self).__init__()

        self.stream_id = stream_id
        self.quality = quality
        self.streamer = streamer


    @asynchronous
    def run(self, respond):

        stream_obj = yield task(self.query, self.db.streams.find_one,
                                {"_id": ObjectId(self.stream_id)}, {"_id": 0, "user_id": 1})

        server = yield task(self.call, SelectStreamingServer(stream_obj["user_id"],
                                                             self.stream_id, quality=self.quality).run)

        if "error" in server:
            result = server
        else:
            result = self.streamer.scale(server["db_obj"], quality = self.quality)

        respond(result)
