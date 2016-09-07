
define(function (require) {
    "use strict";

    var user = require('model/User'),
        frameView = require('view/Frame');

    return extend.View('singleton', function () {

        this.template = 'user-profile';
        this.append = '#profile';

        this.afterRenderCb = [
            function () {
                frameView.fill();
            }];


        this.initialize = function () {

            $('#top-menu .icon').removeClass('active');
            $('#top-menu .icon.user').addClass('active');

            $('.lightblue-menu a').removeClass('active');
            $('.lightblue-menu a[href="#profile"]').addClass('active');
            $('.lightblue-menu a[href="#profile"]').tab('show');
        };

        this.events = function () {

            $(".chosen-select-one").chosen({
                no_results_text: "Oops, nothing found!",
                width: "100%"
            });
        };


    });
});