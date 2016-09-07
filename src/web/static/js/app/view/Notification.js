define(function (require) {
    "use strict";

    var user = require('model/User');

    return extend.View('singleton', function () {
        'use strict';

        this.template = 'notify';
        this.append = '#top-menu .container-fluid .row';
        this.replace = false;

        this.notify = function (settings) {
            $('.top-right').notify(settings).show();
        };

        this.on_expire = function () {
            this.notify({
                type: 'danger',
                message: { text: 'Session has expired, please sign in again :-)' },
                fadeOut: { enabled: true, delay: 5000 }
            });
        };

        this.events = function () {
            var _this = this;
            user.sessionChanged.attach(function (sender, session) {
                if (session['val'] === "expired") {
                    _this.on_expire();
                }
            });

            user.confirmedChanged.attach(function (sender, confirmed) {
                if (confirmed['val'] === true) {
                    _this.notify({
                        type: 'success',
                        message: { text: 'Email address successfully confirmed' },
                        fadeOut: { enabled: true, delay: 5000 }
                    });
                }
            });

        };
    });

});