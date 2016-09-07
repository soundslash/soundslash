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

class RescaleStreaming(Base):

    def __init__(self, stream_id, streamer, stop, stream_servers):
        super(RescaleStreaming, self).__init__()

        self.stream_id = stream_id
        self.streamer = streamer
        self.stop = stop
        self.stream_servers = stream_servers


    @asynchronous
    def run(self, respond):

        servers_cursor = yield task(self.query, self.db.servers.find,
                                {"streaming.stream": self.stream_id, "level": float(0), "streaming.streaming": True},
                                {"_id": 1, "public_ip": 1, "port": 1, "streaming": 1})
        servers_count = yield task(self.query, servers_cursor.count)

        if self.stop and self.stream_servers == servers_count:

            self.send({
                "signal": 'stop',
                "stream": self.stream_id
            })
            result = {"msg": "Stopping stream"}

        else:

            if servers_count >= 1:
                result = self.streamer.rescale(list(servers_cursor))
                for server in result["freed"]:
                    if not self.streamer.is_sync(server["id"]):
                        self.db.conn.servers.update({"_id": ObjectId(server["id"])}, {"$set":{"streaming.streaming": False}})
            else:
                result = {"msg": "No unused server"}

        respond(result)
