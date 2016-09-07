
__version__ = "0.2"

import pygst
pygst.require("0.10")
import gst
import gobject
gobject.threads_init()
from functools import partial
from threading import Thread


class AudioPreprocessor(Thread):

    caps = gst.caps_from_string("audio/x-raw-int, channels=2, endianness=1234, rate=44100, width=16, depth=16, signed=true")

    def __on_dynamic_pad(self, dbin, pad, islast, audioconverter=None):
        decode = pad.get_parent()
        decode.link(audioconverter)

    def __on_pad(self, comp, pad, audioconverter = None):
        decode = pad.get_parent()
        pipeline = decode.get_parent()
        decode.link(audioconverter)
        pipeline.set_state(gst.STATE_PLAYING)

    def __init__(self, tags, f, t, quality):
        Thread.__init__(self)

        self.tags = tags

        gnlcomposition = gst.element_factory_make("gnlcomposition")
        self.gnlcomposition = gnlcomposition
        audioconverter = gst.element_factory_make("audioconvert")
        gnlcomposition.connect("pad-added", partial(self.__on_pad, audioconverter = audioconverter))
        # gnlcomposition.connect("new-decoded-pad", partial(self.__on_dynamic_pad, audioconverter = audioconverter))
        filesrc = gst.element_factory_make("gnlfilesource", None)

        dur = tags["cut-end-at"]-tags["cut-start-at"]
        if dur > 0 and tags["cut-start-at"] != 0 and tags["cut-end-at"] != 0:

            filesrc.set_property("location", f)
            filesrc.set_property("start", tags["cut-start-at"])
            filesrc.set_property("duration", dur)
            self.tags["duration"] = dur
        else:
            # print "Discarding start/end silence removing "+unicode(tags["cut-start-at"])+"-"+unicode(tags["cut-end-at"])

            filesrc.set_property("location", f)
            filesrc.set_property("start", 0)
            # max 1 hour
            filesrc.set_property("duration", self.tags["duration"])


        gnlcomposition.add(filesrc)
        self.filesrc = filesrc



        audioresample = gst.element_factory_make("audioresample")
        audiofilter = gst.element_factory_make("capsfilter")
        audiofilter.set_property("caps", self.caps)


        self.pipe = gst.Pipeline("pipeline")


        audioconverter2 = gst.element_factory_make("audioconvert")

        rgvolume = gst.element_factory_make("rgvolume")
        self.rgvolume = rgvolume
        rgvolume.set_property("album-mode", 0)
        rgvolume.set_property("pre-amp", tags["replaygain-track-gain"])
        rgvolume.set_property("headroom", 60.0)
        rglimiter = gst.element_factory_make("rglimiter")


        tl = gst.TagList()
        # tl[gst.TAG_ALBUM_GAIN] = tags["replaygain-track-gain"]
        # tl[gst.TAG_ALBUM_PEAK] = tags["replaygain-track-peak"]

        # This do not work
        tl[gst.TAG_TRACK_GAIN] = tags["replaygain-track-gain"]
        tl["replaygain-track-gain"] = tags["replaygain-track-gain"]
        tl[gst.TAG_TRACK_PEAK] = tags["replaygain-track-peak"]
        tl["replaygain-track-peak"] = tags["replaygain-track-peak"]
        tl[gst.TAG_REFERENCE_LEVEL] = tags["replaygain-reference-level"]
        tl["replaygain-reference-level"] = tags["replaygain-reference-level"]
        event = gst.event_new_tag(tl)
        rgvolume_sink = rgvolume.get_pad("sink")
        rgvolume_sink.send_event(event)
        rgvolume.send_event(event)



        audioconverter3 = gst.element_factory_make("audioconvert")

        vorbisenc = gst.element_factory_make("vorbisenc")
        # [-0.1,1]
        # 64 = 0.1
        # 128 = 0.4
        # -q0 	64 kb/s
        # -q1 	80 kb/s
        # -q2 	96 kb/s
        # -q3 	112 kb/s
        # -q4 	128 kb/s
        # -q5 	160 kb/s
        # -q6 	192 kb/s
        # -q7 	224 kb/s
        # -q8 	256 kb/s
        # -q9 	320 kb/s
        # -q10 	500 kb/s

        # If we change quality we need to change it also in Pipeline
        vorbisenc.set_property("quality", quality)
        oggmux = gst.element_factory_make('oggmux')

        filesink = gst.element_factory_make("filesink")
        filesink.set_property("location", t)



        self.pipe.add(gnlcomposition, audioconverter, audioresample, audiofilter, audioconverter2, rgvolume, audioconverter3, rglimiter, vorbisenc, oggmux, filesink)

        gst.element_link_many(audioconverter, audioresample, audiofilter, audioconverter2, rgvolume, audioconverter3, rglimiter, vorbisenc, oggmux, filesink)

        bus = self.pipe.get_bus()
        bus.add_signal_watch()
        bus.connect("message::eos", self.bus_message_eos)
        # bus.connect("message", self.bus_message)

        self.pipe.set_state(gst.STATE_PLAYING)


    def run(self):
        self.mainloop = gobject.MainLoop()
        self.mainloop.run()

    # def bus_message(self, bus, message):
    #     # print message
    #     pass

    def bus_message_eos(self, bus, message):
        self.mainloop.quit()

        # format = gst.Format(gst.FORMAT_TIME)
        # duration = self.pipe.query_duration(format)[0]
        # self.tags["duration"] = duration

        print "Processing finished result-gain: "+unicode(self.rgvolume.get_property("result-gain"))+" target-gain: "+unicode(self.rgvolume.get_property("target-gain"))


