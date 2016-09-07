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
from API.Auth.MountHandler import MountAddHandler
from API.Auth.MountHandler import MountRemoveHandler
from API.Auth.MountHandler import ListenerAddHandler
from API.Auth.MountHandler import ListenerRemoveHandler
from API.Auth.IcecastHandler import IcecastHandler
from Model.Db import Db

__author__ = "Michal Bystricky"
__copyright__ = "Copyright 2013, Michal Bystricky"
__status__ = "Prototype"

class Web(Base, Thread):

    def __init__(self, port, icecast):
        super(Web, self).__init__()

        self.port = port
        self.streams = icecast.get_streams()
        self.icecast = icecast

    def run(self):

        settings = {
            "title": u"SoundSlash backend Web API",
            "xsrf_cookies": False,
            "debug": True,
            "db": motor.MotorClient("mongodb://pipeline:horcica7med#vajco1parky@127.0.0.1:27017/pipeline")["pipeline"],
            "facebook_api_key": "486579808100437",
            "facebook_secret": "5841eb1027ed61718249f034d503e612",
            "executor": ThreadPoolExecutor(max_workers=4),
            "streams": self.streams,
            "icecast": self.icecast
            }

        application = tornado.web.Application([
                                                  (r"/mount_add", MountAddHandler),
                                                  (r"/mount_remove", MountRemoveHandler),
                                                  (r"/listener_add", ListenerAddHandler),
                                                  (r"/listener_remove", ListenerRemoveHandler),
                                              ], **settings)

        application.listen(self.port)
        logging.getLogger('pipeline_api').debug("Starting Auth Web API")
        tornado.ioloop.IOLoop.instance().start()
