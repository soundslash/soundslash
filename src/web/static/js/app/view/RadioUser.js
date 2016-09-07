define(function (require) {
    "use strict";

    var
        user = require('model/User'),
        frameView = require('view/Frame'),
        radioView = require('view/Radio');

    return extend.View('singleton', function () {

        this.template = 'radio-user';
        this.append = '.main';

        this.afterRenderCb = [
            function () {
                frameView.fill();
            }];

        var _this = this;

        this.initialize = function () {

            $('#top-menu .icon').removeClass('active');
            $('#top-menu .icon.microphone').addClass('active');

            $('#stream-menu, .highlight-menu a[href="#stream-menu"]').click(function () {
                if($('#stream-menu').hasClass('active')) {
                    $('.highlight-menu a[href="#stream-menu"]').removeClass('lightblue-bg');
                    $('#stream-menu').removeClass('active');
                    return false;
                } else {
                    $('.highlight-menu a[href="#stream-menu"]').addClass('lightblue-bg');
                }
            });


            radioView._snapper(user._user);
            this.resizable($('.lightblue-menu'));
        };


        this.resizable = function (element) {
            var _this = this;
            element.dblclick(function() {

                var min = '450px';
                var max = '768px';

                if ($('.container-fluid').css('max-width') === max) {
                    _this.resizeOneColumn();
                }

                if ($('.container-fluid').css('max-width') === min) {
                    _this.resizeTwoColumn();
                }

            });
        };

        this.resizeOneColumn = function () {

            var min = '450px';
            var max = '768px';

            if ($( document ).width() >= 768 && $('.container-fluid').css('max-width') === max) {

                $(document.head).find('.resize').remove();
                $(document.head).append('<style class="resize">'+
                    '.container-fluid,.max-width{max-width:'+min+'}'+
                    '.blocks .block{width:100%;display:block}'+
                    '</style>');


                $('.container-fluid, .max-width').css('transition', '1s');
                $('.container-fluid, .max-width').css('max-width', min);

                var t = setInterval(function () {
                    clearInterval(t);
                    frameView.fill();
                }, 1000);

//                $('.container-fluid, .max-width').stop().animate(css, {
//                    'duration': 500,
//                    'done': endOfAnimate
//                });
            }
        };


        this.resizeTwoColumn = function () {

            var min = '450px';
            var max = '768px';

            if ($( document ).width() >= 768 && $('.container-fluid').css('max-width') === min) {

                $('.container-fluid, .max-width').css('transition', '1s');
                $('.container-fluid, .max-width').css('max-width', max);

                var t = setInterval(function () {
                    clearInterval(t);

                    $(document.head).find('.resize').remove();
                    $(document.head).append('<style class="resize">'+
                        '.container-fluid,.max-width{max-width:'+max+'}'+
                        '.blocks{display:table;width:100%}'+
                        '.blocks .block{width:50%;display:table-cell;vertical-align:top}'+
                        '.blocks .block:first-child{padding-right:7px}'+
                        '.blocks .block:last-child{padding-left:7px}'+
                        '</style>');

                    frameView.fill();
                }, 1000);

//                $('.container-fluid, .max-width').stop().animate(css, {
//                    'duration': 500,
//                    'done': endOfAnimate
//                });

            }
        };


    });
});