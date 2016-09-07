#!/usr/bin/env python

"""
Server creates web server using Tornado and handles communication.
"""

import time
import pygst
pygst.require("0.10")
import gst
import logging
import tornado.auth
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.websocket
from tornado.options import define, options
import motor
from tornado.options import define, options
from concurrent.futures import ThreadPoolExecutor
from functools import partial, wraps
from threading import Thread

from Framework.Base import *
from Model.BaseThreaded import BaseThreaded
from Model.Streaming.StreamBin import StreamBin
from API.Pipeline.LiveHandler import LiveHandler
from API.Pipeline.UpdatesHandler import UpdatesHandler
from API.Pipeline.DirectorHandler import StartStreamHandler
from API.Pipeline.DirectorHandler import RestartStreamHandler
from API.Pipeline.DirectorHandler import IsAliveHandler
from API.Pipeline.DirectorHandler import RunCommandHandler
from API.Pipeline.DirectorHandler import PlaylistUpdateHandler
from API.Pipeline.DirectorHandler import ScaleHandler

__author__ = "Michal Bystricky"
__copyright__ = "Copyright 2013, Michal Bystricky"
__status__ = "Prototype"

class Web(Base, Thread):

    def __init__(self, port):
        super(Web, self).__init__()

        self.port = port
        # self.director = director

    def run(self):

        settings = {
            "title": u"SoundSlash backend Web API",
            "xsrf_cookies": False,
            "debug": True,
            "db": motor.MotorClient("mongodb://pipeline:horcica7med#vajco1parky@127.0.0.1:27017/pipeline")["pipeline"],
            "facebook_api_key": "486579808100437",
            "facebook_secret": "5841eb1027ed61718249f034d503e612",
            "executor": ThreadPoolExecutor(max_workers=4),
            # "director": self.director,
            }

        application = tornado.web.Application([
            (r"/live.json", LiveHandler),
            (r"/updates.json", UpdatesHandler),
            (r"/start-streaming.json", StartStreamHandler),
            (r"/restart.json", RestartStreamHandler),
            (r"/scale.json", ScaleHandler),
            (r"/is-alive.json", IsAliveHandler),
            (r"/playlist-update.json", PlaylistUpdateHandler),
            (r"/run-command.json", RunCommandHandler)
        ], **settings)

        application.listen(self.port)
        logging.getLogger('pipeline_api').debug("Starting Pipeline Web API")
        tornado.ioloop.IOLoop.instance().start()
