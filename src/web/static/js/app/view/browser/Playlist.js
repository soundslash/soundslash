define(function (require) {
    "use strict";

    var user = require('model/User'),
        frameView = require('view/Frame'),
        Buffer = require('view/Buffer'),
        dialog = require('view/Dialog'),
        Stream = require('model/Stream'),
        _ = require('lib/jquery.serializeObject.min');

    return extend.View(function () {

        var _this = this;

        this.editPlaylists = function (a) {

            $('.edit-db-menu a.active').removeClass('active');
            $(a).addClass('active');

            if ($('#edit-playlists tr').length == 0) {
                this.playlist('edit-playlists');
            }
        };

        this.databasePlaylists = function(a) {

            $('.db-menu a.active').removeClass('active');
            $(a).addClass('active');
            $(a).tab('show');

            if ($('#playlists tr').length == 0) {
                this.playlist();
            }
            frameView.fill();
        };
        this.displayPlaylist = function(parent, tr) {
            $('#'+parent+'search-form input[name=search]').val("");
            $('#'+parent+'search-form input[name=group_id]').val($(tr).attr('id'));
            $('#'+parent+'search-form input[name=groups]').val("false");
            $('#'+parent+'search-form input[name=page]').val("1");

            this.playlist(parent);
        };

        this.displayPlaylists = function(parent) {
            $('#'+parent+'ssearch-form input[name=group_id]').val("null");
            $('#'+parent+'search-form input[name=groups]').val("true");
            $('#'+parent+'search-form input[name=page]').val("1");

            this.playlist(parent);
        };



        this.playlist = function(parent) {

            var _this = this;
            if (parent === undefined) parent = 'playlists';

            $('#'+parent+' form').show();

            $('#'+parent).loading_center();
            $.ajax({
                type: 'POST',
                url: "/stream/database/search.json",
                data: $('#'+parent+'search-form').serialize() +
                    "&stream_id="+_this.stream_id
                ,
                success: function (data) {
                    data['parent'] = parent;

                    var buffer = new Buffer();
                    buffer.append = '#'+parent+' .'+parent+'-body';
                    buffer.render(data).afterRender(function () {

                        $('.format-duration').each(function (index) {
                            $(this).html(format_seconds($(this).data('duration') / 1000000000));
                        });

                        if (data.nav)
                            _this.do_draggable();

                        $('#'+parent+' .'+parent+'-body .mark .checkbox').click(function () {
                            data['playlist'] = {
                                'name': $(this).closest('tr').find('.playlist-no-action .playlist').html(),
                                'id': $(this).closest('tr').attr('id')
                            };

                            var tps = new View();
                            tps.wrap_el = false;
                            tps.template = 'stream-program-selected';
                            tps.append = '#'+parent+' .'+parent+'-body';
                            tps.afterRender(function () {
                                $('#'+parent+' form').hide();
                                frameView.fill();
                            });
                            tps.render(data);


                        });

                        frameView.fill();
                        $('#'+parent).loading_stop();
                    });


                },
                error: function (data) {
                    $('#'+parent).loading_stop();
                }
            });

        };



        this.update_playlists = function() {
            var _this = this;
            if ($("#edit-playlists").is_loading())
                return;
            $("#edit-playlists").loading();

            var data = $('#edit-playlistssearch-form').serializeObject();

            data['stream_id'] = _this.stream_id;
            data['i'] = [];
            data['elems'] = [];

            $("#edit-playlists .edit-playlists-body tr.track").each(function (index) {
                if ($(this).data('remove') == true) {
                    data['action'] = 'remove';
                    data['i'].push(index);
                }
                if ($(this).data('append') == true) {
                    data['action'] = 'append';
                    data['i'].push(index);
                }
                if ($(this).data('move') == true) {
                    data['action'] = 'move';
                    data['i'].push(index);
                }
                data['elems'][index] = {
                    i: index,
                    id: $(this).find('input[name=id]').val(),
                    weight: $(this).find('input[name=weight]').val()
                };
            });

            $.ajax({
                type: 'POST',
                url: "/stream/database/playlist.json",
                data: {
                    data: JSON.stringify(data)
                },
                success: function (data) {
                    $("#edit-playlists").loading_stop();
                    _this.playlist('edit-playlists');
                }
            });
        };


        this.create_playlist = function () {
            var create = $('.create-playlist');
            if (create.hasClass('hide')) {

                create.removeClass('hide');
                create.css('height', '0px');
                create.find('td *').hide();
                create.animate({'height': '42px'}, 500, function () {
                    create.find('td *').show();
                })
            } else {
                create.find('td *').hide();
                create.animate({'height': '0px'}, 500, function () {
                    create.addClass('hide');
                })
            }
        };

        this.do_create_playlist = function () {
            var _this = this;
            $("#edit-playlists").loading();

            var data = $('#edit-playlistssearch-form').serializeObject();

            data['stream_id'] = _this.stream_id;
            data['i'] = [];
            data['elems'] = [];

            data['action'] = 'create';
            data['name'] = $('.create-playlist input[name=playlist_name]').val();


            $.ajax({
                type: 'POST',
                url: "/stream/database/playlist.json",
                data: {
                    data: JSON.stringify(data)
                },
                success: function (data) {
                    _this.create_playlist();
                    $("#edit-playlists").loading_stop();
                    _this.playlist('edit-playlists');
                }
            });
        };

        this.do_remove_playlist = function (e) {
            var _this = this;
            $("#edit-playlists").loading();

            var data = $('#edit-playlistssearch-form').serializeObject();

            data['group_id'] = $(e).closest('tr').prev().attr('id');
            data['stream_id'] = _this.stream_id;
            data['i'] = [];
            data['elems'] = [];

            data['action'] = 'delete';

            $.ajax({
                type: 'POST',
                url: "/stream/database/playlist.json",
                data: {
                    data: JSON.stringify(data)
                },
                success: function (data) {
                    $("#edit-playlists").loading_stop();
                    _this.playlist('edit-playlists');
                }
            });
        };
        this.remove_playlist = function (e) {
            var _this = this;
            var playlist_id = $(e).closest('tr').attr('id');

            _this.swipe('left', $(e).closest('tr'));

        };

        this.do_edit_playlist = function (e) {
            var _this = this;
            $("#edit-playlists").loading();

            var data = $('#edit-playlistssearch-form').serializeObject();

            data['group_id'] = $(e).closest('tr').prev().prev().attr('id');
            data['stream_id'] = _this.stream_id;
            data['i'] = [];
            data['elems'] = [];

            data['action'] = 'rename';
            data['name'] = $(e).closest('tr').find('input').val();


            $.ajax({
                type: 'POST',
                url: "/stream/database/playlist.json",
                data: {
                    data: JSON.stringify(data)
                },
                success: function (data) {
                    $("#edit-playlists").loading_stop();
                    _this.playlist('edit-playlists');
                }
            });
        };

        this.edit_playlist = function (e) {
            var _this = this;
            var playlist_id = $(e).closest('tr').attr('id');

            _this.swipe('right', $(e).closest('tr'));

        };



    });
});
