import logging
import tornado.auth
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.websocket
from tornado.options import define, options
from bson.objectid import ObjectId
import Helpers.globals
import motor
from bson import SON

import Helpers.globals
from API.Pipeline.BaseHandler import BaseHandler
from Framework.Base import *

class StartStreamHandler(BaseHandler, Base):

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self):

        stream = self.get_argument("stream")
        quality = self.get_argument("quality")

        logging.getLogger('pipeline_api').debug("Request from "+self.request.remote_ip+
                                                ": Start streaming stream "+stream+", quality "+unicode(quality))

        response = yield tornado.gen.Task(self.send, message={"signal": "start", "stream": stream, "quality": quality}, unblock=True)


        self.write(response)
        self.finish()


class RestartStreamHandler(BaseHandler, Base):

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self):

        stream = self.get_argument("stream")
        quality = self.get_argument("quality")

        logging.getLogger('pipeline_api').debug("Request from "+self.request.remote_ip+
                                                ": REstart streaming stream "+stream+", quality "+unicode(quality))

        result = []
        response = yield tornado.gen.Task(self.send, message={"signal": "stop", "stream": stream}, unblock=True)
        result.append(response)
        response = yield tornado.gen.Task(self.send, message={"signal": "start", "stream": stream, "quality": quality}, unblock=True)
        result.append(response)

        self.write({"result": result})
        self.finish()


class ScaleHandler(BaseHandler, Base):

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self):

        stream = self.get_argument("stream")
        quality = self.get_argument("quality")

        logging.getLogger('pipeline_api').debug("Request from "+self.request.remote_ip+
                                                ": Scaling stream "+stream+", quality "+unicode(quality))

        result = yield tornado.gen.Task(self.send, message={"signal": "scale", "stream": stream}, unblock=True)

        self.write(result)
        self.finish()


class IsAliveHandler(BaseHandler, Base):

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self):

        stream = self.get_argument("stream")

        logging.getLogger('pipeline_api').debug("Request from "+self.request.remote_ip+": Is alive "+stream+"?")

        result = yield tornado.gen.Task(self.send, message={"signal": "is_alive", "stream":stream}, unblock=True)
        print('!!!!!', result)

        self.write(result)
        self.finish()

class PlaylistUpdateHandler(BaseHandler, Base):

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self):

        stream = self.get_argument("stream")
        group = self.get_argument("group")

        logging.getLogger('pipeline_api').debug("Request from "+self.request.remote_ip+
                                                ": Playlist update on stream "+stream+", group "+group)

        result = yield tornado.gen.Task(self.send, message={"signal": "playlist_update", "stream":stream, "group":group}, unblock=True)

        self.write(result)
        self.finish()


class RunCommandHandler(BaseHandler, Base):

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self):

        command = self.get_argument("command")

        logging.getLogger('pipeline_api').debug("Request from "+self.request.remote_ip+": Running command "+command)

        result = yield tornado.gen.Task(self.send, message={"signal": "run_command", "command": command}, unblock=True)


        self.write(result)
        self.finish()
