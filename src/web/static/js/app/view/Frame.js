define(function (require) {
    "use strict";

    var playerView = require('view/PlayerView');
//        _ = require('text!/static/img/ss_bg_sexi_blur.jpg');
//        rollerView = require('view/Roller');

    return extend.View('singleton', function () {

        this.template = 'frame';
        this.append = 'body';

        this.initialize = function () {



            playerView.render();
            playerView.bg('/static/img/ss_bg_sexi.jpg');
//            rollerView.render();

            this.bpObj = $('#bottom-player');
            this.tbObj = $('#toolbar');
            this.tmObj = $('#top-menu');
            this.nObj = $('.notifications.top-right');
            this.fObj = $('.footer');
            this.mObj = $('.main');
        };

        this.mode1 = function () {
            $('.main').css('background-color', 'transparent');
            $('#toolbar > div').css('background-color', 'transparent');
        };
        this.mode1_2 = function () {
            playerView.bg('/static/img/ss_bg_sexi_blur.jpg');
//            $('#background-in').css('filter', 'blur(5px)');
        };
        this.mode2 = function () {
            $('.main').css('background-color', '');
            $('#toolbar > div').css('background-color', '');
        };


        this.events = function () {

            $('#top-menu').scrollToFixed({
                dontSetWidth: true,
                content: $('#content')[0]
            });
        };


        this.fill = function () {

//            var bp = this.bpObj.height();
//            if (this.bpObj.is(':hidden')) {
//                bp = 0;
//            }

            if (this.nObj.length === 0) {
                this.nObj = $('.notifications.top-right');
            }

            var height = $(window).height()
                -this.tmObj.height()
                -this.tbObj.height()
                +7 // -7px margin of .main
                +this.nObj.height()
//                -bp
                -this.fObj.height();

            if (height > 0)
                this.mObj.css('min-height', height+'px');
            else
                this.mObj.css('min-height', '0px');

            var dialog = $('.dialog');

            if (dialog.length >= 1) {
                var new_height = dialog.height()
                    +parseInt(dialog.css('top'))
                    -this.fObj.height()
                    -this.mObj.height()
                    +parseInt(this.mObj.css("margin-top").replace("px", ""));
                if (new_height > height)
                    this.mObj.css('min-height', new_height+'px');
            }
        };
    });
});