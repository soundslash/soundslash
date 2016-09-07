
__version__ = "0.2"

import re
import tornado.web
import tornado.gen
import tornado.websocket
import motor
import websocket
from bson.objectid import ObjectId
import simplejson as json
import base64
from threading import Thread

from controller.BaseHandler import BaseHandler
from controller.admin.AdminHandler import AdminHandler
from controller.PipelineRouter import PipelineRouter

class LiveHandler(AdminHandler):

    @tornado.web.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):

        stream_id = self.get_argument("stream_id")

        stream = yield motor.Op(self.db.streams.find_one, {"_id": ObjectId(stream_id)},
                                {"reencoding":1,
                                 "name": 1,
                                 "default_program_id": 1,
                                 "fav_group_id": 1,
                                 "picture": 1,
                                 "_id": 1})

        program = yield motor.Op(self.db.programs.find_one, {"_id": ObjectId(stream["default_program_id"])},
                                 {"groups":1, "selection": 1, "_id": 0})

        group_id = program["groups"][0]

        stream["_id"] = unicode(stream["_id"])

        self.write({
            "program": program,
            "group_id": group_id,
            "stream": stream
        })
        self.finish()



class LiveForwarderHandler(tornado.websocket.WebSocketHandler, BaseHandler):

    def open(self):
        self.metadata = False

    def check_origin(self, origin):
        return bool(re.match(r'^.*?\.soundslash\.com', origin))


    @tornado.gen.engine
    def on_metadata(self):

        if "stream_id" in self.metadata:

            stream = yield motor.Op(self.db.streams.find_one, {"_id": ObjectId(self.metadata["stream_id"])},
                                    {"reencoding":1, "_id": 0})

            if stream['reencoding']:

                pr = PipelineRouter(self.db, self.metadata["stream_id"])
                server = yield tornado.gen.Task(pr.get_server)
                url = pr.get_live_url(server)

                # websocket.enableTrace(True)
                self.client = websocket.create_connection(url)
                self.client.send(json.dumps(self.metadata))
            else:

                self.close()

    def on_message(self, message):
        # print self.metadata
        if self.metadata is False:
            try:
                self.metadata = json.loads(unicode(message))

            except:
                print "Metadata not parsed :("

            if self.metadata != False:
                self.on_metadata()

        else:
            if hasattr(self, "client"):
                self.client.send(base64.b64encode(message))

    def on_close(self):
        self.client.close()



class UpdatesForwarderHandler(tornado.websocket.WebSocketHandler, BaseHandler):

    def open(self):
        self.metadata = False

    @tornado.gen.coroutine
    def on_metadata(self):
        if "stream_id" in self.metadata:
            pr = PipelineRouter(self.db, self.metadata["stream_id"])
            server = yield tornado.gen.Task(pr.get_server)
            url = pr.get_updates_url(server)

            # websocket.enableTrace(True)
            self.client = websocket.create_connection(url)
            self.client.send(json.dumps(self.metadata))

            self.client_receiver = ClientWSReceiver(self)
            self.client_receiver.start()


    def check_origin(self, origin):
        return bool(re.match(r'^.*?\.soundslash\.com', origin))

    def on_message(self, message):
        if self.metadata is False:
            try:
                self.metadata = json.loads(unicode(message))

            except:
                print "Metadata not parsed :("

            if self.metadata != False:
                self.on_metadata()

        else:
            if hasattr(self, "client"):
                self.client.send(unicode(message))


    def on_close(self):
        # self.client_receiver.close()
        self.client.close()

class ClientWSReceiver(Thread):

    def __init__(self, handler):
        Thread.__init__(self)
        self.closed = False
        self.handler = handler

    def close(self):
        try:
            self.handler.client.close()
        except:
            pass
        self.closed = True

    def run(self):
        while not self.closed:
            try:
                message = self.handler.client.recv()

            except:
                self.close()
                print "Error receiving"

            try:

                message = json.loads(unicode(message))
                self.handler.write_message(message)
            except:
                print "Message failed to parse"



