define(function (require) {
    "use strict";

    var user = require('model/User'),
        frameView = require('view/Frame'),
        Buffer = require('view/Buffer'),
        EditTags = require('view/EditTags'),
        dialog = require('view/Dialog'),
        updates = require('model/Updates'),
        Stream = require('model/Stream'),
        _ = require('lib/jquery-ui-1.11.1');

    var Buffer = require('view/browser/Buffer'),
        Favorite = require('view/browser/Favorite'),
        Media = require('view/browser/Media'),
        Playlist = require('view/browser/Playlist'),
        Repeat = require('view/browser/Repeat'),
        Tag = require('view/browser/Tag');

    var Browser = extend.View(function () {


        this.initEditBrowser = function () {

            var _this = this;
            var stream = new Stream();
            stream.getStream().done(function (data) {


                _this.stream_id = data.stream._id;
                _this.playlist('edit-playlists');

                $('#edit-playlistssearch-form').submit(function () {
                    _this.playlist('edit-playlists');
                    return false;
                });
                $('#edit-playlistssearch-form').keyup(
                    function () {
                        clearTimeout($.data(this, 'timer'));
                        $(this).data('timer', setTimeout(function() {
                            _this.playlist('edit-playlists');
                        }, 200));
                    });

                $('#edit-favoritessearch-form').submit(function () {
                    _this.favorites('edit-favorites');
                    return false;
                });
                $('#edit-favoritessearch-form').keyup(
                    function () {
                        clearTimeout($.data(this, 'timer'));
                        $(this).data('timer', setTimeout(function() {
                            _this.favorites('edit-favorites');
                        }, 200));

                    });
            });
        };

        this.initBrowser = function (ajax) {

            var _this = this;
            var stream = new Stream();
            stream.getStream().done(function (data) {

                _this.stream_id = data.stream._id;

                if (ajax === undefined)
                    _this.update_group(0);

                $('#playlistssearch-form').submit(function () {
                    _this.playlist();
                    return false;
                });
                $('#playlistssearch-form').keyup(
                    function () {
                        clearTimeout($.data(this, 'timer'));
                        $(this).data('timer', setTimeout(function() {
                            _this.playlist();
                        }, 200));
                    });

                $('#favoritessearch-form').submit(function () {
                    _this.favorites();
                    return false;
                });
                $('#favoritessearch-form').keyup(
                    function () {
                        clearTimeout($.data(this, 'timer'));
                        $(this).data('timer', setTimeout(function() {
                            _this.favorites();
                        }, 200));

                    });

                $('#groupsearch-form').submit(function () {
                    _this.update_group(0);
                    return false;
                });

                $('#groupsearch').keyup(
                    function () {
                        clearTimeout($.data(this, 'timer'));
                        $(this).data('timer', setTimeout(function() {
                            _this.update_group(0);
                        }, 200));

                    });

                $('#database-order').chosen({disable_search_threshold: 10});
                $('#database-order').change(function () {
                    _this.update_group(0);
                });
            });


        };


        this.database = function(a) {

            $('.db-menu a.active').removeClass('active');
            $(a).addClass('active');
        };

        this.do_draggable = function () {

            var _this = this;
            $("#database tbody.sortable-group")
                .sortable({
                    connectWith: [".sortable-buffer", ".sortable-live-loop", ".sortable-edit-playlists", ".sortable-edit-favorites"],
                    items: "> tr",
                    cancel: ".nodrag",
//                helper:"clone",
                    zIndex: 999990,
                    helper: function (e, li) {
                        var copyHelper = li.clone().insertAfter(li);

                        return li.clone().css('width', 'auto');
                    },
                    beforeStop: function (event, ui) {
                        if (ui.item.closest('table').attr('id') == "group" ||
                            ui.item.closest('table').attr('id') == "previous" ||
                            ui.item.closest('table').attr('id') == "playlists-table" ||
                            ui.item.closest('table').attr('id') == "favorites-table") {
                            $(ui.item).remove();
                        }
                    },
                    start: function (event, ui) {
                        ui.placeholder.html("<td colspan='10'></td>");
                        $('.dragging .active input:checked').attr('checked', false);
                    },
                    stop: function (event, ui) {
                        if (ui.item.closest('table').attr('id') == "buffer") {
                            updates.update_buffer();
                        }
                        if (ui.item.closest('table').attr('id') == "edit-playlists-table") {
                            // when item is dragged to edit playlist
                            $(ui.item).attr('data-append', true);
                            _this.update_playlists();
                        }
                        if (ui.item.closest('table').attr('id') == "edit-favorites-table") {
                            $(ui.item).attr('data-append', true);
                            _this.update_favorites();
                        }
                    }

                })
                .disableSelection();


            $("#playlists tbody.sortable-playlist")
                .sortable({
                    connectWith: [".sortable-buffer", ".sortable-live-loop", ".sortable-edit-playlists", ".sortable-edit-favorites"],
                    items: "> tr",
                    cancel: ".nodrag",
//                helper:"clone",
                    zIndex: 999990,
                    helper: function (e, li) {
                        var copyHelper = li.clone().insertAfter(li);
                        return li.clone().css('width', 'auto');
                    },
                    beforeStop: function (event, ui) {
                        if (ui.item.closest('table').attr('id') == "group" ||
                            ui.item.closest('table').attr('id') == "previous" ||
                            ui.item.closest('table').attr('id') == "playlists-table" ||
                            ui.item.closest('table').attr('id') == "favorites-table") {
                            $(ui.item).remove();
                        }
                    },
                    start: function (event, ui) {

                        ui.placeholder.html("<td colspan='10'></td>");
                        $('.dragging .active input:checked').attr('checked', false);
                    },
                    stop: function (event, ui) {
                        if (ui.item.closest('table').attr('id') == "buffer") {
                            updates.update_buffer();
                        }
                        if (ui.item.closest('table').attr('id') == "edit-playlists-table") {
                            $(ui.item).attr('data-append', true);
                            _this.update_playlists();
                        }
                        if (ui.item.closest('table').attr('id') == "edit-favorites-table") {
                            $(ui.item).attr('data-append', true);
                            _this.update_favorites();
                        }
                    }

                })
                .disableSelection();

            $("#favorites tbody.sortable-favorites")
                .sortable({
                    connectWith: [".sortable-buffer", ".sortable-live-loop", ".sortable-edit-playlists", ".sortable-edit-favorites"],
                    items: "> tr",
                    cancel: ".nodrag",
//                helper:"clone",
                    zIndex: 999990,
                    helper: function (e, li) {
                        var copyHelper = li.clone().insertAfter(li);
                        return li.clone().css('width', 'auto');
                    },
                    beforeStop: function (event, ui) {
                        if (ui.item.closest('table').attr('id') == "group" ||
                            ui.item.closest('table').attr('id') == "previous" ||
                            ui.item.closest('table').attr('id') == "playlists-table" ||
                            ui.item.closest('table').attr('id') == "favorites-table") {
                            $(ui.item).remove();
                        }
                    },
                    start: function (event, ui) {

                        ui.placeholder.html("<td colspan='10'></td>");
                        $('.dragging .active input:checked').attr('checked', false);
                    },
                    stop: function (event, ui) {
                        if (ui.item.closest('table').attr('id') == "buffer") {
                            updates.update_buffer();
                        }
                        if (ui.item.closest('table').attr('id') == "edit-playlists-table") {
                            _this.update_playlists();
                        }
                        if (ui.item.closest('table').attr('id') == "edit-favorites-table") {
                            _this.update_favorites();
                        }
                    }

                })
                .disableSelection();

            $("#previous tbody.sortable-previous")
                .sortable({
                    connectWith: [".sortable-buffer", ".sortable-live-loop", ".sortable-edit-playlists", ".sortable-edit-favorites"],
                    items: "> tr",
                    cancel: ".nodrag",
//                helper:"clone",
                    zIndex: 999990,
                    helper: function (e, li) {
//                        return li;
                        var copyHelper = li.clone().insertAfter(li);
                        return li.clone().css('width', 'auto');
                    },
                    beforeStop: function (event, ui) {
                        if (ui.item.closest('table').attr('id') == "group" ||
                            ui.item.closest('table').attr('id') == "previous" ||
                            ui.item.closest('table').attr('id') == "playlists-table" ||
                            ui.item.closest('table').attr('id') == "favorites-table") {
                            $(ui.item).remove();
                        }
                    },
                    start: function (event, ui) {

                        ui.placeholder.html("<td colspan='10'></td>");
                        $('.dragging .active input:checked').attr('checked', false);
                    },
                    stop: function (event, ui) {
                        if (ui.item.closest('table').attr('id') == "buffer") {
                            updates.update_buffer();
                        }
                        if (ui.item.closest('table').attr('id') == "edit-playlists-table") {
                            _this.update_playlists();
                        }
                        if (ui.item.closest('table').attr('id') == "edit-favorites-table") {
                            _this.update_favorites();
                        }
                    }

                })
                .disableSelection();

            $("#buffer tbody.sortable-buffer")
                .sortable({
                    // just remove the item
                    connectWith: ".sortable-group",
                    items: "> tr",
                    cancel: ".nodrag",
//                helper:"clone",
                    zIndex: 999990,
                    beforeStop: function (event, ui) {
                        if (ui.item.closest('table').attr('id') == "group" ||
                            ui.item.closest('table').attr('id') == "previous" ||
                            ui.item.closest('table').attr('id') == "playlists-table" ||
                            ui.item.closest('table').attr('id') == "favorites-table") {
                            $(ui.item).remove();
                        }
                    },
                    start: function (event, ui) {

                        ui.placeholder.html("<td colspan='10'></td>");
                        $('.dragging .active input:checked').attr('checked', false);

                    },
                    stop: function (event, ui) {

                        updates.update_buffer();
                    }

                })
                .disableSelection();

            $("#edit-playlists tbody.sortable-edit-playlists")
                .sortable({
                    connectWith: ".sortable-group",
                    items: "> tr",
                    cancel: ".nodrag",
//                helper:"clone",
                    zIndex: 999990,
                    helper: function (e, li) {
                        var copyHelper = li.clone().insertAfter(li);
                        var elem = li.clone().css('width', 'auto');

                        //when item is dragged FROM edit playlist
                        //clone and hide
                        $(copyHelper).attr('data-remove', true);
                        $(copyHelper).hide();

                        return elem;
                    },
                    beforeStop: function (event, ui) {
                        if (ui.item.closest('table').attr('id') == "group" ||
                            ui.item.closest('table').attr('id') == "previous" ||
                            ui.item.closest('table').attr('id') == "playlists-table" ||
                            ui.item.closest('table').attr('id') == "favorites-table") {
                            $(ui.item).remove();
                        }
                    },
                    start: function (event, ui) {

                        ui.placeholder.html("<td colspan='10'></td>");
                        $('.dragging .active input:checked').attr('checked', false);
                    },
                    stop: function (event, ui) {
                        if (ui.item.closest('table').attr('id') == "edit-playlists-table") {
                            ui.item.closest('tbody').find('tr[data-remove=true]').remove();
                            ui.item.attr('data-move', true);
                        }
                        _this.update_playlists();
                    }

                });

            $("#edit-favorites tbody.sortable-edit-favorites")
                .sortable({
                    connectWith: ".sortable-group",
                    items: "> tr",
                    cancel: ".nodrag",
//                helper:"clone",
                    zIndex: 999990,
                    helper: function (e, li) {
                        var copyHelper = li.clone().insertAfter(li);
                        var elem = li.clone().css('width', 'auto');

                        //when item is dragged FROM edit favorites
                        //clone and hide
                        $(copyHelper).attr('data-remove', true);
                        $(copyHelper).hide();

                        return elem;
                    },
                    beforeStop: function (event, ui) {
                        if (ui.item.closest('table').attr('id') == "group" ||
                            ui.item.closest('table').attr('id') == "previous" ||
                            ui.item.closest('table').attr('id') == "playlists-table" ||
                            ui.item.closest('table').attr('id') == "favorites-table") {
                            $(ui.item).remove();
                        }
                    },
                    start: function (event, ui) {

                        ui.placeholder.html("<td colspan='10'></td>");
                        $('.dragging .active input:checked').attr('checked', false);
                    },
                    stop: function (event, ui) {

                        if (ui.item.closest('table').attr('id') == "edit-favorites-table") {
                            ui.item.closest('tbody').find('tr[data-remove=true]').remove();
                            ui.item.attr('data-move', true);
                        }
                        _this.update_favorites();
                    }

                })
                .disableSelection();

            $(".live-holder tbody.sortable-live-loop")
                .sortable({
                    connectWith: ".sortable-group",
                    items: "> tr",
                    cancel: ".nodrag",
//                helper:"clone",
                    zIndex: 999990,
                    beforeStop: function (event, ui) {
                        if (ui.item.closest('table').attr('id') == "group" || ui.item.closest('table').attr('id') == "previous" || ui.item.closest('table').attr('id') == "playlist-table") {
                            $(ui.item).remove();
                        }
                    },
                    start: function (event, ui) {

                        ui.placeholder.html("<td colspan='10'></td>");
                        $('.dragging .active input:checked').attr('checked', false);
                    },
                    stop: function (event, ui) {

                    }

                })
                .disableSelection();


        };




    });

    Browser = extend({target: Browser}, Buffer);
    Browser = extend({target: Browser}, Favorite);
    Browser = extend({target: Browser}, Media);
    Browser = extend({target: Browser}, Playlist);
    Browser = extend({target: Browser}, Repeat);
    Browser = extend({target: Browser}, Tag);

    var browser = new Browser();
    return window.browser = browser;
});