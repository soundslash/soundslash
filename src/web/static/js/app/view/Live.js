define(function (require) {
    "use strict";

    var user = require('model/User'),
        browser = require('view/Browser'),
        frameView = require('view/Frame'),
        Stream = require('model/Stream'),
        dialog = require('view/Dialog'),


        _ = require('lib/deflate'),
        _ = require('lib/recorder'),
        _ = require('lib/recorderWorker'),
        _ = require('lib/swfobject');

    window.__MediaCaptureUI = {
        stylesheet: "/static/js/styles/lib/mediacapture.css", swf: "/static/assets/MediaCapture.swf", timeout: 500
    };
    var
        _ = require('lib/mediacapture'),
        _ = require('lib/audiofile'),
        _ = require('lib/xaudio'),
        _ = require('lib/zip'),
        _ = require('lib/deflate');




    return window.live = extend.View('singleton', function () {

        this.template = 'stream-live';
        this.append = '#radio-content';


        this.afterRenderCb = [
            function () {
                frameView.fill();
            }];

        var _this = this;

        this.initialize = function () {

            $('#top-menu .icon').removeClass('active');
            $('#top-menu .icon.microphone').addClass('active');

            $('.stream-menu a.active').removeClass('active');
            $('.stream-menu a.stream-menu-live').addClass('active');

            $('.lightblue-menu h1.menu-title').html('Live');


            browser.initBrowser();
        };

        this._events = function () {

        };


        this.initLive = function() {
            if ($('.live-holder').is( ":hidden" ) == true) {
                $('.live-holder').show();

                this.startCapture();
            } else {
                $('.live-holder').hide();
            }
        };

        this.doStartCapture = function (method)
        {
            var recording = null;
            var recorder;
            var websockets;
            var _this = this;

            if (method == "gUM")
            {
                navigator.getMedia = ( navigator.getUserMedia ||
                    navigator.webkitGetUserMedia ||
                    navigator.mozGetUserMedia ||
                    navigator.msGetUserMedia );

                navigator.getMedia (
                    {
                        video: false,
                        audio: true
                    },
                    // successCallback
                    function(stream) {
                        var contextClass = (window.AudioContext ||
                            window.webkitAudioContext ||
                            window.mozAudioContext ||
                            window.oAudioContext ||
                            window.msAudioContext );
                        if (contextClass) {
                            var context = new contextClass();
                            var mediaStreamSource = context.createMediaStreamSource(stream);
                            recorder = new Recorder(mediaStreamSource,{sampleRate:16000});
                        }
                        else {
                            console.log("Not supported");
                        }
                    },
                    // errorCallback
                    function(err) {
                        console.log("The following error occured: " + err);
                    }
                );
            }
            else
            {
                recorder = new Recorder(null, {flash: true});
            }

            var stream = new Stream();
            stream.getStream().done(function (stream_obj) {

                $('#record').click(function() {

                    if (recording == null || recording == false)
                    {

                        websockets = new WebSocket("ws://"+location.host+"/ws/stream/live/data.json");
                        websockets.onopen = function () {
                            console.log("Openened connection to websocket");

                            websockets.send(JSON.stringify({stream_id: stream_obj.stream._id
                                //,loop: ["5253fc2d6e955213f68a478e"]
                            }));

                            if (recording == null)
                                recorder.record();

                            // export a wav every half second, so we can send it using websockets
                            if (recording == null)
                            {
                                var intervalKey = setInterval(function() {
                                    recorder.exportWAV(function(blob) {
                                        if (recording)
                                            _this.zipBlob("part.wav", blob, function(zippedBlob) {
                                                websockets.send(zippedBlob);
                                            });

                                    });
                                }, 1000);
                            }
                            recording = true;

                            $('#record .p-danger').html("Stop");

                            $('.top-right').notify({
                                message: { text: 'Started streaming!' },
                                type: "success"
//                    type: "error"
//                    type: "info"
                            }).show();
                        };
                        websockets.onclose = function () {
                            console.log("Closed connection to websocket");

                            $('.top-right').notify({
                                message: { text: 'Connection closed!' },
//                    type: "success"
//                    type: "error"
                                type: "danger"
                            }).show();
                        };

                    }
                    else
                    {
                        recording = false;
                        websockets.close();
                        $('#record .p-danger').html("Record");
                    }

                });
            });

        };

        this.startCapture = function () {

            var Context = window["webkitAudioContext"] || window["mozAudioContext"] || window["AudioContext"];
            var supported = typeof(Context) !== "undefined";
            supported && !!(new Context()).createMediaElementSource;

            if (supported) {
                this.doStartCapture("gUM");
                return;
            }

            if(swfobject.hasFlashPlayerVersion("1")) {

                dialog.show('Not supported', '<div class="flash-allow-holder"></div>', function (dialog) {
                    dialog.removeClass('dialog');
                    $('#mic-use').css('position', 'fixed');
                    $('#mic-use').css("overflow", "hidden");
                    $('#mic-use').css('bottom', '0px');
                    $('#mic-use').css('left', '0px');
                    $('#mic-use').css('opacity', '0');
                    $('#mic-use').css('width', '2px');
                    $('#mic-use').css('height', '2px');
                    $('#mic-use').css('z-index', '100');

                    $('.main .loading-bg').remove();
                    return false;
                });

                var v = new View(), _this = this;
                v.template = 'stream-live-flash';
                v.append = '.flash-allow-holder';
                v.afterRender(function () {
                    _this.doStartCapture("flash");
                });
                v.render({});

            } else {

                $('.top-right').notify({
                    type: 'danger',
                    message: { text: "Your browser does not support HTML 5 or Flash Player." },
                    fadeOut: { enabled: true, delay: 10000 }
                }).show();

                $('.live-holder').hide();
            }

        };

        this.zipBlob = function (filename, blob, callback) {
            // use a zip.BlobWriter object to write zipped data into a Blob object
            zip.createWriter(new zip.BlobWriter("application/zip"), function(zipWriter) {
                // use a BlobReader object to read the data stored into blob variable
                zipWriter.add(filename, new zip.BlobReader(blob), function() {
                    // close the writer and calls callback function
                    zipWriter.close(callback);
                }, function(a,b){}, {level:9});
            }, onerror);
        };




    });
});