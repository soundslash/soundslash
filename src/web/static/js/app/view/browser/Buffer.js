define(function (require) {
    "use strict";

    var user = require('model/User'),
        frameView = require('view/Frame'),
        Buffer = require('view/Buffer'),
        dialog = require('view/Dialog'),
        Stream = require('model/Stream');

    return extend.View(function () {



        this.nextTracks = function(a) {

            $(a).closest('.icons-row').find('a.active').removeClass('active');
            $(a).addClass('active');

        };
        this.lastPlayed = function(a) {

            $(a).closest('.icons-row').find('a.active').removeClass('active');
            $(a).addClass('active');
        };





    });
});
