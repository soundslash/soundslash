define(function (require) {
    "use strict";

    var user = require('model/User'),
        dialog = require('view/Dialog');

    return extend.View('singleton', function () {

        this.initialize = function () {
            user.terms().done(function (data) {
                dialog.show('Terms and conditions', data);
            });
        };


    });
});