define(function (require) {
    "use strict";

    var

        _ = require('lib/swfobject');

    return window.player = extend.View('singleton', function () {

        this.replace = false;
        this.template = 'player';
        this.append = 'body';

        this.initialize = function () {

//            this.show_player();
//            $('#bottom-player').scrollToFixed( {
//                bottom: 0,
//                dontSetWidth: true,
//                content: $('#content')[0]
//            });
//            this.hide_player();

        };

        this._events = function () {
            var _this = this;


            $('.slider').slider().on('slide', function(ev) {
                $('.slider .tooltip-inner').html(ev.value);
                _this.do_volume(ev.value);
            });
        };

        this.bg = function (img) {
            var only = true;
            if ($('#background-in').css('display') == 'none') {
                var bg_in = $('#background-in');
                var bg_out = $('#background-out');
            }
            if ($('#background-out').css('display') == 'none') {
                var bg_in = $('#background-out');
                var bg_out = $('#background-in');
            }
            if ($('#background-in').css('display') != 'none' && $('#background-out').css('display') != 'none') {
                return;
            }
            bg_in.css('opacity', 0);
            bg_in.css('display', 'block');
            bg_in.css('z-index', 3);
            bg_out.css('z-index', 2);
            if (img == null) {
                bg_in.css('background-image', 'url(/static/img/ss_bg_sexi.jpg)');
                bg_in.css('background-color', '');
//                bg_in.css('background-image', '');
//                bg_in.css('background-color', '#ffffff');
            } else {
                if (img.match("^/static")) {
                    bg_in.css('background-image', 'url('+img+')');
                } else {
                    bg_in.css('background-image', 'url(/image.jpg?id='+img+'&thumb=1440x900)');
                }

                var pomer_window_h = 1440;
                var pomer_window_w = 1440*$(window).height()/$(window).width();

                if (pomer_window_w > 900) {
                    bg_in.css('background-size', 'auto 100%');
                } else {
                    bg_in.css('background-size', '100% auto');

                }
                bg_in.css('background-color', 'none');
            }
            bg_in.animate({
                opacity: 1
            }, 1000, function(){
                bg_out.css('display', 'none');
            });
        };

        this.change_volume = function (volume) {
            if (this.is_html_supported()) {
                var audio = $('#player audio').get(0);
                audio.volume = volume/100;
            } else {
                if (this.is_flash_supported()) {
                    playflash.Volume(volume);
                } else {
                    console.log("Not supported");
                }
            }

        };

        this.do_play_stop = function (object) {
            if (this.playingObj != object && this.playing) {
                this.do_stop();
                $(this.playingObj).find('.glyphicon-stop').removeClass('glyphicon-stop').addClass('glyphicon-play');
            }
            if (this.playing) {
                this.do_stop();
                $(object).find('.glyphicon-stop').removeClass('glyphicon-stop').addClass('glyphicon-play');
            } else {

                if ($(object).data('url') != null)
                    this.do_play($(object).data('url'));

                if ($(object).attr('data-stream') != null)
                    this.play($(object).attr('data-stream'));

                $(object).find('.glyphicon-play').removeClass('glyphicon-play').addClass('glyphicon-stop');
                this.playingObj = object;
            }
        };

        this.do_stop = function () {
            if (this.is_html_supported()) {
                console.log("Pausing HTML player ...");
                var audio = $('#player audio');
                audio.removeAttr("src");
                audio.get(0).load();

                this.playing = false;
            } else {
                if (this.is_flash_supported()) {
                    console.log("Pausing FLASH player ...");
                    $('#player').html("<div id='playflash'></div>");

                    this.playing = false;
                } else {
                    console.log("Not supported");
                }
            }
        };

        this.do_play = function (url) {
            var o = {url: url+"?rand=" + (new Date()).getTime()},
                _this = this;

            if (this.is_html_supported()) {

                console.log("Starting HTML player ...");

                var v = new View();
                v.template = 'html-player';
                v.append = '#player';

                v.afterRender(function () {


                    var audio = $('#player audio');
                    audio.attr("src", url);
                    audio.get(0).load();



                    $('#player audio').get(0).oncanplaythrough = function canplay() {
                        $('#player audio').get(0).play();
                    };
                    $('#player audio').get(0).play();

                    _this.playing = true;
                });
                v.render(o);



            } else {
                if (this.is_flash_supported()) {

                    console.log("Starting new FLASH player ...");
                    var flashurl = "FOggPlayer.swf?url="+url+"&volume=100&external=true&play=true";
                    var flashvars = {};
                    var params = {};
                    var attributes = {};

                    swfobject.embedSWF("/static/assets/"+flashurl, "playflash", "0", "0", "9.0.0", "expressInstall.swf", flashvars, params, attributes);

                    this.playing = true;

                } else {
                    console.log("Not supported");
                }

            }
        };



        this.is_html_supported = function () {
            var a = document.createElement('audio');
            var is_html_supported = !!(a.canPlayType && a.canPlayType('audio/ogg;').replace(/no/, ''));
            if (this.forceFlash) return false; else return is_html_supported;
        };

        this.is_flash_supported = function () {
            var hasFlash = false;
            try {
                var fo = new ActiveXObject('ShockwaveFlash.ShockwaveFlash');
                if(fo) hasFlash = true;
            }catch(e){
                if(navigator.mimeTypes ["application/x-shockwave-flash"] != undefined) hasFlash = true;
            }
            return hasFlash
        };

        this.hide_player = function () {
            $('#bottom-player').hide();
            $('.bottom-player-spacer').hide();
        };

        this.show_player = function () {
            $('#bottom-player').show();
            $('.bottom-player-spacer').show();
        };

        this.play = function (id) {

            var _this = this;
            $.ajax({
                type: 'GET',
                url: "/play.json",
                data: {
                    streamId: id
                },
                success: function (data) {

                    if ('password' in data['stream']) {
                        var password = "&password="+encodeURIComponent(data['stream']['password']);
                    } else {
                        var password = '';
                    }

                    var addr = "http://" + data.public_ip + ":" + data.port + data.mount + "?&rand=" + (new Date()).getTime()+password;
                    _this.do_play(addr);
                    $('.player .name-wrap .stream').html(data.stream.name);
                    if (data.user.name == "") {
                        $('.player .details .user').html(data.user.email);
                    } else {
                        $('.player .details .user').html(data.user.name);
                    }
                    if (data.stream.picture) {
                        $('.player .pic img').attr('src', "/image.jpg?id="+data.stream.picture+"&thumb=65x65");
                    } else {
                        $('.player .pic img').attr('src', "/static/img/media_default.png");
                    }

                    $('.player.play').removeClass('play');
                    $('.player').addClass('stop');
                    $('.player a').attr('data-stream', id);
                    _this.receive_meta(id);
                    _this.bg(data.stream.cover_image);
                    _this.show_player();
                }
            });
        };

        this.stop = function () {
            this.do_stop();
            $('.player.stop').removeClass('stop');
            $('.player').addClass('play');
            this.hide_player();
            this.bg('#ffffff');
        };


        this.play_pause = function (object) {
            if (this.playing) {
                this.do_stop();
                $('.player.stop').removeClass('stop');
                $('.player').addClass('play');
                this.playingObj = false;
                this.bg(null);
            } else {
                this.play($(object).attr('data-stream'));
                this.playingObj = object;
            }
        };

        this.play_stop = function (object) {
            if (this.playing) {
                this.do_stop();
                $('.player.stop').removeClass('stop');
                $('.player').addClass('play');


                if ($(object).attr('data-stream') != $(this.playingObj).attr('data-stream')) {
                    this.play($(object).attr('data-stream'));
                    this.playingObj = object;
                } else {

                    this.bg(null);
                    this.playingObj = false;
                }
            } else {
                this.play($(object).attr('data-stream'));
                this.playingObj = object;
            }
        };

        this.append_image = function (id, klass, img) {
            $.ajax({
                type: 'GET', url: "/image.json",
                data: {
                    id: img
                },
                success: function(data)
                {
                    if (!data.error)
                    {
                        var img = $('<img>');
                        img.attr("src", data.data);
                        img.addClass(klass);
                        $('#'+id).append(img);
                    }
                }
            });
        };

        this.receive_meta = function (stream_id) {

            if (window.meta_ws !== undefined) {
                window.meta_ws.close();
            }

            var websockets = new WebSocket("ws://"+location.host+"/ws/stream/updates.json");
            window.meta_ws = websockets;

            websockets.onopen = function () {
                console.log("Receiving meta...");
                websockets.send(JSON.stringify({stream_id: stream_id}));
            };
            websockets.onclose = function () {
                console.log("Connection to meta closed...");
            };
            websockets.onmessage = function (event) {

                var message = jQuery.parseJSON(event.data);
                if ("playing" in message) {
                    $(".player .artist").html(message["playing"]["artist"]);
                    $(".player .title").html(message["playing"]["title"]);
                }
                if ("error" in message) {
                    $('.top-right').notify({
                        message: { text: message["error"] },
                        //                    type: "success"
                        //                    type: "error"
                        type: "danger"
                    }).show();
                }
            };


        };


    });
});

