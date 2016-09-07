define(function (require) {
    "use strict";

    return extend.Model('singleton', function () {

        this.live = function (data) {
            return this.ajax({
                type: 'GET',
                url: "/stream/live.json",
                data: data
            });
        };
    });
});