define(function (require) {
    "use strict";

    var user = require('model/User'),
        frameView = require('view/Frame'),
        Buffer = require('view/Buffer'),
        dialog = require('view/Dialog'),
        Stream = require('model/Stream');

    return extend.View(function () {

        var _this = this;


        this.favorites = function(parent) {

            var _this = this;
            if (parent === undefined) parent = 'favorites';

            $('#'+parent+'').loading_center();
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

                        _this.do_draggable();

                        frameView.fill();
                        $('#'+parent+'').loading_stop();
                    });


                },
                error: function (data) {
                    $('#'+parent+'').loading_stop();
                }
            });

        };


        this.update_favorites = function () {
            var _this = this;

            $("#edit-favorites").loading();

            var data = $('#edit-favoritessearch-form').serializeObject();


            data['stream_id'] = _this.stream_id;
            data['i'] = [];
            data['elems'] = [];

            $("#edit-favorites .edit-favorites-body tr.track").each(function (index) {
                if ($(this).data('remove') == true) {
                    data['action'] = 'favorites-remove';
                    data['i'].push(index);
                }
                if ($(this).data('append') == true) {
                    data['action'] = 'favorites-append';
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

                    $("#edit-favorites").loading_stop();
                    _this.favorites('edit-favorites');
                }
            });
        };


        this.databaseFavorites = function(a) {

            $('.db-menu a.active').removeClass('active');
            $(a).addClass('active');
            if ($('#favorites tr').length == 0) {
                this.favorites('favorites');
            }
        };
        this.editFavorites = function (a) {

            $('.edit-db-menu a.active').removeClass('active');
            $(a).addClass('active');

            if ($('#edit-favorites tr').length == 0) {
                this.favorites('edit-favorites');
            }
        };
    });
});
