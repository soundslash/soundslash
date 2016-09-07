define(function (require) {
    "use strict";

    return extend.Model(function () {

        this.initialize = function () {

        };

        this.find = function (string, page, sort) {
            return this.ajax({
                cache: 10,
                type: 'GET',
                url: "/search.json?search="+encodeURIComponent(string)+
                    "&p="+encodeURIComponent(page)+
                    (!(typeof sort === 'undefined')?"&sort="+encodeURIComponent(sort):'')
            });
        };

        this.findGenres = function () {
            return this.ajax({
                cache: 10,
                type: 'GET',
                url: "/genres.json"
            });
        };

        this.getStream = function () {
            return this.ajax({
                cache: 10,
                type: 'GET',
                url: "/radio.json"
            });
        };

        this.database = function (data) {
            return this.ajax({
                    type: 'GET',
                    url: "/stream/database.json",
                    data: data
                }
            );
        };

        this.about = function (stream_id) {

            return this.ajax({
                    type: 'GET',
                    url: "/stream/about.json",
                    data: {
                        stream_id: stream_id
                    }
                }
            );
        };

        this.program = function (data) {

            return this.ajax({
                    type: 'GET',
                    url: "/stream/program.json",
                    data: data
                }
            );
        };


        this.play = function (data) {
            return this.ajax({
                type: 'GET',
                url: "/play.json",
                data: data
            });
        };

        this.getGenresHtml = function () {
            return this.ajax({
                cache: 60*60*24*15,//15 days
                type: 'GET',
                url: "/stream-genres.html"
            });
        };

        this._events = function () {

        };
    });
});