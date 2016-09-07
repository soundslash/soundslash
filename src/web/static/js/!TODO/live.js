function doStartCapture(method)
{
    var recording = null;
    var recorder;
    var websockets;

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

    $('#record').click(function() {

        if (recording == null || recording == false)
        {

            websockets = new WebSocket("ws://"+location.host+"/ws/stream/live.json");
            websockets.onopen = function () {
                console.log("Openened connection to websocket");

                websockets.send(JSON.stringify({stream_id: window.stream_id, loop:
                    ["5253fc2d6e955213f68a478e"]
                }));

                if (recording == null)
                    recorder.record();

                // export a wav every half second, so we can send it using websockets
                if (recording == null)
                {
                    intervalKey = setInterval(function() {
                        recorder.exportWAV(function(blob) {
                            if (recording)
                                zipBlob("part.wav", blob, function(zippedBlob) {
                                    websockets.send(zippedBlob);
                                });

                        });
                    }, 1000);
                }
                recording = true;

                $('#record').html("Stop");

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
                    type: "error"
                }).show();
            };

        }
        else
        {
            recording = false;
            websockets.close();
            $('#record').html("Record");
        }

    });

}

function startCapture() {

    var Context = window["webkitAudioContext"] || window["mozAudioContext"] || window["AudioContext"];
    var supported = typeof(Context) !== "undefined";
    supported && !!(new Context()).createMediaElementSource;

    if (supported) {
        doStartCapture("gUM");
        return;
    }

    if(swfobject.hasFlashPlayerVersion("1")) {

        UI.dialog('Not supported', tmpl('template-live-flash', {}), function (dialog) {
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

        doStartCapture("flash");
    } else {

        $('.top-right').notify({
            type: 'danger',
            message: { text: "Your browser does not support HTML 5 or Flash Player." },
            fadeOut: { enabled: true, delay: 10000 }
        }).show();

        $('.live-holder').hide();
    }

}

function zipBlob(filename, blob, callback) {
    // use a zip.BlobWriter object to write zipped data into a Blob object
    zip.createWriter(new zip.BlobWriter("application/zip"), function(zipWriter) {
        // use a BlobReader object to read the data stored into blob variable
        zipWriter.add(filename, new zip.BlobReader(blob), function() {
            // close the writer and calls callback function
            zipWriter.close(callback);
        }, function(a,b){}, {level:9});
    }, onerror);
}
