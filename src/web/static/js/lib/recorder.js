(function (window) {

    var WORKER_PATH = '/static/js/lib/recorderWorker.js';

    var Recorder = function (source, cfg) {
        var config = cfg || {};
        var bufferLen = config.bufferLen || 4096;
        var flash = config.flash || false;
        var recording = false,
                currCallback;
        if (flash)
        {
            function onRecordingComplete() {
            }

            function onCaptureError() {
            }

            var decoder = new WAVDecoder();

            function flashonaudioprocess(samples) {
                if (!recording) return;

                var wavData = atob(samples);
                var decoded = decoder.decode(wavData);

                worker.postMessage({
                    command: 'record',
                    buffer: [
                        decoded.channels[0],
                        decoded.channels[0]
                    ]
                });
            }

            navigator.device.captureAudio(onRecordingComplete, onCaptureError, {
                raw: true, onsamples: flashonaudioprocess
            });
            var sampleRate = 8000;
        }
        else
        {
            this.context = source.context;
            var fromSampleRate = this.context.sampleRate;
            var sampleRate = cfg.sampleRate;

            // TODO CHROME
//            this.node = this.context.createJavaScriptNode(bufferLen, 2, 2);
            // TODO FF
            this.node = this.context.createScriptProcessor(bufferLen, 2, 2);
//            console.log(sampleRate);
        }

        var worker = new Worker(config.workerPath || WORKER_PATH);
        worker.postMessage({
            command: 'init',
            config: {
                sampleRate: sampleRate
            }
        });



        if (!flash) this.node.onaudioprocess = function (e) {
            if (!recording) return;

            var inputBuffer = e.inputBuffer.getChannelData(0);
            var resampler = new Resampler(fromSampleRate, sampleRate, 1, inputBuffer.length);
            var samples = resampler.resampler(inputBuffer);
//            console.log(samples);
//
//            for (var i = 0; i < samples.length; ++i) {
//                refillBuffer[i] = Math.ceil(samples[i] * 32768);
//            }

            worker.postMessage({
                command: 'record',
                buffer: [
                    samples,
                    samples
                ]
            });
        }

        this.configure = function (cfg) {
            for (var prop in cfg) {
                if (cfg.hasOwnProperty(prop)) {
                    config[prop] = cfg[prop];
                }
            }
        }

        this.record = function () {
            recording = true;
        }

        this.stop = function () {
            recording = false;
        }

        this.clear = function () {
            worker.postMessage({ command: 'clear' });
        }

        this.getBuffer = function (cb) {
            currCallback = cb || config.callback;
            worker.postMessage({ command: 'getBuffer' })
        }

        this.exportWAV = function (cb, type) {
            currCallback = cb || config.callback;
            type = type || config.type || 'audio/wav';
            if (!currCallback) throw new Error('Callback not set');
            worker.postMessage({
                command: 'exportWAV',
                type: type
            });
        }

        worker.onmessage = function (e) {
            var blob = e.data;
            currCallback(blob);
        }

        if (flash) {

        }
        else {
            source.connect(this.node);
            this.node.connect(this.context.destination);    //this should not be necessary
        }
    };

    Recorder.forceDownload = function (blob, filename) {
        var url = (window.URL || window.webkitURL).createObjectURL(blob);
        var link = window.document.createElement('a');
        link.href = url;
        link.download = filename || 'output.wav';
        var click = document.createEvent("Event");
        click.initEvent("click", true, true);
        link.dispatchEvent(click);
    }

    window.Recorder = Recorder;

})(window);
