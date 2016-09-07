
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

class LiveAdminHandler(AdminHandler):

    @tornado.web.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self, stream_id):

        stream = yield motor.Op(self.db.streams.find_one, {"_id": ObjectId(stream_id)},
                                {"reencoding":1, "name": 1, "default_program_id": 1, "_id": 1})

        program = yield motor.Op(self.db.programs.find_one, {"_id": ObjectId(stream["default_program_id"])},
                                 {"groups":1, "selection": 1, "_id": 0})

        group_id = program["groups"][0]

        stream["_id"] = unicode(stream["_id"])
        stream["id"] = unicode(stream["_id"])

        self.template_vars["program"] = program
        self.template_vars["group_id"] = group_id
        self.template_vars["stream"] = stream
        self.template_vars["live"] = True
        self.template_vars["menu"] = "streams"
        self.template_vars["submenu"] = "live"
        self.template_vars["stream_id"] = stream_id

        self.render("admin/live.html", **self.template_vars)



class LiveForwarderAdminHandler(tornado.websocket.WebSocketHandler, BaseHandler):

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



class UpdatesForwarderAdminHandler(tornado.websocket.WebSocketHandler, BaseHandler):

    def check_origin(self, origin):
        return bool(re.match(r'^.*?\.soundslash\.com', origin))

    def open(self):
        self.metadata = False

    @tornado.gen.coroutine
    def on_metadata(self):
        if "stream_id" in self.metadata:
            pr = PipelineRouter(self.db, self.metadata["stream_id"])
            server = yield tornado.gen.Task(pr.get_server)
            url = pr.get_updates_url(server)

            # websocket.enableTrace(True)
            cache_hash = url+"?stream_id="+self.metadata["stream_id"]

            if cache_hash in self.settings["ws_cache"]:
                self.client_receiver = self.settings["ws_cache"][cache_hash]
            else:
                # print "vyt"
                client = websocket.create_connection(url)
                # client = yield tornado.gen.Task(websocket.create_connection, url)
                # print "at"
                client.send(json.dumps(self.metadata))
                # print client

                self.client_receiver = ClientWSReceiver(cache_hash, client)
                self.client_receiver.start()
                self.settings["ws_cache"][cache_hash] = self.client_receiver

            self.client_receiver.add_handler(self)
            print(self.metadata)
            if "action" in self.metadata:
                print('send ', self.metadata)
                self.client_receiver.client.send(self.metadata)



    def on_message(self, message):
        # print('mess1 '+unicode(message), self.metadata)
        if self.metadata is False:
            try:
                self.metadata = json.loads(unicode(message))

            except:
                print "Metadata not parsed :("

            if self.metadata != False:
                self.on_metadata()

        else:
            if hasattr(self, "client_receiver"):
                self.client_receiver.client.send(unicode(message))


    def on_close(self):
        # self.client_receiver.close()
        self.client_receiver.close_handler(self)

class ClientWSReceiver(Thread):

    def __init__(self, cache_hash, client):
        Thread.__init__(self)
        self.message = {}
        self.closed = False
        self.handlers = []
        self.cache_hash = cache_hash
        self.client = client

    def add_handler(self, handler):
        self.handlers.append(handler)
        handler.write_message(self.message)

    def close_handler(self, handler):
        self.handlers.remove(handler)
        if (len(self.handlers) == 0):
            del handler.settings["ws_cache"][self.cache_hash]
            self.close()

    def close(self):
        self.closed = True
        self.client.close()

    def run(self):
        while not self.closed:
            try:
                message = self.client.recv()
            except:
                self.close()
                print "Error receiving"
            # print(message)
            # print('mess2 '+unicode(message))

            try:
                message = json.loads(unicode(message))
                self.message = dict(self.message.items() + message.items())
                for handler in self.handlers:
                    handler.write_message(message)
            except:
                print "Message failed to parse"



