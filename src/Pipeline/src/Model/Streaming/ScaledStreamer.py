
import pygst
pygst.require("0.10")
import gst
import time
import gobject
gobject.threads_init()
import os
import logging
import datetime
from threading import Thread
from bson.binary import Binary

from Framework.Base import *
from Model.BaseThreaded import BaseThreaded
from Model.Streaming.FileSource import FileSource
from Model.Streaming.QuietSource import QuietSource
from Model.Streaming.EncodedScheduler import EncodedScheduler
from Model.Streaming.ScaledTailBin import ScaledTailBin


class ScaledStreamer():

    # def scale(self, server, quality=None, sync=0):
    def scale(self, server, quality=None, sync=0, init=False):

        self.lock.acquire()

        # if quality is None:
        #     quality = self.default_quality
        #
        # if quality not in self.tees:
        #     self.lock.release()
        #     return {"error": "No such quality"}

        # db = ScaledTailBin(self, self.tees[quality], server, sync)

        if hasattr(self, 'tees') and quality is not None:
            db = ScaledTailBin(self, self.tees[quality], server, sync, init)
        else:
            db = ScaledTailBin(self, self.tee, server, sync, init)

        db.set_metadata(self.streamname, self.description, self.genre)
        db.link_and_unblock()

        self.tailbins.append(db)

        if server is not None:
            self.servers[unicode(server["_id"])] = db

            self.lock.release()

            return {
                "public_ip": server["public_ip"],
                "port": server["port"],
                "mount": server["streaming"]["mount"]
            }
        else:

            self.lock.release()

            return {
                "msg": "Fakesink added",
            }

    def is_sync(self, stream):
        if stream not in self.servers:
            return False
        elif self.servers[stream].sync == 1:
            return True
        else:
            return False

    def rescale(self, servers):

        result = {
            "freed": []
        }

        self.lock.acquire()

        for server in servers:

            server["_id"] = unicode(server["_id"])

            # keep sync=1 element, because he is one that handling realtime sync
            if server["_id"] in self.servers and self.servers[server["_id"]].sync == 0:

                res = self.servers[server["_id"]].unlink_and_dispose()

                if res:
                    del self.servers[server["_id"]]

                    result["freed"].append({
                        "id": server["_id"],
                        "public_ip": server["public_ip"],
                        "port": server["port"],
                        "mount": server["streaming"]["mount"]
                    })



        self.lock.release()

        return result

    @asynchronous
    def dump_dot_file(self, respond, basename='pipeline'):
        # GST_DEBUG_DUMP_DOT_DIR=/tmp/
        directory = os.environ.get('GST_DEBUG_DUMP_DOT_DIR', None)
        if directory:
            dotfile = os.path.join(directory, '%s.dot' %basename)
            pngfile = os.path.join(directory, '%s.png' %basename)
            if os.path.isfile(dotfile):
                logging.getLogger('pipeline').debug('Removing existing dotfile %s' %dotfile)
                os.remove(dotfile)
            if os.path.isfile(dotfile):
                logging.getLogger('pipeline').debug('Removing existing pngfile %s' %pngfile)
                os.remove(pngfile)

            logging.getLogger('pipeline').debug('Dumping graph to %s' %dotfile)
            gst.DEBUG_BIN_TO_DOT_FILE(self.pipe, gst.DEBUG_GRAPH_SHOW_ALL, basename)
            dot = '/usr/bin/dot'
            os.system(dot + " -Tpng -o " + pngfile + " " + dotfile)

            logging.getLogger('pipeline').debug('Reading image file')
            with open(pngfile, 'r') as content_file:
                content = content_file.read()

            logging.getLogger('pipeline').debug('Inserting image file to database')
            image_id = self.db.images.insert({
                "format": "jpg",
                "template": "default",
                "tags": ["delete"],
                "created_at": datetime.datetime.utcnow(),
                "data": Binary(content)
            })

            respond({"temp_dotfile": dotfile, "temp_pngfile": pngfile, "temp_dbpath": "/image.jpg?id="+unicode(image_id)})
        else:
            logging.getLogger('pipeline').debug("You need to define the GST_DEBUG_DUMP_DOT_DIR env var to dump a .dot graph of the running pipeline")
            respond(None)

