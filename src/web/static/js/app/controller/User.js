define(function (require) {
    "use strict";

    var loginView = require('view/Login'),
        accountFrameView = require('view/AccountFrame'),
        accountView = require('view/Account'),
        profileView = require('view/Profile'),
        user = require('model/User'),
        chosen = require('lib/chosen.jquery.min'),
        frameView = require('view/Frame'),
        notify = require('view/Notification')
        ;

    return extend.Controller(function () {

        this._this = this;

        this.actionRequire = {
            '*': [
                {
                    action: 'frame',
                    isRendered: function () { return $("#body-wrap").length === 1;}
                },
                {
                    action: 'userFrame',
                    isRendered: function () {
                        return $(".main > div[data-view=user]").length === 1;
                    }
                }
            ]
        };

        this.actionUserFrame = function () {
            frameView.mode2();
            if (user._user) {
                accountFrameView.afterRenderCb = [this.actionUserFrame.done];
                accountFrameView.render();
            } else {
                this.actionUserFrame.done();
            }
        };

        this.actionIndex = function (args) {
            var _this = this;
            if (user._user) {
                url('/user.html', {action: "account"});
            } else {
                if (args.session === "expired") {
                    notify.on_expire();
                    user._session = args.session;
                }
                loginView.render();
            }
        };

        this.actionAccount = function (args) {
            user.profile().done(function (data) {
                accountView.render(data);
            });
        };

        this.actionProfile = function (args) {
            user.profile().done(function (data) {
                profileView.render(data);
            });
        };

        this.actionLogout = function (args) {
            user.logout().done(function () {
                user._user = false;
                url('/listen.html');
            });
        };
    });

});
