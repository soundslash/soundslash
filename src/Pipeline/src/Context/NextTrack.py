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
from Context.SelectStreamingServer import SelectStreamingServer
from Model.Usecase import Usecase
from Model.Usecase import send
from Model.Db import Db
from Context.StopStreaming import StopStreaming

__author__ = "Michal Bystricky"
__copyright__ = "Copyright 2013, Michal Bystricky"
__status__ = "Prototype"

@context("NextTrack")
class NextTrack(Base):

    def __init__(self, streamer, fade_in=None, fade_out=None):
        super(NextTrack, self).__init__()

        self.streamer = streamer
        if hasattr(self.streamer.scheduler, "fade") and fade_in is None:
            fade_in = self.streamer.scheduler.fade["fade_in"]
        elif fade_in is None:
            fade_in = 0
        self.fade_in = fade_in
        if hasattr(self.streamer.scheduler, "fade") and fade_out is None:
            fade_out = self.streamer.scheduler.fade["fade_out"]
        elif fade_out is None:
            fade_out = 0
        self.fade_out = fade_out


    # @staticmethod
    # def aspects():
    #
    #
    #     def decrease_volume(*args, **kwargs):
    #         if kwargs["self"].encoded or kwargs["fade_out"] == 0: return Call.proceed
    #
    #         # volume = kwargs["self"].stream_bin.get_volume()
    #         volume = 100
    #         final_volume = 0
    #
    #         sleep = 0.01
    #         sleep_duration = kwargs["fade_out"]
    #         position = kwargs["self"].stream_bin.get_postion()
    #
    #         change_volume = volume-final_volume
    #
    #         iterations = int(sleep_duration/sleep)
    #         change_iteration = float(change_volume)/float(iterations)
    #
    #         for i in range(iterations):
    #             volume -= change_iteration
    #             position += sleep*gst.SECOND
    #             kwargs["self"].stream_bin.set_volume(position, volume)
    #             # print position, volume
    #
    #         while kwargs["self"].stream_bin.get_postion() <= position+(0.5*gst.SECOND):
    #             time.sleep(0.1)
    #
    #         return Call.proceed
    #
    #     def increase_volume(*args, **kwargs):
    #         if kwargs["self"].encoded or kwargs["fade_in"] == 0: return Call.proceed
    #         volume = 0
    #         final_volume = 100
    #
    #         sleep = 0.01
    #         sleep_duration = kwargs["fade_in"]
    #
    #         change_volume = volume-final_volume
    #
    #         iterations = int(sleep_duration/sleep)
    #         change_iteration = float(change_volume/iterations)
    #
    #         position = 0
    #         for i in range(iterations):
    #             volume -= change_iteration
    #             position += sleep*gst.SECOND
    #             kwargs["self"].stream_bin.set_volume(position, volume)
    #             # time.sleep(sleep)
    #
    #         return Call.proceed
    #
    #     # def black_hole(*args, **kwargs):
    #     #     print "skipujem"
    #
    #
    #     aspect1 = {
    #         "pointcut": "^stream_eos$",
    #         "advise": {
    #             "before": increase_volume
    #         }
    #     }
    #
    #     aspect2 = {
    #         "pointcut": "^stream_eos$",
    #         "advise": {
    #             "before": decrease_volume,
    #             # "around": black_hole
    #         }
    #     }
    #
    #     def unset_volume_control(*args, **kwargs):
    #
    #         if kwargs["self"].encoded or kwargs["fade_in"] == 0: return Call.proceed
    #
    #         # w8 for increase volume
    #         time.sleep(kwargs["fade_in"])
    #         kwargs["self"].stream_bin.unset_volume_control()
    #
    #         return Call.proceed
    #
    #
    #     aspect3 = {
    #         "pointcut": "^stream_eos$",
    #         "advise": {
    #             "after": unset_volume_control,
    #         }
    #     }
    #
    #
    #     def default_volume(*args, **kwargs):
    #
    #         if kwargs["self"].encoded: return Call.proceed
    #
    #         fade_out = kwargs["self"]["fade"]["fade_out"]
    #         fade_in = kwargs["self"]["fade"]["fade_in"]
    #
    #         kwargs["self"].stream_bin.unset_volume_control()
    #
    #         if fade_out != 0:
    #             # fade out
    #             volume = 100
    #             final_volume = 0
    #             sleep = 0.01
    #             sleep_duration = fade_out
    #
    #             position = int(kwargs["self"].buffer.current_track_serialized["duration"])-(sleep_duration*gst.SECOND)
    #
    #             change_volume = volume-final_volume
    #             iterations = int(sleep_duration/sleep)
    #             change_iteration = float(change_volume)/float(iterations)
    #             for i in range(iterations):
    #                 volume -= change_iteration
    #                 position += sleep*gst.SECOND
    #                 kwargs["self"].stream_bin.set_volume(position, volume)
    #
    #         if fade_in != 0:
    #             # fade in
    #             volume = 0
    #             final_volume = 100
    #             sleep = 0.01
    #             sleep_duration = fade_in
    #             change_volume = volume-final_volume
    #             iterations = int(sleep_duration/sleep)
    #             change_iteration = float(change_volume/iterations)
    #             position = 0
    #             for i in range(iterations):
    #                 volume -= change_iteration
    #                 position += sleep*gst.SECOND
    #                 kwargs["self"].stream_bin.set_volume(position, volume)
    #
    #         return Call.proceed
    #
    #     aspect4 = {
    #         "pointcut": "^stream_eos$",
    #         "advise": {
    #             "after": default_volume
    #         }
    #     }
    #
    #
    #     return [aspect1, aspect2, aspect3, aspect4]

    @in_context([])
    def run(self, respond):

        scheduler = self.streamer.scheduler

        result = yield task(self.send, in_context=respond.this_context, message={
            "signal": "stream_eos_"+unicode(self.streamer.stream["_id"]),
            "sender": scheduler.stream_bin,
            "fade_in": self.fade_in,
            "fade_out": self.fade_out
        }, unblock=True)

        yield task(self.call, scheduler.buffer.notify_current_track, unblock=False)
        yield task(self.call, scheduler.buffer.notify_buffer_update, unblock=False)
        yield task(self.call, scheduler.history.notify_previous_update, unblock=False)

        respond(result)
