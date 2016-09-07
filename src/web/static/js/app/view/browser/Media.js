define(function (require) {
    "use strict";

    var user = require('model/User'),
        frameView = require('view/Frame'),
        Buffer = require('view/Buffer'),
        dialog = require('view/Dialog'),
        Stream = require('model/Stream'),
        DeleteTracks = require('view/DeleteTracks');

    return extend.View(function () {


        this.update_group = function (page, prev) {
            var _this = this;
            if ($("#group").is_loading())
                return;
            $("#group").loading();

            if (page !== undefined) {
                if (prev)
                    page = parseInt(page) - 1;
                else
                    page = parseInt(page) + 1;

                $('#groupsearch-form').find('input[name=page]').val(page);
            } else
                page = $('#groupsearch-form').find('input[name=page]').val();

            $.ajax({
                type: 'POST',
                url: "/stream/database/search.json",
                data: $('#groupsearch-form').serialize() + "&stream_id="+_this.stream_id,
                success: function (data) {
                    if (data.error) {
                        $(".error").html('<div class="alert alert-danger">' + data.msg + '</div>');
                        $(".error").show();
                    }
                    else {


                        for (var i in window.selected_repeats) {
                            for (var j in data.results) {
                                if (window.selected_repeats[i]['id'] == data.results[j]['_id']) {
                                    data.results[j]['repeating'] = window.selected_repeats[i]['repeating'];
                                    break;
                                }
                            }
                        }

                        data['parent'] = "database";

                        var buffer = new Buffer();
                        buffer.afterRender(function () {

                            $('.group-body .repeats select.repeating').chosen({
                                disable_search_threshold: 99999,
                                width: "100%"
                            });
                            $('.group-body .repeats select.repeating').change(function() {

                                if (!window.selected_repeats) {
                                    window.selected_repeats = [];
                                }
                                window.selected_repeats.push({
                                    id: $(this).closest('tr').attr('id'),
                                    artist: $(this).closest('tr').find('input[name="artist"]').val(),
                                    title: $(this).closest('tr').find('input[name="title"]').val(),
                                    duration: $(this).closest('tr').find('.repeats .format-duration').attr('data-duration'),
                                    repeating: $(this).closest('tr').find('select.repeating').val()
                                });
                                _this.updateRepeats(window.selected_repeats);
                            });

                            $('.format-duration').each(function (index) {
                                $(this).html(format_seconds($(this).data('duration') / 1000000000));
                            });
                            _this.do_draggable();
                        });
                        buffer.append = '.group-body';
                        buffer.render(data);

                        var srt = new View();
                        srt.wrap_el = false;
                        srt.template = 'sort-table';
                        srt.append = '.sort-table';
                        srt.render(data);

                    }

                    frameView.fill();
                    $("#group").loading_stop();

                }
            });
        };

        this.select_all = function (e) {
            if ($(e).closest('table').find('input[type=checkbox]:checked').length) {
                $(e).closest('table').find('input[type=checkbox]').prop('checked', false);
            } else {
                $(e).closest('table').find('input[type=checkbox]').prop('checked', true);
            }
        };

        this.delete_selected = function (e) {
            var tracks = [];
            var track_ids = [];
            $(e).closest('.tab-pane').find('input[type=checkbox]:checked').each(function () {
                var track = {
                    id: $(this).closest('tr').attr('id'),
                    title: $(this).closest('tr').find('input[name=title]').val(),
                    artist: $(this).closest('tr').find('input[name=artist]').val()
                };

                if ($.inArray($(this).closest('tr').attr('id'), track_ids) === -1) {
                    track_ids.push($(this).closest('tr').attr('id'));
                    tracks.push(track);
                }
            });
            dialog.show(
                'Delete tracks', '<div class="delete-tracks-holder"></div>'
            );

            var dt = new DeleteTracks();
            dt.render({
                tracks: tracks
            });
        };

        this.do_delete = function (e) {

            var _this = this;

            $(".dialog").loading();

            var data = {};

            var elems = [];
            $(e).closest('form').find('input[name=elems\\[\\]]').each(function () {
                elems.push($(this).val());
            });
            data['elems'] = elems;
            data['stream_id'] = _this.stream_id;
            data['i'] = [];
            data['group_id'] = "";
            data['stream_id'] = "";

            data['action'] = 'delete-track';

            $.ajax({
                type: 'POST',
                url: "/stream/database/playlist.json",
                data: {
                    data: JSON.stringify(data)
                },
                success: function (data) {
                    $(".dialog").loading_stop();
                    _this.update_group();
                    $(".dialog").find('.close').click();
                }
            });
        };


        this.paste_into = function (e) {
            var _this = this;
            $("#edit-playlists").loading();
            var data = $('#edit-playlistssearch-form').serializeObject();

            data["i"] = [];
            data["elems"] = [];
            data["action"] = 'paste-into';
            data['stream_id'] = _this.stream_id;
            data['group_id'] = $(e).closest('tr').attr('id');
            var w = new Date().getTime();

            $('.dragging .active input:checked').closest('tr').each(function (index) {
                data['elems'][index] = {
                    id: $(this).find('input[name=id]').val(),
                    weight: w
                };
                w += 1;
            });

            $.ajax({
                type: 'POST',
                url: "/stream/database/playlist.json",
                data: {
                    data: JSON.stringify(data)
                },
                success: function (data) {
                    $("#edit-playlists").loading_stop();
                    _this.displayPlaylists('edit-playlists');
                }
            });
        };

        this.sort = function (elem, sort) {
            var form = $(elem).closest('.tab-pane').find('form');
            form.find('input[name=order]').val(sort);
            if ($(elem).closest('.sort .active').data('sort') == sort) {
                if (form.find('input[name=asc]').val() == 1) {
                    form.find('input[name=asc]').val(-1);
                } else {
                    form.find('input[name=asc]').val(1);
                }
            }
            form.submit();
        };


        this.next_page = function (obj, page) {
            var _this = this;
            var id = $(obj).closest('table').attr('id');
            if (id == "group") {
                _this.update_group(page, false);
            } else if (id == "playlists-table") {
                $(obj).closest('.tab-pane').find('> form input[name=page]').val(page+1);
                _this.playlist('playlists');
            } else if (id == "edit-playlists-table") {
                $(obj).closest('.tab-pane').find('> form input[name=page]').val(page+1);
                _this.playlist('edit-playlists');
            } else if (id == "favorites-table") {
                $(obj).closest('.tab-pane').find('> form input[name=page]').val(page+1);
                _this.playlist('favorites');
            } else if (id == "edit-favorites-table") {
                $(obj).closest('.tab-pane').find('> form input[name=page]').val(page+1);
                _this.playlist('edit-favorites');
            }
        };

        this.prev_page = function (obj, page) {
            var _this = this;
            var id = $(obj).closest('table').attr('id');
            if (id == "group") {
                _this.update_group(page, true);
            } else if (id == "playlists-table") {
                $(obj).closest('.tab-pane').find('> form input[name=page]').val(page-1);
                _this.playlist('playlists');
            } else if (id == "edit-playlists-table") {
                $(obj).closest('.tab-pane').find('> form input[name=page]').val(page-1);
                _this.playlist('edit-playlists');
            } else if (id == "favorites-table") {
                $(obj).closest('.tab-pane').find('> form input[name=page]').val(page-1);
                _this.playlist('favorites');
            } else if (id == "edit-favorites-table") {
                $(obj).closest('.tab-pane').find('> form input[name=page]').val(page-1);
                _this.playlist('edit-favorites');
            }
        };

        this.paste_above_buffer = function (e) {
            $(e).closest('tr').before($('.dragging .active input:checked').closest('tr').clone());
            updates.update_buffer();
        };

        this.remove_from_buffer = function (e) {
            $(e).closest('tr').remove();
            updates.update_buffer();
        };

        this.paste_above_playlists = function (e) {
            var _this = this;
            var elms = $('.dragging .active input:checked').closest('tr').clone();
            elms.attr('data-append', true);
            $(e).closest('tr').before(elms);
            _this.update_playlists();
        };
        this.remove_from_playlists = function (e) {
            var _this = this;
            $(e).closest('tr').attr('data-remove', true);
            $(e).closest('tr').hide();
            _this.update_playlists();
        };
        this.paste_above_favorites = function (e) {
            var _this = this;
            var elms = $('.dragging .active input:checked').closest('tr').clone();
            elms.attr('data-append', true);
            $(e).closest('tr').before(elms);
            _this.update_favorites();
        };
        this.remove_from_favorites = function (e) {
            var _this = this;
            $(e).closest('tr').attr('data-remove', true);
            $(e).closest('tr').hide();
            _this.update_favorites();
        };



        this.swipe = function (direction, otr) {
            var _this = this;

            var width = otr.width();
            var height = otr.height();
            var tr = null;
            var top = otr.position().top;

            if (direction == 'left' && otr.next().hasClass('swipe-left')) {
                var tr = otr.next();
                tr.removeClass('hide');
            } else if (direction == 'right' && otr.next().next().hasClass('swipe-right')) {
                var tr = otr.next().next();
                tr.removeClass('hide');
            } else {
                return false;
            }

            otr.addClass('moving');
            otr.css('left', '0px');
            otr.css('top', top+'px');
            otr.css('width', width+'px');
            otr.css('z-index', '5');
            // substract border...
            if(navigator.userAgent.toLowerCase().indexOf('firefox') > -1) {
                otr.css('margin-top', '-1px');
            }

            otr.css('height', height+'px');
            tr.css('height', height+'px');
            tr.css('z-index', '4');

            if (direction == 'left') {
                otr.animate({left: -width}, 500, function () {
                    otr.addClass('hide');
                });
            } else {
                otr.animate({left: width}, 500, function () {
                    otr.addClass('hide');
                });
            }
        };

        this.unswipe = function (e) {
            var tr = $(e).closest('tr');

            if (tr.hasClass('swipe-left')) {
                var otr = tr.prev();
            } else if (tr.hasClass('swipe-right')) {
                var otr = tr.prev().prev();
            }

            otr.removeClass('hide');

            otr.animate({left: '0px'}, 500, function () {
                otr.removeClass('moving');
                otr.css('left', '');
                otr.css('top', '');
                otr.css('width', '');
//        otr.css('height', '');
                otr.css('z-index', '');
                otr.css('margin-top', '');

                tr.addClass('hide');
//        tr.css('height', '');
                tr.css('z-index', '');

            });
        };

        this.generateUUID = function (){
            var d = new Date().getTime();
            var uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
                var r = (d + Math.random()*16)%16 | 0;
                d = Math.floor(d/16);
                return (c=='x' ? r : (r&0x7|0x8)).toString(16);
            });
            return uuid;
        };


    });

});
