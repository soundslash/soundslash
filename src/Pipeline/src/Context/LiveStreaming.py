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
from Model.Streaming.GridFSSource import GridFSSource

__author__ = "Michal Bystricky"
__copyright__ = "Copyright 2013, Michal Bystricky"
__status__ = "Prototype"

@context("LiveStreaming")
class LiveStreaming(Base):

    def __init__(self, stream, streamer, loop, appsrc):
        super(LiveStreaming, self).__init__()

        self.streamer = streamer
        self.appsrc = appsrc
        self.stream = stream
        self.loop = loop

    @staticmethod
    def aspects():

        def decrease_volume(*args, **kwargs):

            # volume = kwargs["self"].stream_bin.get_volume()
            # final_volume = 0
            #
            # sleep = 0.05
            # sleep_duration = 1
            #
            # change_volume = volume-final_volume
            #
            # iterations = int(sleep_duration/sleep)
            # change_iteration = float(change_volume/iterations)
            #
            # position = kwargs["self"].stream_bin.get_postion()
            #
            # for i in range(iterations):
            #     volume -= change_iteration
            #     position += sleep*gst.SECOND
            #     kwargs["self"].stream_bin.set_volume(position, volume)
            #
            # kwargs["self"].stream_bin.set_volume(0, 100)
            #
            # while kwargs["self"].stream_bin.get_postion() <= position+(0.5*gst.SECOND):
            #     time.sleep(0.1)



            return Call.proceed


        aspect1 = {
            "pointcut": "^start_live$",
            "advise": {
                "before": decrease_volume
            }
        }

        def pause_main_stream_loop(*args, **kwargs):

            # kwargs["self"].stream_bin.loop(kwargs["loop"])
            # kwargs["self"].stream_bin.unset_volume_control()

            return Call.proceed

        aspect1_2 = {
            "pointcut": "^start_live$",
            "advise": {
                "before": pause_main_stream_loop
            }
        }

        def increase_volume(*args, **kwargs):

            # kwargs["self"].stream_bin.stop_loop()


            # volume = 0
            # final_volume = 100
            #
            # sleep = 0.05
            # sleep_duration = 1
            #
            # change_volume = volume-final_volume
            #
            # iterations = int(sleep_duration/sleep)
            # change_iteration = float(change_volume/iterations)
            #
            # position = kwargs["self"].stream_bin.get_postion()
            #
            # for i in range(iterations):
            #     volume -= change_iteration
            #     position += sleep*gst.SECOND
            #     kwargs["self"].stream_bin.set_volume(position, volume)


            return Call.proceed


        aspect2 = {
            "pointcut": "^stop_live$",
            "advise": {
                "after": increase_volume
            }
        }

        return [aspect1, aspect1_2, aspect2]

    @in_context(["LiveStreaming"])
    def run(self, respond):

        result = yield task(self.call, in_context=respond.this_context, fn=self.streamer.scheduler.start_live,
                            appsrc=self.appsrc, loop=self.loop, unblock=True)

        respond(result)
