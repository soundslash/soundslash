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
import gc
import logging

from Framework.Base import *
from Context.SelectStreamingServer import SelectStreamingServer
from Model.Usecase import Usecase
from Model.Usecase import send
from Model.Db import Db

__author__ = "Michal Bystricky"
__copyright__ = "Copyright 2013, Michal Bystricky"
__status__ = "Prototype"

class StopStreaming(Base):

    def __init__(self, stream_manager, stream_id, streamer):
        super(StopStreaming, self).__init__()

        self.stream_manager = stream_manager
        self.stream_id = stream_id
        self.streamer = streamer


    @asynchronous
    def run(self, respond):

        del self.stream_manager.streams[self.stream_id]
        self.streamer.pipe.set_state(gst.STATE_NULL)
        self.streamer.mainloop_thread.mainloop.quit()
        # try:
        #     self.streamer.lock.release()
        # except:
        #     pass

        yield task(self.query, self.db.streams.update, {"_id": ObjectId(self.stream_id)},
                                    {"$set":{"status": "ready"}})

        yield task(self.query, self.db.servers.update, {"streaming.stream": self.stream_id, "streaming.streaming": True},
                                    {"$set":{"streaming.streaming": False}}, multi=True)

        collected = gc.collect()
        logging.getLogger('system').debug("StopStreaming: Deallocated %d objects." % (collected))


        respond({
            "msg": "Pipeline set to NULL state"
        })
