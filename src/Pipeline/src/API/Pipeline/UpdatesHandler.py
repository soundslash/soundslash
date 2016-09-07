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
import cStringIO
import StringIO
import pylzma
import simplejson as json

from Model.BaseThreaded import BaseThreaded
from API.Pipeline.BaseHandler import BaseWebSocketHandler
from Model.Streaming.StreamBin import StreamBin
from Framework.Base import *

class UpdatesHandler(BaseWebSocketHandler, Base):

    def open(self):
        logging.getLogger('pipeline_api').debug("UpdatesHandler: New connection from "+self.request.remote_ip)
        self.metadata = False


    def check_origin(self, origin):
        return True

    @asynchronous
    def on_message(self, message):

        if self.metadata is False:
            try:
                metadata = json.loads(unicode(message))
                self.metadata = metadata
                logging.getLogger('pipeline_api').debug("UpdatesHandler: Received metadata "+unicode(self.metadata))

            except:
                logging.getLogger('pipeline_api').debug("UpdatesHandler: Problem with parsing metadata "+unicode(message))

            if self.metadata is not False:

                result = yield task(self.send, message={"signal": "register_updates_observer",
                                                        "stream": self.metadata['stream_id'],
                                                        "handler": self}, unblock=True)

                self.write_message(json.dumps(result))

            # return
        else:

            try:
                message = json.loads(unicode(message))

            except:
                pass

            if "action" in message:
                if message["action"] == "notify_current_track":

                    result = yield task(self.send, message={"signal": "notify_current_track",
                                                            "stream": self.metadata['stream_id']
                    }, unblock=True)
                    self.write_message(json.dumps(result))

                if message["action"] == "next":
                    result = yield task(self.send, message={
                        "signal": "next",
                        "stream": self.metadata['stream_id'],
                        "fade_out": 1}, unblock=True)
                    self.write_message(json.dumps(result))

                if message["action"] == "update_buffer":
                    result = yield task(self.send, message={"signal": "update_buffer",
                                                            "stream": self.metadata['stream_id'],
                                                            "buffer": message}, unblock=True)
                    self.write_message(json.dumps(result))

                if message["action"] == "change_selection":
                    result = yield task(self.send, message={"signal": "change_selection",
                                                            "stream": self.metadata['stream_id']}, unblock=True)
                    self.write_message(json.dumps(result))

    @asynchronous
    def on_close(self):
        logging.getLogger('pipeline_api').debug("LiveHandler stream "+self.metadata["stream_id"]+": Connection closed")
        yield task(self.send, message={"signal": "unregister_updates_observer",
                                       "stream": self.metadata['stream_id'], "handler": self}, unblock=True)