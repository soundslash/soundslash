define(function (require) {
    "use strict";

    window.Raphael = require('lib/raphael-min');
    var browser = require('view/Browser'),
        frameView = require('view/Frame'),

        _ = require('lib/jquery.async'),
        _ = require('lib/date.format.1.2.3.min'),
        _ = require('lib/g.raphael-min'),
        _ = require('lib/g.line-min'),
        _ = require('lib/g.pie-min'),
        _ = require('lib/chart');

    return window.report = extend.View('singleton', function () {

        this.template = 'stream-report';
        this.append = '#radio-content';

        this.initialize = function () {

            $(".datepicker").datepicker({ dateFormat: 'dd.mm.yy' });

            $('.lightblue-menu h1.menu-title').html('Report');

            $('#export-format').chosen({
                disable_search_threshold: 99999,
                width: "100%"
            });
            this.export()
        };

        this.export = function(a) {

            $(a).tab('show');
            $('.reports-menu a.active').removeClass('active');
            $(a).addClass('active');
            frameView.fill();
        };

        this.tags = function(a, reload) {

            if (reload === undefined) var reload = false;

            $(a).tab('show');
            $('.reports-menu a.active').removeClass('active');
            $(a).addClass('active');

            if (!reload && $('#tags').find('tr').length != 0) {
                frameView.fill();
                return;
            }


            $('.main').loading_center();
            $.ajax({
                type: 'GET',
                url: "/stream/tags.json",
                data: {
                    stream_id: $('#stream').data('id')
                },
                success: function (data) {

                    var v = new View();
                    v.template = 'stream-report-tags';
                    v.append = '#tags';
                    v.afterRender(function () {
                        frameView.fill();
                    });
                    v.render(data);

                    $('.main').loading_stop();
                },
                error: function (data) {
                    $('.main').loading_stop();
                }
            });
        };

        this.saveTags = function (a) {

            var s = $('#tag-edit').serializeObject();
            s['action'] = 'tags';
            $('.dialog').loading_center();
            $.ajax({
                type: 'POST',
                url: "/stream/tags.json",
                data: s,
                success: function (data) {

                    $(a).closest('.dialog').find('.close').click();

                    frameView.fill();
                    $('.dialog').loading_stop();
                },
                error: function (data) {
                    $('.dialog').loading_stop();
                }
            });
        };


        this.stats = function(a) {

            var _this = this;
            $(a).tab('show');
            $('.reports-menu a.active').removeClass('active');
            $(a).addClass('active');

            if ($('#stats').find('div').length != 0) {
                frameView.fill();
                return;
            }

            $('.main').loading_center();
            $.ajax({
                type: 'GET',
                url: "/stream/statistics.json",
                data: {
                    stream_id: $('#stream').data('id')
                },
                success: function (data) {


                    var v = new View();
                    v.template = 'stream-report-stats';
                    v.append = '#stats';
                    v.afterRender(function () {

                        $("#datepicker").change(function () {
                            _this.on_graph_update();
                        });
                        $(".chosen-select").change(function () {
                            _this.on_graph_update();
                        });



                        $(".datepicker").datepicker({ dateFormat: 'dd.mm.yy' });



                        $(".chosen-select").chosen({disable_search_threshold: 10});



                        _this.on_graph_update();

                        frameView.fill();
                    });
                    v.render(data);

                    $('.main').loading_stop();
                },
                error: function (data) {
                    $('.main').loading_stop();
                }
            });
        };

        this.on_graph_update = function () {

            $("#listeners-form").loading();
            $.ajax({
                type: 'POST',
                url: "/statistics/listeners.json",
                data: $('#listeners-form').serialize(),
                success: function (data) {
                    if (data.error) {

                    }
                    else {
                        $("#holder").html("");
                        var l = new Chart(-1, 150,
                            {
                                "x": data.x,
                                "y": data.y,
                                "legend": data.legend,
                                "time": 1
                            }
                            , "holder", $('select[name="range"] option:selected').val());

                        l.drawLinechart();


                    }
                    $("#listeners-form").loading_stop();

                }
            });
        };


        this.create_tag = function () {
            browser.create_playlist();
        };

        this.do_create_tag = function () {
            $("#edit-playlists").loading();
            var data = {}, _that = this;
            data['stream_id'] = $('#stream').data('id');
            data['action'] = 'create';
            data['name'] = $('.create-playlist input[name=playlist_name]').val();


            $.ajax({
                type: 'POST',
                url: "/stream/tags.json",
                data: data,
                success: function (data) {
                    browser.create_playlist();
                    $("#edit-playlists").loading_stop();
                    _that.tags($('.reports-menu a.active'), true);
                }
            });
        };

        this.do_remove_tag = function (e) {
            $("#edit-playlists").loading();

            var data = {}, _this = this;
            data['stream_id'] = $('#stream').data('id');
            data['name'] = $(e).data('name');
            data['action'] = 'delete';

            $.ajax({
                type: 'POST',
                url: "/stream/tags.json",
                data: data,
                success: function (data) {
                    $("#edit-playlists").loading_stop();
                    _this.tags($('.reports-menu a.active'), true);
                }
            });
        };

        this.remove_tag = function (e) {
            browser.swipe('left', $(e).closest('tr'));
        };

        this.do_edit_tag = function (e) {
            $("#edit-playlists").loading();

            var data = {}, _this = this;

            data['stream_id'] = $('#stream').data('id');
            data['name'] = $(e).data('name');
            data['action'] = 'rename';

            data['new_name'] = $(e).closest('tr').find('input').val();


            $.ajax({
                type: 'POST',
                url: "/stream/tags.json",
                data: data,
                success: function (data) {
                    $("#edit-playlists").loading_stop();
                    _this.tags($('.reports-menu a.active'), true);
                }
            });
        };

        this.edit_tag = function (e) {

            browser.swipe('right', $(e).closest('tr'));

        };



    });

});
