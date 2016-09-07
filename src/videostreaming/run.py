#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, os
import pygst

pygst.require("0.10")
import gst
import time
import datetime

from threading import Thread

import gtk
# this is very important, without this, callbacks from gstreamer thread
# will messed our program up
gtk.gdk.threads_init()

# gst-launch-0.10 v4l2src ! ffmpegcolorspace ! videoscale ! video/x-raw-yuv,width=320,height=240 ! theoraenc quality=16 ! oggmux ! shout2send ip=127.0.0.1 port=8000 password=hackme mount=radio2
#gst-launch-0.10 v4l2src device=/dev/video1 ! ffmpegcolorspace ! videoscale ! video/x-raw-yuv,width=640,height=480 ! theoraenc quality=16 ! oggmux name=mux alsasrc ! queue ! audioconvert ! queue ! vorbisenc ! queue ! mux. mux. ! shout2send ip=127.0.0.1 port=8000 password=hackme mount=radio2

class Player(Thread):

    caps = gst.Caps("video/x-raw-yuv, width=480, height=320, framerate=30/1")

    def __init__(self):
        Thread.__init__(self)

    def play(self):

        pipeline = gst.Pipeline("player")
        v4l2src = gst.element_factory_make("v4l2src", "source")
        v4l2src.set_property("device", "/dev/video0")

        pngdec = gst.element_factory_make("pngdec", "pngdec")
        pngsrc = gst.element_factory_make("filesrc", "pngsrc")
        pngsrc.set_property("location", "s.png")
        videobox = gst.element_factory_make("videobox", "videobox")
        videobox.set_property("border-alpha", 0)
        videobox.set_property("alpha", 1)
        videobox.set_property("left", -10)
        videobox.set_property("top", -10)
        alphacolor = gst.element_factory_make("alphacolor", "alphacolor")
        imagefreeze = gst.element_factory_make("imagefreeze", "imagefreeze")

        videomixer = gst.element_factory_make("videomixer", "videomixer")

        ffmpeg1 = gst.element_factory_make('ffmpegcolorspace', "ffmpeg1")
        ffmpeg2 = gst.element_factory_make('ffmpegcolorspace', "ffmpeg2")
        ffmpeg3 = gst.element_factory_make("ffmpegcolorspace", "ffmpeg3")
        ffmpeg4 = gst.element_factory_make('ffmpegcolorspace', "ffmpeg4")

        videoscale = gst.element_factory_make("videoscale")
        videorate = gst.element_factory_make("videorate")

        videofilter = gst.element_factory_make("capsfilter", "filter")
        videofilter.set_property("caps", self.caps)

        enc = gst.element_factory_make('theoraenc')
        enc.set_property("quality", 32)

        oggmux = gst.element_factory_make('oggmux')

        alsasrc = gst.element_factory_make("alsasrc", "alsasrc")
        vorbisenc = gst.element_factory_make("vorbisenc", "vorbisenc")
        vorbisenc.set_property("quality", 0.4)

        audioconvert = gst.element_factory_make("audioconvert", "audioconvert")

        audioconvert2 = gst.element_factory_make("audioconvert", "audioconvert2")

        audioresample = gst.element_factory_make("audioresample", "audioresample")

        interleave = gst.element_factory_make("interleave", "interleave")

        # save to file
        tee = gst.element_factory_make("tee")

        filesink = gst.element_factory_make("filesink")
        filename = str(datetime.datetime.now())+".ogv"
        filesink.set_property("location", filename)

        # threads
        queuea = gst.element_factory_make("queue", "queuea")
        queuev = gst.element_factory_make("queue", "queuev")
        queue2 = gst.element_factory_make("queue", "queue2")
        queue3 = gst.element_factory_make("queue", "queue3")

        # icecast
        shout = gst.element_factory_make('shout2send')
        shout.set_property("ip", "94.229.33.138")
        shout.set_property("password", "cafeeuropa2")
        shout.set_property("mount", "/video.ogg")

        #video
        pipeline.add(v4l2src, ffmpeg1, videoscale, videorate, videofilter, ffmpeg2, videomixer, ffmpeg3, enc, oggmux, tee, queue2, shout, queuev)
        pipeline.add(filesink, queue3)

        # image
        pipeline.add(pngsrc, pngdec, alphacolor, ffmpeg4, videobox, imagefreeze)

        #audio
        pipeline.add(alsasrc)
        pipeline.add(interleave, audioconvert2, audioresample, audioconvert, queuea, vorbisenc)

        #video
        gst.element_link_many(v4l2src, ffmpeg1, queuev, videoscale, videorate, videofilter, ffmpeg2, videomixer, ffmpeg3,
                              enc, oggmux, tee, queue2, shout)

        gst.element_link_many(tee, queue3, filesink)

        #image
        gst.element_link_many(pngsrc, pngdec, alphacolor, ffmpeg4, videobox, imagefreeze, videomixer)

        #audio
        gst.element_link_many(alsasrc, interleave)

        gst.element_link_many(interleave, audioconvert2, audioresample, audioconvert, queuea, vorbisenc, oggmux)

        pipeline.set_state(gst.STATE_PLAYING)

        raw_input("Press <ENTER> to continue.")


def main():
    player = Player()
    player.play()
    gtk.main()

if __name__ == "__main__":
    main()
