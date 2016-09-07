define(function (require) {
    "use strict";

    var ListenView = require('view/Listen'),
        Stream = require('model/Stream'),
        ListenPopularView = require('view/ListenPopular'),
        ListenGenreView = require('view/ListenGenre'),
        ListenGenreListView = require('view/ListenGenreList'),
        ListenNewView = require('view/ListenNew'),
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
                    action: 'listenFrame',
                    isRendered: function () {
                        return $("input#search-listen").length === 1;
                    }
                }
            ]
        };

        this.actionListenFrame = function () {
            frameView.mode2();
            var lv = new ListenView();
            lv.afterRender(this.actionListenFrame.done);
            lv.render();
        };

        this.actionPopular = function (args) {
            var search_string = args.search_string,
                page = args.page;

            if (typeof search_string === 'undefined')
                search_string = '';

            if (typeof page === 'undefined')
                page = 1;

            var stream = new Stream();
            stream.find(search_string, page)
                .done(function (data) {
                    var lpv = new ListenPopularView();

                    if (parseInt(page) === 1) {
                        lpv.render(data);
                    } else if (parseInt(page) > 1) {
                        lpv.loadMore(data);
                    }
                });
        };

        this.actionIndex =
            this.actionPopular;

        this.actionGenres = function (args) {

            var stream = new Stream();
            stream.findGenres()
                .done(function (data) {
                    var lpv = new ListenGenreView();
                    lpv.render(data);
                });
        };

        this.actionGenreList = function (args) {

            var genre = args.genre,
                page = args.page;

            if (typeof genre === 'undefined')
                genre = '';

            if (typeof page === 'undefined')
                page = 1;

            var stream = new Stream();
            stream.find(genre, page)
                .done(function (data) {
                    var lpv = new ListenGenreListView();
                    lpv.render(data);
                });
        };
        this.actionNew = function (args) {

            var search_string = args.search_string,
                page = args.page;

            if (typeof search_string === 'undefined')
                search_string = '';

            if (typeof page === 'undefined')
                page = 1;

            var stream = new Stream();
            stream.find(search_string, page, '_id')
                .done(function (data) {
                    var lpv = new ListenNewView();
                    lpv.render(data);
                });
        };


    });

});
