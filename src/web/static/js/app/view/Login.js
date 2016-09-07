
define(function (require) {
    "use strict";

    var user = require('model/User'),
        frameView = require('view/Frame');

    return extend.View('singleton', function () {

        this.template = 'login';
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

        this.events = function () {

            $('#login').submit(function(e) {
                e.preventDefault();
                var _this = this;
                $(_this).loading();

                user.login($(this).serialize()).done(function (data) {

                    if (data.error) {
                        $('.top-right').notify({
                            type: 'danger',
                            message: { text: data.msg },
                            fadeOut: { enabled: true, delay: 5000 }
                        }).show();
                    } else {
                        user._user = data.user;

                        $('.top-right').notify({
                            type: 'success',
                            message: { text: "Successfully signed up" },
                            fadeOut: { enabled: true, delay: 5000 }
                        }).show();

                        url('/stream.html', {action: 'live'});


                    }
                    $(_this).loading_stop();
                });

                return false;
            });
        };



    });
});