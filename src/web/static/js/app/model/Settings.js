define(function (require) {
    "use strict";

    return extend.Model('singleton', function () {

        this.fetch = function () {
            return this.ajax({
                type: 'GET',
                url: "/settings.json"
            });
        };

    });
});