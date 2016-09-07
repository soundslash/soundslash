function init_updates() {

    window.position = 0;
    function count() {
        var timer = setInterval(function() {
            $('.position').html(format_seconds(window.position));
            $('.clock').html(format_epoch(window.clock));
            window.position++;
            window.clock++;
        }, 1000);
    }
    if (window.websockets === undefined) {
        count();
    }
    if (window.websockets) {
        window.websockets.close();
    }
    var websockets = new WebSocket("ws://"+location.host+"/ws/stream/updates.json");
    window.websockets = websockets;

    websockets.onopen = function () {
        console.log("Openened connection to websocket");

        websockets.send(JSON.stringify({
            stream_id: window.stream_id,
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
                window.position = message["playing"]["position"];
            else
                window.position = 0;
            $(".position").html(format_seconds(window.position));
            $(".duration").html(format_seconds(message["playing"]["duration"]/1000000000));
        }
        if ("buffer_update" in message) {
            var o = {results: message['buffer_update'], parent: "buffer"};
            $('.buffer-body').html(tmpl(
                    'template-buffer',
                    o
            ));
            $('.format-duration').each(function( index ) {
                $(this).html(format_seconds($(this).data('duration')/1000000000));
            });
            do_draggable();
        }
        if ("server_time" in message) {
            window.clock = message['server_time'];
        }
        if ("previous_update" in message) {
            var o = {results: message['previous_update'], parent: "previous"};
            $('.previous-body').html(tmpl(
                    'template-buffer',
                    o
            ));
            $('.format-duration').each(function( index ) {
                $(this).html(format_seconds($(this).data('duration')/1000000000));
            });
            do_draggable();
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

}

function next() {
    window.websockets.send(JSON.stringify({"action": "next"}));
}

function change_selection() {
    window.websockets.send(JSON.stringify({"action": "change_selection"}));

}


function update_buffer() {
    var bufferArray = [];
    $("#buffer-form .about input[name=id]").each( function () {
        bufferArray.push($(this).val());
    });
    window.websockets.send(JSON.stringify({action: "update_buffer", buffer: bufferArray}));
}