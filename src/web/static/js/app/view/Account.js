
define(function (require) {
    "use strict";

    var user = require('model/User'),
        frameView = require('view/Frame'),
        knob = require('lib/jquery.knob.min');

    return extend.View('singleton', function () {

        this.template = 'user-account';
        this.append = '#account';

        this.afterRenderCb = [
            function () {
                frameView.fill();
            }];

        this.initialize = function () {

            $('#top-menu .icon').removeClass('active');
            $('#top-menu .icon.user').addClass('active');

            $('.lightblue-menu a').removeClass('active');
            $('.lightblue-menu a[href="#account"]').addClass('active');
            $('.lightblue-menu a[href="#account"]').tab('show');
        };

        this.price_count = function () {

            var days = parseInt($('#days').val());
            if ($('#license1').is(':checked')) {
                $('.price').html((days*0.1).toFixed(2)+' EUR');
            } else if ($('#license2').is(':checked')) {
                $('.price').html((days*1)+' EUR');

            } else if ($('#license3').is(':checked')) {
                $('.price').html((days*2)+' EUR');

            }

        };

        this.events = function () {

            var _this = this;

            $(".dial").knob({
                'min':0,
                'max':100,
                'readOnly': true,
                'displayInput': false,
                'thickness': 0.14,
                'fgColor': '#5A86DC',
                'bgColor': '#232836',
                'width': 150,
                'height': 150,
                'angleOffset': 90
            });

            $(".minus").mousedown(function() {
                $('#days').val(parseInt($('#days').val())-1);
                $(this).attr('src', '/static/img/icons/radio-minus-hover.png');
                _this.price_count();
            });
            $(".minus").mouseleave(function() {
                $(this).attr('src', '/static/img/icons/radio-minus.png');
            });
            $(".minus").mouseup(function() {
                $(this).attr('src', '/static/img/icons/radio-minus.png');
            });
            $(".plus").mousedown(function() {
                $('#days').val(parseInt($('#days').val())+1);
                $(this).attr('src', '/static/img/icons/radio-plus-hover.png');
                _this.price_count();
            });
            $(".plus").mouseleave(function() {
                $(this).attr('src', '/static/img/icons/radio-plus.png');
            });
            $(".plus").mouseup(function() {
                $(this).attr('src', '/static/img/icons/radio-plus.png');
            });

            $("#days").change(function () {
                _this.price_count();
            });

            $("input[name=license]").change(function () {
                _this.price_count();
            });
        };


    });
});