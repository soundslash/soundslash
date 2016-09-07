#!/usr/bin/env python

"""
StreamManagement class (Singleton)
* handle control through console (e.g. Bash, SSH)
* spawning and removing new streamings (management of streamings)
"""

import time
import pygst
pygst.require("0.10")
import gst
import logging
from mongokit import *
from bson.objectid import ObjectId
from multiprocessing.synchronize import BoundedSemaphore
import psutil
from threading import Thread
from noconflict import classmaker

from Framework.Base import *
from Framework.Singleton import Singleton
from Model.PipelineLoadBalancer import PipelineLoadBalancer
from Context.StartStreaming import StartStreaming
from Context.StartEncodedStreaming import StartEncodedStreaming
from Context.LiveStreaming import LiveStreaming
import Helpers.ip
from Model.Server import Server
from Model.Stream import Stream
import Helpers.globals
from Model.Db import Db
from Terminal import Terminal
from Context.SelectStreamingServer import SelectStreamingServer
from Context.ScaleStreaming import ScaleStreaming
from Context.RescaleStreaming import RescaleStreaming
from Context.StopStreaming import StopStreaming
from Context.IsStreamingAlive import IsStreamingAlive
from Context.NextTrack import NextTrack

__author__ = "Michal Bystricky"
__copyright__ = "Copyright 2013, Michal Bystricky"
__status__ = "Prototype"

@context("StreamManagement")
class StreamManagement(Base, Singleton):

    __metaclass__ = classmaker()

    @staticmethod
    def aspects():

        def stream_to_unicode(*args, **kwargs):
            if "stream" in kwargs:
                kwargs["stream"] = unicode(kwargs["stream"])
            return kwargs

        aspect1 = {
            "pointcut": ".*",
            "advise": {
                "before": stream_to_unicode
            }
        }

        def no_such_stream(*args, **kwargs):
            if kwargs["stream"] not in kwargs["self"].streams:
                kwargs["respond"]({"error": "No such stream"})
                return Call.stop
            else:
                return Call.proceed

        aspect2 = {
            "pointcut": "^(?!((start_streaming))$).*",
            "advise": {
                "before": no_such_stream
            }
        }

        def stream_exists(*args, **kwargs):
            if kwargs["stream"] in kwargs["self"].streams:
                kwargs["respond"]({"error": "Stream exists"})
                return Call.stop
            else:
                return Call.proceed

        aspect3 = {
            "pointcut": "^start_streaming$",
            "advise": {
                "before": stream_exists
            }
        }

        return [aspect1, aspect2, aspect3]



    def __init__(self, port):
        super(StreamManagement, self).__init__()
        self.streams = {}

        # one command at the time
        self.lock = BoundedSemaphore(value=1)

        local_ip = Helpers.ip.local_ip()
        public_ip = Helpers.ip.public_ip()

        self.db.servers.update(
                             { "type": "pipeline", "local_ip": local_ip, "port": port },
                             {  "level": float(0),
                                "type": "pipeline",
                                "local_ip": local_ip,
                                "public_ip": public_ip,
                                "port": port,
                                "down": False
                             }, upsert=True)
        server = self.db.servers.find_one(
                            { "type": "pipeline", "local_ip": local_ip, "port": port },
                            { "_id": 1, })
        # db = Db()
        # server = db.conn.Server.find_one({"type": "pipeline", "local_ip": local_ip, "port": port})
        # if server == None:
        #     server = db.conn.Server()
        #
        # server["level"] = float(0)
        # server["type"] = "pipeline"
        # server["local_ip"] = local_ip
        # server["public_ip"] = public_ip
        # server["port"] = port
        # server["down"] = False
        # server.save()

        self.pipeline_server_id = unicode(server["_id"])

        PipelineLoadBalancer(self.pipeline_server_id).start()

        # self.db = db

        Helpers.globals.set_id_pipeline(server["_id"])

        self.connect(handler= self.dump_dot_file, signal= "dump_dot_file")
        self.connect(handler= self.playlist_update, signal= "playlist_update")
        self.connect(handler= self.change_selection, signal= "change_selection")
        self.connect(handler= self.next, signal= "next")
        self.connect(handler= self.is_alive, signal= "is_alive")
        self.connect(handler= self.scale_streaming, signal= "scale")
        self.connect(handler= self.start_streaming, signal= "start")
        self.connect(handler= self.print_playlist, signal= "print_playlist")
        self.connect(handler= self.register_updates_observer, signal= "register_updates_observer")
        self.connect(handler= self.notify_current_track, signal= "notify_current_track")
        self.connect(handler= self.unregister_updates_observer, signal= "unregister_updates_observer")
        self.connect(handler= self.update_buffer, signal= "update_buffer")
        self.connect(handler= self.start_live, signal= "start_live")
        self.connect(handler= self.stop_streaming, signal= "stop")
        self.connect(handler= self.rescale_streaming, signal= "rescale")
        self.connect(handler= self.__streamer_initialized, signal="streamer_initialized")


    @in_context([])
    def __streamer_initialized(self, streamer, respond):
        logging.debug("__streamer_initialized(): New initialized streamer")
        self.streams[unicode(streamer.stream["_id"])] = streamer
        self.lock.release()
        yield task(self.query, self.db.streams.update, {"_id": streamer.stream["_id"]},
                   {"$set":{"status": "playing"}}, upsert=False, multi=False)
        respond('OK')

    @in_context(["StreamManagement"])
    def help(self, respond):
        pr = ""
        with open('README.TXT', 'r') as content_file:
            lines = content_file.readlines()
        for line in lines:
            if line.startswith("#"):
                pr += line[1:]
        del lines
        print pr
        respond({"msg": pr})

    @in_context(["StreamManagement"])
    def start_streaming(self, stream, quality, respond):
        self.lock.acquire()

        stream = yield task(self.query, self.db.streams.find_one, {"_id": ObjectId(stream)},
                                {
                                    "_id": 1,
                                    "reencoding": 1,
                                    "user_id": 1,
                                    "name": 1,
                                    "description": 1,
                                    "genres": 1,
                                    "quality": 1,
                                    "default_program_id": 1})

        if stream["reencoding"]:

            result = yield task(self.call, StartStreaming(self, self.pipeline_server_id, stream, quality).run)

        else:
            result = yield task(self.call, StartEncodedStreaming(self, self.pipeline_server_id, stream).run)


        if "error" in result:
            self.lock.release()

        respond(result)

    @in_context(["StreamManagement"])
    def is_alive(self, stream, respond):
        result = yield task(self.call, IsStreamingAlive(self, stream, streamer=self.streams[stream]).run)
        respond(result)

    @in_context(["StreamManagement"])
    def playlist_update(self, stream, group, respond):
        result = yield task(self.call, self.streams[stream].scheduler.playlist_update, group=group)
        respond(result)

    @in_context(["StreamManagement"])
    def change_selection(self, stream, respond):
        result = yield task(self.call, self.streams[stream].scheduler.change_selection)
        respond(result)

    @in_context(["StreamManagement"])
    def next(self, stream, respond, fade_in=None, fade_out=None):
        result = yield task(self.call, NextTrack(streamer=self.streams[stream], fade_in=fade_in, fade_out=fade_out).run)
        respond(result)

    @in_context(["StreamManagement"])
    def stop_streaming(self, stream, respond):
        self.lock.acquire()
        result = yield task(self.call, StopStreaming(self, stream, streamer=self.streams[stream]).run)
        self.lock.release()
        respond(result)

    @in_context(["StreamManagement"])
    def scale_streaming(self, stream, respond, quality = None):
        result = yield task(self.call, ScaleStreaming(stream, quality=quality, streamer=self.streams[stream]).run)
        respond(result)

    @in_context(["StreamManagement"])
    def rescale_streaming(self, stream, respond, stop = True):
        result = yield task(self.call, RescaleStreaming(
                stream,
                streamer=self.streams[stream],
                stop=stop,
                stream_servers=len(self.streams[stream].servers.items())
            ).run)

        respond(result)

    @in_context(["StreamManagement"])
    def start_live(self, stream, appsrc, respond, loop=None):
        result = yield task(self.call, LiveStreaming(stream, streamer=self.streams[stream], appsrc=appsrc, loop=loop).run)
        respond(result)

    @in_context(["StreamManagement"])
    def register_updates_observer(self, stream, handler, respond):
        result = yield task(self.call, self.streams[stream].scheduler.register_updates_observer, handler=handler)
        respond(result)

    @in_context(["StreamManagement"])
    def notify_current_track(self, stream, respond):
        result = yield task(self.call, self.streams[stream].scheduler.buffer.notify_current_track)
        respond(result)

    @in_context(["StreamManagement"])
    def unregister_updates_observer(self, stream, handler, respond):
        result = yield task(self.call, self.streams[stream].scheduler.unregister_updates_observer, handler=handler)
        respond(result)

    @in_context(["StreamManagement"])
    def update_buffer(self, stream, buffer, respond):
        result = yield task(self.call, self.streams[stream].scheduler.update_buffer, buffer=buffer, unblock=True)
        respond(result)

    @in_context(["StreamManagement"])
    def dump_dot_file(self, stream, respond):
        result = yield task(self.call, self.streams[stream].dump_dot_file, unblock=True)
        respond({"msg": "OK", "result": result})

    @in_context(["StreamManagement"])
    def print_playlist(self, stream, respond):
        result = self.streams[stream].scheduler.print_playlist()
        respond(result)

    @in_context(["StreamManagement"])
    def run_command(self, command, respond):
        terminal = Terminal(self)
        result = terminal.parse_and_execute(command)
        respond(result)

    def __results_to_dict(self, results):
        res_arr = []
        for result in results:
            res_arr.append(result)
        return res_arr
