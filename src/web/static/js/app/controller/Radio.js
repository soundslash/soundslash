define(function (require) {
    "use strict";

    var radioView = require('view/Radio'),
        radioUserView = require('view/RadioUser'),
        termsView = require('view/Terms'),
        Stream    = require('model/Stream'),
        user      = require('model/User'),
        frameView = require('view/Frame');

    return extend.Controller(function () {

        this._this = this;

        this.actionRequire = {
            '*': [
                {
                    action: 'frame',
                    isRendered: function () { return $("#body-wrap").length === 1;}
                },
                {
                    action: 'radioFrame',
                    isRendered: function () {
                        return $(".main > div[data-view=radio]").length === 1;
                    }
                }
            ]
        };

        this.actionRadioFrame = function () {
            var _this = this;
            frameView.mode2();
            if (user._user) {
                var stream = new Stream();
                stream.getStream().done(function (data) {
                    if (data.user) {
                        radioUserView.afterRenderCb = [_this.actionRadioFrame.done];
                        radioUserView.render(data);
                    } else {
                        url('/user.html', {action: 'logout'});
                    }
                });
            } else {
                this.actionRadioFrame.done();
            }
        };

        this.actionIndex = function (args) {
            var _this = this;
            if (user._user) {
                //redirect
                url('/stream.html', {action: 'live'});
            } else {
                frameView.mode1();
                radioView.render({user: user._user});
            }
        };

        this.actionTerms = function (args) {
            termsView.initialize();
        };

    });

});
