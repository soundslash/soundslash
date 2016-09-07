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
from Queue import Queue
from threading import Thread

from Framework.Base import *
from Model.Db import Db

__author__ = "Michal Bystricky"
__copyright__ = "Copyright 2013, Michal Bystricky"
__status__ = "Prototype"


class BridgeSink(gst.Element):

    _sinkpadtemplate = gst.PadTemplate ("sinkpadtemplate",
                                        gst.PAD_SINK,
                                        gst.PAD_ALWAYS,
                                        gst.caps_new_any())

    def __init__(self, queue):
        gst.Element.__init__(self)

        self.queue = queue

        gst.info('creating sinkpad')
        self.sinkpad = gst.Pad(self._sinkpadtemplate, "sink")
        gst.info('adding sinkpad to self')
        self.add_pad(self.sinkpad)

        gst.info('setting chain/event functions')
        self.sinkpad.set_chain_function(self.chainfunc)
        self.sinkpad.set_event_function(self.eventfunc)

    def chainfunc(self, pad, buffer):
        self.info("%s timestamp(buffer):%d" % (pad, buffer.timestamp))
        self.queue.put(buffer)
        return gst.FLOW_OK

    def eventfunc(self, pad, event):
        self.info("%s event:%r" % (pad, event.type))
        return True

gobject.type_register(BridgeSink)


class BridgeSource(gst.BaseSrc):
    __gsttemplates__ = (
        gst.PadTemplate("src",
                        gst.PAD_SRC,
                        gst.PAD_ALWAYS,
                        gst.caps_new_any()
        ),
    )

    def __init__(self, buffer):
        self.__gobject_init__()
        self.buffer = buffer

    def do_create(self, offset, size):

        print " L"+unicode(self.buffer.qsize())+"",

        try:
            buff = self.buffer.get(False)
            return gst.FLOW_OK, gst.Buffer(str(buff))

        except:
            return gst.FLOW_UNEXPECTED, None

gobject.type_register(BridgeSource)


class PipeBridge():

    def __init__(self, src_pipe, src_elm, dst_pipe, dst_elm):
        self.queue = Queue()

        bridge_sink = BridgeSink(self.queue)
        src_pipe.add(bridge_sink)
        gst.element_link_many(src_elm, bridge_sink)

        bridge_source = BridgeSource(self.queue)
        dst_pipe.add(bridge_source)
        gst.element_link_many(bridge_source, dst_elm)
