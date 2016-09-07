define(function (require) {
    "use strict";

    var radioView = require('view/Radio'),
        radioUserView = require('view/RadioUser'),
        Stream    = require('model/Stream'),
        live = require('model/Live'),
        updates = require('model/Updates'),
        liveView = require('view/Live'),
        user      = require('model/User'),
        frameView = require('view/Frame'),
        browser = require('view/Browser'),
        DatabaseView = require('view/Database'),
        program = require('view/Program'),
        report = require('view/Report'),
        About = require('view/About');

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
                        return $(".main > div[data-view=radio-user]").length === 1;
                    }
                }
            ]
        };

        this.actionRadioFrame = function () {
            frameView.mode2();
            var stream = new Stream(), _this = this;
            stream.getStream().done(function (data) {
                radioUserView.afterRenderCb = [_this.actionRadioFrame.done];
                radioUserView.render(data);
            });
        };

        this.actionLive = function (args) {
            var stream = new Stream();
            stream.getStream().done(function (data) {
                var stream_id = data.stream._id;
                live.live({stream_id: stream_id}).done(function (data) {
                    liveView.afterRenderCb = [function () {
                        stream.play({streamId: stream_id}).done(function () {
                            updates.initialize(stream_id);

                            if (args.autoplay) {
                                $('.player .pic a')[0].onclick();
                            }
                        });
                    }];
                    liveView.render(data);

                });

            });

        };
        this.actionIndex
            = this.actionLive;


        this.actionMedia = function (args) {

            var stream = new Stream();
            stream.getStream().done(function (data) {
                var stream_id = data.stream._id;

                stream.database({stream_id: stream_id}).done(function (data) {

                    data['parent'] = "database";
                    var dv = new DatabaseView();
                    dv.render(data).afterRender(function () {
                        $('.lightblue-menu h1.menu-title').html('Media');

                        browser.initEditBrowser();
                        radioView.fileupload();
                        browser.initBrowser();
                        frameView.fill();

                    });
                });
            });
        };


        this.actionProgram = function (args) {


            var d = new Date();
            var weekday = new Array(7);
            weekday[0]=  "Sunday";
            weekday[1] = "Monday";
            weekday[2] = "Tuesday";
            weekday[3] = "Wednesday";
            weekday[4] = "Thursday";
            weekday[5] = "Friday";
            weekday[6] = "Saturday";

            var day = weekday[d.getDay()];

            program.afterRenderCb = [function () {
                program.program($('.icons-row a[href=#'+weekday[d.getDay()]+"]"), day);
            }];
            program.render();



        };
        this.actionReport = function (args) {


            report.afterRenderCb = [function () {

            }];
            report.render();

        };


        this.actionAbout = function (args) {

            var stream = new Stream();
            stream.getStream().done(function (data) {

                var stream_id = data.stream._id;
                stream.about(stream_id).done(function (data) {
                    var about = new About();
                    about.afterRender(function () {
                        about.postinitialize(data);
                    });
                    about.render(data);
                });
            });

        };
    });


});