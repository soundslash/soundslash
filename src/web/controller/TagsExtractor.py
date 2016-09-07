
__version__ = "0.2"

import pygst
pygst.require("0.10")
import gst
import gobject
gobject.threads_init()
from functools import partial
from threading import Thread

class TagsExtractor(Thread):

    caps = gst.caps_from_string("audio/x-raw-int, channels=2, endianness=1234, rate=44100, width=16, depth=16, signed=true")

    def __init__(self, filename):
        Thread.__init__(self)

        # rganalysis

        self.tags = {}
        self.start_at = None
        self.end_at = None

        filesrc = gst.element_factory_make("filesrc", None)
        filesrc.set_property("location", filename)

        audioconverter = gst.element_factory_make("audioconvert")

        decodebin = gst.element_factory_make("decodebin")
        decodebin.connect("new-decoded-pad", partial(self.__on_dynamic_pad, audioconverter = audioconverter))

        audioresample = gst.element_factory_make("audioresample")

        cutter = gst.element_factory_make("cutter")
        # cutter.set_property("leaky", 0)
        # cutter.set_property("pre-length", 0)
        # cutter.set_property("run-length", 0)
        # cutter.set_property("threshold", 1)
        cutter.set_property("threshold-dB", -40)

        rganalysis = gst.element_factory_make("rganalysis")

        fakesink = gst.element_factory_make("fakesink")

        self.pipe = gst.Pipeline("pipeline")

        self.pipe.add(filesrc, decodebin)
        self.pipe.add(audioconverter, audioresample, cutter, rganalysis, fakesink)

        gst.element_link_many(filesrc, decodebin)
        gst.element_link_many(audioconverter, audioresample, cutter, rganalysis, fakesink)


        bus = self.pipe.get_bus()
        bus.add_signal_watch()
        bus.connect("message", self.bus_message)
        bus.connect("message::tag", self.bus_message_tag)
        bus.connect("message::state-changed", self.bus_message_state_changed)
        bus.connect("message::eos", self.bus_message_eos)
        bus.connect("message::element", self.bus_message_element)


        self.pipe.set_state(gst.STATE_PLAYING)

        self.pipe.get_state()
        format = gst.Format(gst.FORMAT_TIME)
        duration = self.pipe.query_duration(format)[0]
        self.tags["duration"] = duration


    def run(self):
        self.mainloop = gobject.MainLoop()
        self.mainloop.run()

    def bus_message(self, bus, message):
        pass


    def bus_message_element(self, bus, message):
        if message.structure.has_key('above') and message.structure['above'] == True and self.start_at == None:
            self.start_at = message.structure['timestamp']
        if message.structure.has_key('above') and message.structure['above'] == False:
            self.end_at = message.structure['timestamp']

    def bus_message_tag(self, bus, message):
        taglist = message.parse_tag()
        #put the keys in the dictionary
        for key in taglist.keys():
            self.tags[key] = taglist[key]

    def bus_message_state_changed(self, bus, message):
        old, new, pending = message.parse_state_changed()
        # force to play pipeline in case of STOP


    def bus_message_eos(self, bus, message):
        if self.start_at == None: self.start_at = 0
        if self.end_at == None: self.end_at = 0
        self.tags["cut-start-at"] = self.start_at
        self.tags["cut-end-at"] = self.end_at
        self.mainloop.quit()
        # print "Found tags "+unicode(self.tags)


    def __on_dynamic_pad(self, dbin, pad, islast, audioconverter=None):
        decode = pad.get_parent()
        decode.link(audioconverter)
