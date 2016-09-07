define(function (require) {
    "use strict";

    var
//        browser = require('view/Browser'),
        Buffer = require('view/Buffer'),
        _ = require('app/helpers/time');

    return window.updates = extend.Model('singleton', function () {

        this.initialize = function (stream_id) {
            this.stream_id = stream_id;
            var _this = this;

            _this.position = 0;
            function count() {
                var timer = setInterval(function() {
                    $('.position').html(format_seconds(_this.position));
                    $('.clock').html(format_epoch(_this.clock));
                    _this.position++;
                    _this.clock++;
                }, 1000);
            }
            if (_this.websockets === undefined) {
                count();
            }
            if (_this.websockets) {
                _this.websockets.close();
            }
            var websockets = new WebSocket("ws://"+location.host+"/ws/stream/updates.json");
            _this.websockets = websockets;

            websockets.onopen = function () {
                console.log("Openened connection to websocket");

                websockets.send(JSON.stringify({
                    stream_id: _this.stream_id,
                    action: "notify_current_track"
                }));

            };
            websockets.onclose = function () {
                console.log("Closed connection to websocket");

//        $('.top-right').notify({
//            message: { text: 'Connection closed!' },
//    //                    type: "success"
//    //                    type: "error"
//            type: "danger"
//        }).show();
            };
            websockets.onmessage = function (event) {
//        console.log(event.data);
                var message = jQuery.parseJSON(event.data);
                if ("playing" in message) {
                    $(".live-details .artist").html(message["playing"]["artist"]);
                    $(".live-details .title").html(message["playing"]["title"]);
                    if ("position" in message["playing"])
                        _this.position = message["playing"]["position"];
                    else
                        _this.position = 0;
                    $(".position").html(format_seconds(_this.position));
                    $(".duration").html(format_seconds(message["playing"]["duration"]/1000000000));
                }
                if ("buffer_update" in message) {
                    var b = new Buffer();
                    b.wrap_el = false;
                    b.append = '.buffer-body';
                    b.afterRender(function () {

                        $('.format-duration').each(function( index ) {
                            $(this).html(format_seconds($(this).data('duration')/1000000000));
                        });
                        browser.do_draggable();
                    });
                    b.render({results: message['buffer_update'], parent: "buffer"});
                }
                if ("server_time" in message) {
                    _this.clock = message['server_time'];
                }
                if ("previous_update" in message) {

                    var b = new Buffer();
                    b.wrap_el = false;
                    b.append = '.previous-body';
                    b.afterRender(function () {

                        $('.format-duration').each(function( index ) {
                            $(this).html(format_seconds($(this).data('duration')/1000000000));
                        });
                        browser.do_draggable();
                    });
                    b.render({results: message['previous_update'], parent: "previous"});


                }
                if ("selection" in message) {

                    if (message["selection"] == "shuffle") {
                        var text = "Shuffle";
                    } else {
                        var text = "Sequence";
                    }

                    var a = $('<a href="#" onclick="change_selection();return false;">'+text+'</a>')
                    $('.track-selection').html(a);
                }
                if ("error" in message) {
                    $('.top-right').notify({
                        message: { text: message["error"] },
                        //                    type: "success"
                        //                    type: "error"
                        type: "danger"
                    }).show();
                }
            }
        };


        this.next = function() {
            this.websockets.send(JSON.stringify({"action": "next"}));
        };

        this.change_selection = function() {
            this.websockets.send(JSON.stringify({"action": "change_selection"}));

        };


        this.update_buffer = function() {
            var bufferArray = [];
            $("#buffer-form .about input[name=id]").each( function () {
                bufferArray.push($(this).val());
            });
            this.websockets.send(JSON.stringify({action: "update_buffer", buffer: bufferArray}));
        };

    });
});