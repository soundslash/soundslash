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
from Model.Usecase import Usecase
from Model.Usecase import send
from Model.Db import Db

__author__ = "Michal Bystricky"
__copyright__ = "Copyright 2013, Michal Bystricky"
__status__ = "Prototype"

class SelectStreamingServer(Base):

    def __init__(self, user_id, stream_id, quality=None):
        super(SelectStreamingServer, self).__init__()
        self.user_id = user_id
        self.stream_id = stream_id
        self.quality = quality

    @asynchronous
    def run(self, respond):

        update = { "user_id": self.user_id, "streaming.stream": unicode(self.stream_id), "streaming.streaming": True }

        if self.quality is not None:
            update["streaming.quality"] = float(self.quality)

        response = yield task(self.query, self.db.servers.find_and_modify,
                              query={ "type": "streaming", "streaming.streaming": False, "streaming.max_listeners": 8 },
                              fields={ "public_ip": 1, 'local_ip': 1, "port": 1, "streaming": 1, "_id": 1 },
                              update={ "$set": update },
                              new=False)


        if response is None:
            server = {
                "error": "No streaming server found"
            }

        else:
            server = {
                "public_ip": response["public_ip"],
                "port": response["port"],
                "mount": response["streaming"]["mount"],
                "db_obj": response
            }

        respond(server)
