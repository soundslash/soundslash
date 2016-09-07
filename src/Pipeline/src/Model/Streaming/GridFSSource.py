#!/usr/bin/env python

"""
GStremer source MongoDB GridFS.
"""

import pygst
pygst.require("0.10")
import gst
import time
import gobject
gobject.threads_init()
from mongokit import *
from bson.objectid import ObjectId
from threading import Thread
import gridfs
from noconflict import classmaker

from Framework.Base import *
from Model.Db import Db

__author__ = "Michal Bystricky"
__copyright__ = "Copyright 2013, Michal Bystricky"
__status__ = "Prototype"

class GridFSSource(Base, gst.BaseSrc):

    __metaclass__=classmaker()

    __gsttemplates__ = (
        gst.PadTemplate("src",
                        gst.PAD_SRC,
                        gst.PAD_ALWAYS,
                        gst.caps_new_any()
                        # gst.caps_from_string("application/ogg")
                        # gst.caps_from_string("audio/x-raw-int, channels=2, endianness=1234, rate=44100, width=16, depth=16, signed=true")
                        ),
    )

    blocksize = 4096
    fd = None

    def __init__(self, file_id):
        super(GridFSSource, self).__init__()
        self.__gobject_init__()
        self.curoffset = 0

        self.file_id = file_id

        # doc = self.db.conn.files.File()
        fs = gridfs.GridFS(self.db)
        self.fd = fs.get(ObjectId(file_id))

    # @asynchronous
    def do_create(self, offset, size):

        if offset != self.curoffset:
            self.fd.seek(offset, 0)

        # data = yield task(self.query, self.fd.read, self.blocksize)
        data = self.fd.read(self.blocksize)

        if data:
            self.curoffset += len(data)
            # respond(gst.FLOW_OK, gst.Buffer(data))
            return gst.FLOW_OK, gst.Buffer(data)
        else:
            # respond(gst.FLOW_UNEXPECTED, None)
            return gst.FLOW_UNEXPECTED, None

    def __del__(self):
        self.fd.close()

gobject.type_register(GridFSSource)
