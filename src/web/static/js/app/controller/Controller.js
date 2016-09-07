define(function (require) {
    "use strict";

    var settings = require('model/Settings'),
        tmpl = require('tmpl'),

    /*
     Frame
     */
//        frameTpl = require('text!tpl/frame.html'),
        frameView = require('view/Frame'),
        notificationView = require('view/Notification'),
        fbView = require('view/Facebook'),
        player = require('view/PlayerView'),

    /*
     User
     */
        user = require('model/User'),

    /*
     Libs
     */
        _ = require('lib/loading'),

        _ = require('bootstrap'), _ = require('css!styles/lib/bootstrap.min.css'),
        _ = require('bootstrap-notify'), _ = require('css!styles/lib/bootstrap-notify.css'),
        _ = require('bootstrap-slider'), _ = require('css!styles/lib/slider.css'),

        _ = require('snap'), _ = require('css!styles/lib/snap.css'),
        _ = require('jquery-scrolltofixed'),

        _ = require('css!styles/lib/chosen.min.css'),

        _ = require('css!styles/lib/bootstrap.min.css'),
        _ = require('css!styles/styles.css'),
        _ = require('css!styles/loading.css');


    return window.Controller = extend({target: Controller}, (function () {

        this.actionFrame = function () {

//            window.View = extend({'target': window.View}, function () {
//                this.loadingTarget = '.main';
//                this.afterRenderCb = [
//                    function () {
//                        console.log('F');
//                        frameView.fill();
//                    }];
//            });

            /*
             Render frame synchronously.
             */


            frameView.render({});

            var _this = this;

            notificationView.render().afterRender(function () {
                /*
                 Configure user
                 */
                settings.fetch().done(
                    function (data) {
                        user.initialize(data);
                        _this.actionFrame.done();
                    }
                );
            });

            player.render();
            fbView.connect();

        };

    }));
});
