define(function (require) {
    "use strict";

    var user = require('model/User'),
        frameView = require('view/Frame'),
        dialog = require('view/Dialog'),
        Stream    = require('model/Stream'),
        _ = require('lib/bootstrap-timepicker.min'),
        _ = require('lib/ajaxinput'),
        _ = require('lib/colorinput'),
        _ = require('lib/bootstrap-filestyle.min');

    return window.program = extend.View('singleton', function () {

        this.template = 'stream-program';
        this.append = '#radio-content';


        this.program = function (e, day) {

            var stream = new Stream(), _this = this;
            stream.program({
                stream_id: $('#stream').data('id'),
                day: day
            }).done(function (data) {


                $('.lightblue-menu h1.menu-title').html('Program');

                $(e).tab('show');
                $(e).closest('.icons-row').find('a.active').removeClass('active');
                $(e).addClass('active');

                data = _this.countProgram(data);

                var v = new View();
                v.template = 'stream-program-list';
                v.append = '#radio-content #' + day + '';
                v.afterRender(function () {

                    var v = new View();
                    v.template = 'stream-program-timeline';
                    v.append = '#radio-content #' + day + " .timeline";
                    v.afterRender(function () {

                        $('#radio-content #' + day + ' .program .hour > div').mouseenter(function () {
                            var id = $(this).data('program-id');
                            if (id != "undefined") {
                                $('#radio-content #' + day + ' .program .program-' + id).css('z-index', 100);
                                $('#radio-content #' + day + ' .program .program-' + id).css('box-shadow', '0px 0px 5px rgba(255,255,255,0.6)');
                                //                            $('.program .program-' + id).css('opacity', 1);
                                var bg = $("<div class='bg'></div>");
                                bg.hide();
                                bg.appendTo($('#radio-content #' + day + ' .program .hour'));
                                $('#radio-content #' + day + ' .program .hour .bg').fadeIn(250);

                                $('#radio-content #' + day + ' .program .program-' + id).animate({
                                    opacity: 1
                                }, 250, function () {

                                });
                            }
                        });

                        $('#radio-content #' + day + ' .program .hour > div').mouseleave(function () {
                            var id = $(this).data('program-id');
                            if (id != "undefined") {
                                $('#radio-content #' + day + ' .program .program-' + id).each(function () {
                                    $(this).css('z-index', $(this).data('z-index'));
                                    $(this).css('box-shadow', '');
                                    $(this).css('opacity', $(this).data('opacity'));
                                });
                                $('#radio-content #' + day + ' .program .hour .bg').remove();
                            }
                        });
                        frameView.fill();
                    });
                    v.render(data);

                });
                v.render(data);

            });


        };

        this.initialize = function () {

        };


        this.programTimeline = function(e) {
            var day = $(e).closest('.tab-pane').attr('id');
            if ($(e).data('href') == '#timeline') {
                $(e).find('span').html('View as list');
                $(e).data('href', '#list');
                $("#"+day+" .list").hide();
                $("#"+day+" .timeline").show();
            } else {
                $(e).find('span').html('View as timeline');
                $(e).data('href', '#timeline');
                $("#"+day+" .timeline").hide();
                $("#"+day+" .list").show();
            }
            frameView.fill();
            return false;
        };

        this.reloadProgram = function(day) {
            $('#'+day+' *').remove();
            this.program(undefined, day);
        };

        this.createProgram = function(day) {

            $.ajax({
                    type: 'GET',
                    url: "/stream/database.json",
                    data: {
                        stream_id: $('#stream').data('id')
                    },
                    success: function (data) {
                        data['day'] = day;
                        dialog.show('Create program', '<div class="create-program-holder"></div>');

                        var v = new View();
                        v.template = 'stream-program-settings';
                        v.append = '.create-program-holder';
                        v.afterRender(function () {

                            var options = {
                                showMeridian: false
                            };

                            $('#timepicker1').timepicker(options);
                            $('#timepicker2').timepicker(options);

                            var picture = undefined;

                            $("#picture-wrap").ajaxinput("picture",'/stream/picture.json', function () {

                                if (picture === undefined) {
                                    $("#picture-show").html('No picture');
                                } else {
                                    var img = $("<img>");
                                    img.attr("src", "/image.jpg?id="+picture+"&thumb=160x160");
                                    $("#picture-show").html(img);
                                }

                            }, function () {
                                $('.dialog .content').loading();
                            }, function (data) {
                                if (!data.error) {
                                    var img = $("<img>");
                                    img.attr("src", data.data);
                                    $("#picture-show").html(img);
//                            $('#radio-content input[name="picture"]').remove();
//                            var input = $("<input>");
//                            input.attr("type", "hidden");
//                            input.attr("name", "picture");
//                            input.attr("value", data.image_id);
//                            $('#stream-form').append(input);
                                    $('.dialog .content').loading_stop();
                                    frameView.fill();
                                }
                            }, false, true);

                            $(".color-input").colorinput('color', '#588c75', [
                                '#588c75', '#b0c47f', '#f3ae73', '#da645a', '#ab5351', '#8d4548'
                            ], function () {

                            }, function () {

                            }, function () {

                            });

                            // array of repeats
                            window.selected_repeats = [];

                            browser.databasePlaylists($('.db-menu').find('a[href="#playlists"]'));
                            browser.initBrowser(false);

                        });
                        v.render(data);


                    }
                }
            );


        };
        this.editProgram = function(a) {

            var program_id = $(a).attr('data-program-id');

            $.ajax({
                    type: 'GET',
                    url: "/stream/program.json",
                    data: {
                        program_id: program_id,
                        stream_id: $('#stream').data('id')
                    },
                    success: function (data) {

                        data['program_id'] = program_id;
                        dialog.show('Edit program', '<div class="edit-program-holder"></div>');

                        var v = new View();
                        v.template = 'stream-program-settings';
                        v.append = '.edit-program-holder';
                        v.afterRender(function () {


                            $('input[name=name]').val(data['program']['name']);

                            if (data['program']['selection'] == 'shuffle')
                                $('input[name=shuffle]').attr('checked', 'checked');


                            if (data['program']['force_start'] == true)
                                $('input[name=exact]').attr('checked', 'checked');

                            var options = {
                                showMeridian: false
                            };
                            $('#timepicker1').val(data['program']['start'].split(' ')[1]);
                            $('#timepicker2').val(data['program']['end'].split(' ')[1]);
                            $('#timepicker1').timepicker(options);
                            $('#timepicker2').timepicker(options);

                            var picture = data['program']['picture'];

                            $("#picture-wrap").ajaxinput("picture-wide", '/stream/picture.json', function () {

                                if (picture === undefined) {
                                    $("#picture-show").html('No picture');
                                } else {
                                    var img = $("<img>");
                                    img.attr("src", "/image.jpg?id="+picture+"&thumb=160x90");
                                    $("#picture-show").html(img);
                                }

                            }, function () {
                                $('.dialog .content').loading();
                            }, function (data) {
                                if (!data.error) {
                                    var img = $("<img>");
                                    img.attr("src", data.data);
                                    $("#picture-show").html(img);

                                    $('.dialog input[name="pic"]').remove();
                                    var input = $("<input>");
                                    input.attr("type", "hidden");
                                    input.attr("name", "pic");
                                    input.attr("value", data.image_id);
                                    $('.dialog .content').append(input);

                                    $('.dialog .content').loading_stop();
                                    UI.fill();
                                }
                            }, false, true);

                            $(".color-input").colorinput('color', data['program']['color'], [
                                '#588c75', '#b0c47f', '#f3ae73', '#da645a', '#ab5351', '#8d4548'
                            ], function () {

                            }, function () {

                            }, function () {

                            });

                            // array of repeats
                            window.selected_repeats = data['repeating'];
                            browser.databaseRepeats(undefined, window.selected_repeats);



                            data['playlist'] = data['group'];
                            var parent = 'playlists';



                            var v = new View();
                            v.wrap_el = false;
                            v.template = 'stream-program-selected';
                            v.append = '#'+parent+' .'+parent+'-body';
                            v.afterRender(function () {


                                $('#'+parent+' form').hide();

                                $('.db-menu a.active').removeClass('active');
                                $('.db-menu a[href="#playlists"]').addClass('active');

                                frameView.fill();
                                browser.initBrowser(false);
                            });
                            v.render(data);


                        });
                        v.render(data);


                    }}
            );

        };
        this.removeProgram = function(program_id) {

            var _this = this;
            var day = $('.day-menu .active').attr('href').substring(1);
            var data = {
                name: $('input[name=name]').val(),
                start: $('#timepicker1').val(),
                end: $('#timepicker2').val(),
                exact: $('input[name=exact]').is(':checked'),
                shuffle: $('input[name=shuffle]').is(':checked'),
                picture: $('input[name=pic]').val(),
                color: $('input[name=color]').val(),
                playlist: $('#playlists-table tr.playlist-selected').attr('id'),
                repeats: window.selected_repeats,
                day: day
            };

            var all_d = {
                stream_id: $('#stream').data('id'),
                data: JSON.stringify(data),
                remove: true,
                program_id: program_id
            };


            $('.dialog .content').loading_center();
            $.ajax({
                type: 'POST',
                url: "/stream/program.json",
                data: all_d,
                success: function (data) {
                    if (data.error) {

                        $('.top-right').notify({
                            type: 'danger',
                            message: { text: data.error },
                            fadeOut: { enabled: true, delay: 5000 }
                        }).show();
                    } else {
                        _this.reloadProgram(day);
                        $('.dialog .close').click();
                    }
                    $('.dialog .content').loading_stop();

                }});
        };
        this.submitProgram = function(date) {
            var _this = this;
            var day = $('.day-menu .active').attr('href').substring(1);
            var data = {
                name: $('input[name=name]').val(),
                start: $('#timepicker1').val(),
                end: $('#timepicker2').val(),
                exact: $('input[name=exact]').is(':checked'),
                shuffle: $('input[name=shuffle]').is(':checked'),
                picture: $('input[name=pic]').val(),
                color: $('input[name=color]').val(),
                playlist: $('#playlists-table tr.playlist-selected').attr('id'),
                repeats: window.selected_repeats,
                day: day
            };

            var all_d = {
                stream_id: $('#stream').data('id'),
                data: JSON.stringify(data)
            };

            if ($('.dialog input[name=program_id]').length >= 1) {
                all_d['program_id'] = $('input[name=program_id]').val();
            }

            $('.dialog .content').loading_center();
            $.ajax({
                type: 'POST',
                url: "/stream/program.json",
                data: all_d,
                success: function (data) {
                    if (data.error) {

                        $('.top-right').notify({
                            type: 'danger',
                            message: { text: data.error },
                            fadeOut: { enabled: true, delay: 5000 }
                        }).show();
                    } else {
                        _this.reloadProgram(day);
                        $('.dialog .close').click();
                    }
                    $('.dialog .content').loading_stop();

                }});
        };


        this.countProgram = function (data) {

            // 0 - 24
            data["hours"] = new Array(24);
            data["layers_per_hour"] = new Array(24);

            for (var i = 0; i < data['hours'].length; i++) {
                data['hours'][i] = [];
                data["layers_per_hour"][i] = 0;
            }
            function percent(max, val) {
                return (100 * val) / max;
            }


            $.each(data.program, function (i, program) {
                program.start = program.start.split(' ').join('T');
                program.end = program.end.split(' ').join('T');
                var start = new Date(program.start);
                var end = new Date(program.end);
                var this_day = new Date(data.day + "T00:00:00");
                var this_day_end = new Date(data.day + "T23:59:59");
                var now = new Date();

                var cur_hour = 0;
                var start_minute = 0;
                if (start < this_day) {
                    cur_hour = 0;
                    start_minute = 0;
                } else {
                    cur_hour = start.getHours();
                    start_minute = start.getMinutes();
                }

                if (end < this_day_end) {
                    var once = true;

                    while (cur_hour <= end.getHours()) {

                        var layer = 0;

                        if (once) {
                            var s = start_minute;
                            once = false;
                        } else {
                            var s = 0;
                        }

                        if (end.getHours() == cur_hour) {
                            var duration = end.getMinutes() - s;
                            if (duration != 0) {
                                var cur_from = s;
                                var cur_to = s + duration;
                                var max_layer = 0;
                                var collide = false;
                                $.each(data['hours'][cur_hour], function (j, p) {
                                    // check if collide, if so increment layer
                                    var from = p.start;
                                    var to = p.start + p.duration;
                                    if (max_layer < p.layer) {
                                        max_layer = p.layer;
                                    }
                                    //                                            console.log("from: "+from+" cur_from:"+cur_from+" to:"+to+" cur_to:"+cur_to);
                                    if ((from <= cur_from && cur_from < to) ||
                                        (from < cur_to && cur_to <= to)) {
                                        collide = true;
                                    }
                                });
                                if (collide) {
                                    layer = max_layer + 1;
                                    data["layers_per_hour"][cur_hour] = layer;
                                }
                                //                                        console.log(cur_hour+" "+collide+" "+layer);
                                data['hours'][cur_hour].push({
                                    program: program,
                                    duration: duration,
                                    start: s,
                                    duration_percent: percent(60, duration),
                                    start_percent: percent(60, s),
                                    layer: layer
                                });
                            }
                        } else {
                            var duration = 60 - s;
                            if (duration != 0) {
                                var cur_from = s;
                                var cur_to = s + duration;
                                var max_layer = 0;
                                var collide = false;
                                $.each(data['hours'][cur_hour], function (j, p) {
                                    // check if collide, if so increment layer
                                    var from = p.start;
                                    var to = p.start + p.duration;
                                    if (max_layer < p.layer) {
                                        max_layer = p.layer;
                                    }
                                    //                                            console.log("from: "+from+" cur_from:"+cur_from+" to:"+to+" cur_to:"+cur_to);
                                    if ((from <= cur_from && cur_from < to) ||
                                        (from < cur_to && cur_to <= to)) {
                                        collide = true;
                                    }
                                });
                                if (collide) {
                                    layer = max_layer + 1;
                                    data["layers_per_hour"][cur_hour] = layer;
                                }
                                //                                        console.log(cur_hour+" "+collide+" "+layer);
                                data['hours'][cur_hour].push({
                                    program: program,
                                    duration: duration,
                                    start: s,
                                    duration_percent: percent(60, duration),
                                    start_percent: percent(60, s),
                                    layer: layer
                                });
                            }
                        }
                        cur_hour += 1;
                    }
                } else {
                    var once = true;

                    while (cur_hour <= 24) {

                        var layer = 0;

                        if (once) {
                            var s = start_minute;
                            once = false;
                        } else {
                            var s = 0;
                        }

                        var duration = 60 - s;

                        if (duration != 0) {

                            var cur_from = s;
                            var cur_to = s + 60 - s;
                            var max_layer = 0;
                            var collide = false;
                            $.each(data['hours'][cur_hour], function (j, p) {
                                // check if collide, if so increment layer
                                var from = p.start;
                                var to = p.start + p.duration;
                                if (max_layer < p.layer) {
                                    max_layer = p.layer;
                                }
                                if ((from <= cur_from && cur_from < to) ||
                                    (from < cur_to && cur_to <= to)) {
                                    collide = true;
                                }
                            });
                            if (collide) {
                                layer = max_layer + 1;
                                data["layers_per_hour"][cur_hour] = layer;
                            }
                            data['hours'][cur_hour].push({
                                program: program,
                                duration: 60 - s,
                                start: s,
                                duration_percent: percent(60, 60 - s),
                                start_percent: percent(60, s),
                                layer: layer
                            });
                        }
                        cur_hour += 1;
                    }
                }
            });

            // fill gaps

            for (var i = 0; i < data['hours'].length; i++) {
                var position = 0;

                while (position < 60) {

                    var next_start = 60, next_program = null;
                    for (var k = 0; k < data['hours'][i].length; k++) {
                        var np = data['hours'][i][k];
                        if (position <= np.start && np.start <= next_start) {
                            next_start = np.start;
                            next_program = np;
                        }
                    }

                    if (next_start === 0) {
                        position = next_program.start + next_program.duration;
                    } else if (next_start === 60 && next_program === null) {

                        data['hours'][i].push({
                            program: {
                                "name": "Default",
                                "color": "#1C212A",
                                "start": data.day + "T" + (i <= 9 ? '0' : '') + i + ":00:00",
                                "end": data.day + "T" + (i <= 9 ? '0' : '') + i + ":59:00"
                            },
                            duration: 60-position,
                            start: position,
                            duration_percent: percent(60, 60-position),
                            start_percent: percent(60, position),
                            layer: 0
                        });
                    } else if (next_start !== 0 && next_program !== null) {

                        if (position < next_start)
                            data['hours'][i].push({
                                program: {
                                    "name": "Default",
                                    "color": "#1C212A",
                                    "start": data.day + "T" + (i <= 9 ? '0' : '') + i + ":" + (position <= 9 ? '0' : '') + (position) + ":00",
                                    "end": data.day + "T" + (i <= 9 ? '0' : '') + i + ":" + (next_start <= 9 ? '0' : '') + (next_start == 60 ? 59 : next_start) + ":00"
                                },
                                duration: next_start - position,
                                start: position,
                                duration_percent: percent(60, next_start - position),
                                start_percent: percent(60, position),
                                layer: 0
                            });
                        position = next_program.start + next_program.duration;
                    }


                }


            }

            return data;

        }

    });

});
