
define(function (require) {
    "use strict";

    var user = require('model/User'),
        frameView = require('view/Frame');

    return extend.View('singleton', function () {

        this.template = 'user';
        this.append = '.main';


        this.afterRenderCb = [
            function () {
                frameView.fill();
            }];

        var _this = this;

        this.initialize = function () {

            $('#top-menu .icon').removeClass('active');
            $('#top-menu .icon.user').addClass('active');

        };


    });
});