define(function (require) {
    "use strict";

    return extend.Model('singleton', function () {

        this._session = false;
        this._user = false;
        this._confirmed = null;

        this.sessionChanged = new Event(this);
        this.userChanged = new Event(this);
        this.confirmedChanged = new Event(this);

        this.initialize = function (settings) {
            this._session = settings.session;
            this._confirmed = settings.confirmed;
            this._user = settings.user;
        };

        this._events = function () {
            var _this = this;
            this.watch('_session', function (prop, oldval, val) {
                _this.sessionChanged.notify({
                    'oldval': oldval,
                    'val': val
                });
                return val;
            });
            this.watch('_confirmed', function (prop, oldval, val) {
                _this.confirmedChanged.notify({
                    'oldval': oldval,
                    'val': val
                });
                return val;
            });
            this.watch('_user', function (prop, oldval, val) {
                _this.userChanged.notify({
                    'oldval': oldval,
                    'val': val
                });
                return val;
            });
        };

        this.login = function (data) {
            return this.ajax({
                type: 'POST',
                url: "/login.json",
                data: data
            });
        };

        this.fblogin = function (response) {
            return this.ajax({
                type: 'POST',
                url: "/fb-login.json",
                data: {
                    accessToken: response.authResponse.accessToken,
                    expiresIn: response.authResponse.expiresIn,
                    signedRequest: response.authResponse.signedRequest,
                    userID: response.authResponse.userID,
                    status: response.status
                }
            });
        };

        this.signup = function (data) {
            return this.ajax({
                type: 'POST',
                url: "/sign-up.json",
                data: data
            });
        };

        this.logout = function () {
            return this.ajax({
                type: 'GET',
                url: "/logout.json"
            });
        };

        this.terms = function () {
            return this.ajax({
                type: 'GET',
                url: "/terms.html"
            });
        }

        this.profile = function () {
            return this.ajax({
                cache: 10,
                type: 'GET',
                url: "/profile.json"
            });
        };


        this._events();
    });
});