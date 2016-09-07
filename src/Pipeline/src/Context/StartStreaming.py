#!/usr/bin/env python

"""
"""

from pydispatch import dispatcher
import time
from bson.objectid import ObjectId
import pygst
pygst.require("0.10")
import gst

from Framework.Base import *
from Model.Streaming.Scheduler import Scheduler
from Model.Streaming.Streamer import Streamer
from Model.Streaming.EncodedStreamer import EncodedStreamer
from Model.Streaming.EncodedScheduler import EncodedScheduler
from Model.Usecase import Usecase
from Model.Usecase import send
from Context.SelectStreamingServer import SelectStreamingServer
from Model.Db import Db

__author__ = "Michal Bystricky"
__copyright__ = "Copyright 2013, Michal Bystricky"
__status__ = "Prototype"

class StartStreaming(Base):

    def __init__(self, stream_manager, pipeline_server_id, stream, quality):
        super(StartStreaming, self).__init__()

        self.stream_manager = stream_manager
        self.pipeline_server_id = pipeline_server_id
        self.stream = stream
        self.quality = float(quality)

    @asynchronous
    def run(self, respond):

        response = yield task(self.query, self.db.streams.find_and_modify,
            query={ "_id":ObjectId(self.stream["_id"]), "status": "ready" },
            fields={ "_id": 1 },
            update={"$set": {
                "status": "steady",
                "pipeline_server": self.pipeline_server_id
            }},
            new=False)

        if response is None:
            response = {
                "error": "Initialization is handled by another instance"
            }

        else:

            server = yield task(self.call, SelectStreamingServer(self.stream["user_id"],
                                                                    self.stream["_id"],
                                                                    quality=self.quality).run)

            if not "error" in server:
                player = Streamer(self.stream)
                player.scheduler = Scheduler(player)

                yield task(self.call, player.scheduler.init, player=player)

                player.pipe.set_state(gst.STATE_PLAYING)

                player.scale(server["db_obj"], self.quality, sync=0, init=False)

                # w8 to init
                self.stream_manager.lock.acquire()
                self.stream_manager.lock.release()

                del server["db_obj"]


            response = server


        respond(response)
