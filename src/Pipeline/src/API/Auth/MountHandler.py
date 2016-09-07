#!/usr/bin/env python

"""
Handle mount/listener add/remove.
"""

import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s: %(levelname)s: %(message)s')
from mongokit import *
import tornado.auth
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
from tornado.options import define, options
import xml.etree.ElementTree as ET
import urllib
# from Helpers.ip import local_ip
# from Helpers.ip import public_ip
import Helpers.ip
import motor
import urlparse
from collections import OrderedDict
from bson.objectid import ObjectId
from tornado.options import define, options
from concurrent.futures import ThreadPoolExecutor
from functools import partial, wraps
import time
import simplejson as json
import datetime

from Model.Server import Server
from Helpers.level import get_level
from Helpers.level import round_max_listeners
from Model.Db import Db


__author__ = "Michal Bystricky"
__copyright__ = "Copyright 2013, Michal Bystricky"
__status__ = "Prototype"

class BaseHandler(tornado.web.RequestHandler):

    @property
    def streams(self):
        if not hasattr(self, '_streams'):
            self._streams = self.settings['streams']
        return self._streams

    @property
    def icecast(self):
        if not hasattr(self, '_icecast'):
            self._icecast = self.settings['icecast']
        return self._icecast

    @property
    def db(self):
        if not hasattr(self, '_db'):
            self._db = self.settings['db']
        return self._db

    def parse_mount(self, mount):
        mount = mount.split("?")
        args = OrderedDict({})
        if len(mount) == 2:
            args = OrderedDict(urlparse.parse_qs(mount[1]))

        return (mount[0], args)

    def get_first(self, iterable, default=None):
        if iterable:
            for item in iterable:
                return item
        return default

    def unblock(self, function, parameters, callback):
        """
        This will unblock function. Parameters are dict.
        """
        self.settings["executor"].submit(
            partial(function, **parameters)
        ).add_done_callback(
            lambda future: tornado.ioloop.IOLoop.instance().add_callback(
                partial(callback, future.result())))


    @tornado.gen.coroutine
    def update_stream(self, mount, attrs, update):
        self.icecast.update_stream(mount, attrs, update)



class MountRemoveHandler(BaseHandler):

    @tornado.web.asynchronous
    @tornado.gen.engine
    def post(self):
        mount = self.get_argument("mount")
        self.streams[mount]["streaming"] = False
        self.streams[mount]["listeners"] = 0
        self.streams[mount]["level"] = float(0)


        server = yield motor.Op(self.db.servers.find_one,
                                {
                                    "type": "streaming",
                                    "local_ip": self.streams[mount]["local_ip"],
                                    "port": self.streams[mount]["port"],
                                    "streaming.mount": mount
                                },
                                {
                                    "streaming": 1,
                                    "_id": 0
                                })

        stream = yield motor.Op(self.db.streams.find_one,
                                {
                                    "_id": ObjectId(server["streaming"]["stream"])
                                },
                                {
                                    "_id": 1,
                                    "pipeline_server": 1,
                                    "reencoding": 1
                                })

        pipeline = yield motor.Op(self.db.servers.find_one,
                                {
                                    "_id": ObjectId(stream["pipeline_server"])
                                },
                                {
                                    "_id": 0,
                                    "local_ip": 1,
                                    "port": 1,
                                })


        url = "http://"+pipeline["local_ip"]+":"+unicode(pipeline["port"])+"/is-alive.json"

        tornado.httpclient.AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient")

        http_client = tornado.httpclient.AsyncHTTPClient()
        # try:
        post_args = {
            "stream": unicode(stream["_id"])
        }
        req = tornado.httpclient.HTTPRequest(url, body=urllib.urlencode(post_args), method="POST")

        response = yield tornado.gen.Task(http_client.fetch, req)

        if self.is_error(response):
            pipeline_error = True
            pipeline_down = True
        else:
            pipeline_down = False
            try:

                response = json.loads(unicode(response.body))
                if stream['reencoding'] and "error" in response and response["error"] == "No such stream":
                    pipeline_down = False
                    print("NEMAM PRECO!")

                if response["is_alive"] == "hell_yeah":
                    pipeline_error = False
                else:
                    pipeline_error = True
            except:
                pipeline_error = True



        if pipeline_error:
            if pipeline_down:
                logging.getLogger('auth').debug(mount+", pipeline is not responding, setting pipeline "+
                                                stream["pipeline_server"]+" down")
                yield motor.Op(self.db.servers.update, {"_id":ObjectId(stream["pipeline_server"])},
                                          {"$set":{
                                              "down": True
                                          }}, upsert=False, multi=False)

            logging.getLogger('auth').debug(mount+", pipeline error, setting stream's status "+
                                                  "to ready (which pipeline_server is "+stream["pipeline_server"]+")")
            yield motor.Op(self.db.streams.update, {"_id": ObjectId(server["streaming"]["stream"])},
                                      {"$set":{
                                          "status": "ready",
                                          "pipeline_server": None
                                      }}, upsert=False, multi=True)



        yield tornado.gen.Task(self.unblock, function=self.update_stream,
                               parameters={
                                   "mount":mount,
                                   "attrs": self.streams[mount],
                                   "update": self.streams[mount]
                               })

        logging.getLogger('auth').debug(mount+", mount removed")
        self.finish()

    def is_error(self, response):
        try:
            if response.error:
                return True
            else:
                return False
        except:
            return True
        return False


class MountAddHandler(BaseHandler):

    @tornado.web.asynchronous
    @tornado.gen.engine
    def post(self):
        mount = self.get_argument("mount")
        self.streams[mount]["streaming"] = True
        self.streams[mount]["listeners"] = 0
        self.streams[mount]["level"] = float(0)

        yield tornado.gen.Task(self.unblock, function=self.update_stream,
                               parameters={
                                   "mount":mount,
                                   "attrs": self.streams[mount],
                                   "update": self.streams[mount]
                               })

        logging.getLogger('auth').debug(mount+", mount added")

        self.finish()

class ListenerAddHandler(BaseHandler):

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self):
        mount = self.get_argument("mount")
        mount, args = self.parse_mount(mount)

        server = yield motor.Op(self.db.servers.find_one,
                       {
                           "type": "streaming",
                           "local_ip": self.streams[mount]["local_ip"],
                           "port": self.streams[mount]["port"],
                           "streaming.mount": mount
                       },
            {
                "streaming": 1,
                "_id": 0
            })

        stream = yield motor.Op(self.db.streams.find_one,
                                {
                                    "_id": ObjectId(server["streaming"]["stream"])
                                },
                                {
                                    "_id": 0,
                                    "public": 1
                                })

        if not stream["public"]:
            if "password" in args:
                stream_pass = yield motor.Op(self.db.streams.find_one,
                                        {
                                            "_id": ObjectId(server["streaming"]["stream"]),
                                            "users.password": self.get_first(args["password"])
                                        },
                                        {
                                            "_id": 1
                                        })
                if stream_pass is None:
                    auth = None
                else:
                    auth = True

            else:
                auth = None

        log_message = mount+", listener added"
        add_listener = False
        if not self.streams[mount]["listeners"] >= self.streams[mount]["max_listeners"]:
            if stream["public"]:
                self.set_header("icecast-auth-user", 1)
                add_listener = True
                log_message+=", public"
            elif auth:
                self.set_header("icecast-auth-user", 1)
                add_listener = True
                log_message+=", authenticated"
            else:
                self.set_header("icecast-auth-user", 0)
                # self.set_header("icecast-auth-timelimit", 30)

                log_message+=", not authenticated"
        else:
            self.write(mount+": Maximum listeners reached")

            log_message+=", maximum listeners reached "+unicode(self.streams[mount]["listeners"])+"/"+unicode(self.streams[mount]["max_listeners"])

        now = datetime.datetime.now()
        if add_listener:
            query = {
                "stream_id": server["streaming"]["stream"],
                "datetime": datetime.datetime(now.year, now.month, now.day, now.hour),
                "year": now.year,
                "month": now.month,
                "day": now.day,
                "hour": now.hour
            }

            yield motor.Op(self.db.statistics.update, query,
                                      {"$inc":{
                                          "listeners": 1
                                      }}, upsert=True, multi=False)

        if self.streams[mount]["streaming"]:
            if self.streams[mount]["listeners"] < 0: self.streams[mount]["listeners"] = 0
            self.streams[mount]["listeners"] += 1
            prev_level = self.streams[mount]["level"]
            self.streams[mount]["level"] = get_level(self.streams[mount]["listeners"], self.streams[mount]["max_listeners"])

            if self.streams[mount]["level"] != prev_level or (time.time()-self.streams[mount]["listeners_last_updated"])>60:
                self.streams[mount]["listeners_last_updated"] = time.time()
                if self.streams[mount]["level"] == float(10):
                    self.streams[mount]["full"] = True
                # self.update_stream(mount, self.streams[mount], self.streams[mount])
                yield tornado.gen.Task(self.unblock, function=self.update_stream,
                                       parameters={
                                           "mount":mount,
                                           "attrs": self.streams[mount],
                                           "update":self.streams[mount]
                                       })

        # print(mount+)
        log_message+=", level "+unicode(self.streams[mount]["level"])
        print log_message
        logging.getLogger('auth').debug(log_message)

        self.finish()



class ListenerRemoveHandler(BaseHandler):

    @tornado.web.asynchronous
    @tornado.gen.engine
    def post(self):
        mount = self.get_argument("mount")
        mount, args = self.parse_mount(mount)

        if self.streams[mount]["streaming"]:
            self.streams[mount]["listeners"] -= 1
            if self.streams[mount]["listeners"] < 0: self.streams[mount]["listeners"] = 0
            prev_level = self.streams[mount]["level"]
            self.streams[mount]["level"] = get_level(self.streams[mount]["listeners"], self.streams[mount]["max_listeners"])
            if self.streams[mount]["level"] != prev_level or (time.time()-self.streams[mount]["listeners_last_updated"])>60:
                self.streams[mount]["listeners_last_updated"] = time.time()
                if self.streams[mount]["level"] == float(10):
                    self.streams[mount]["full"] = True
                # self.update_stream(mount, self.streams[mount], self.streams[mount])
                yield tornado.gen.Task(self.unblock, function=self.update_stream,
                                       parameters={
                                           "mount":mount,
                                           "attrs": self.streams[mount],
                                           "update":self.streams[mount]
                                       })

        log_message=mount+", listener removed, level "+unicode(self.streams[mount]["level"])

        logging.getLogger('auth').debug(log_message)

        self.finish()
