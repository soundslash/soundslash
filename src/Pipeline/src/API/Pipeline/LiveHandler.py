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
import wave
import cStringIO
import StringIO
import pylzma
import zipfile
import simplejson as json
import base64

from Framework.Base import *
from API.Pipeline.BaseHandler import BaseWebSocketHandler
from Model.Streaming.StreamBin import StreamBin

class LiveHandler(tornado.websocket.WebSocketHandler, Base):

    @asynchronous
    def start_live(self):
        yield task(self.send, message={"signal": "start_live", "stream": self.metadata["stream_id"], "appsrc": self.appsrc}, unblock=True)
        self.playing = True


    def check_origin(self, origin):
        return True

    def open(self):
        logging.getLogger('pipeline_api').debug("LiveHandler: New connection from "+self.request.remote_ip+
                                                ": Start receiving audio live messages")
        self.messages_count = 0
        self.buffer = []
        self.playing = False
        self.messages_buf = 3
        self.metadata = False

        self.appsrc = gst.element_factory_make('appsrc')


    def on_message(self, message):
        if self.metadata is False:
            try:
                metadata = json.loads(unicode(message))
                self.metadata = metadata

                logging.getLogger('pipeline_api').debug("LiveHandler: Received metadata "+unicode(self.metadata))

            except:
                logging.getLogger('pipeline_api').debug("LiveHandler: Problem with parsing metadata "+unicode(message))
                pass

            return

        self.messages_count += 1
        if message:

            output = cStringIO.StringIO(base64.b64decode(message))
            z = zipfile.ZipFile(output, "r")
            decompressed = z.open("part.wav")
            data = decompressed.read()
            output = cStringIO.StringIO(data)
            try:
                w = wave.open(output, 'rb')
            except:
                # skip on bad wav
                self.messages_count -= 1
                return
            self.buffer.append( [w.getparams(), w.readframes(w.getnframes())] )
            w.close()
            output.close()
            decompressed.close()
            z.close()

            logging.getLogger('pipeline_api').debug("LiveHandler: Received audio file NO "+
                                                    unicode(self.messages_count)+" of length "+unicode(len(message)))

            if (self.messages_count == self.messages_buf):
                wav = StringIO.StringIO()
                output = wave.open(wav, 'wb')
                output.setparams(self.buffer[0][0])
                output.setnframes(268435455)
                for b in range(len(self.buffer)):
                    output.writeframesraw(self.buffer[b][1])
                self.buffer = []
                wav.seek(0)
                data = wav.read()
                # data = open(r'/home/dash/Pipeline/samples/nyan.ogg', 'rb').read()
                buf = gst.Buffer(data)
                self.appsrc.emit('push-buffer', buf)
                self.start_live()
                output.close()

            if (self.messages_count > self.messages_buf):
                buf = gst.Buffer(str(self.buffer[0][1]))
                self.appsrc.emit('push-buffer', buf)
                self.buffer = []

    @asynchronous
    def on_close(self):
        logging.getLogger('pipeline_api').debug("LiveHandler stream "+self.metadata["stream_id"]+": Connection closed")

        yield task(self.send, in_context="LiveStreaming", message={
            "signal": "stop_live_"+self.metadata["stream_id"],
            "appsrc": self.appsrc}, unblock=True)

        self.playing = False
        self.buffer = []
        self.messages_count = 0

