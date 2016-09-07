
function format_seconds(seconds, h) {
    var hours = Math.floor(seconds / 60 / 60 % 60);
    var minutes = Math.floor(seconds / 60 % 60);
    var seconds = Math.ceil(seconds % 60);
    if (minutes <= 9) minutes = "0"+minutes;
    if (seconds <= 9) seconds = "0"+seconds;
    if (h) {
        return hours + ":" + minutes + ":" + seconds;
    } else {
        return minutes + ":" + seconds;
    }
}

function format_epoch(seconds) {
    var d = new Date(seconds*1000);
    var hours = d.getHours();
    var minutes = d.getMinutes();
    var seconds = d.getSeconds();
    if (hours <= 9) hours = "0"+hours;
    if (minutes <= 9) minutes = "0"+minutes;
    if (seconds <= 9) seconds = "0"+seconds;
    return hours + ":" + minutes + ":" + seconds;
}


function do_draggable() {

    $("#database tbody.sortable-group")
        .sortable({
            connectWith: [".sortable-buffer", ".sortable-live-loop", ".sortable-edit-playlists", ".sortable-edit-favorites"],
            items: "> tr",
            cancel: ".nodrag",
//                helper:"clone",
            zIndex: 999990,
            helper: function (e, li) {
                copyHelper = li.clone().insertAfter(li);

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
                $('.dragging .active input:checked').attr('checked', false);
            },
            stop: function (event, ui) {
                if (ui.item.closest('table').attr('id') == "buffer") {
                    update_buffer();
                }
                if (ui.item.closest('table').attr('id') == "edit-playlists-table") {
                    // when item is dragged to edit playlist
                    $(ui.item).attr('data-append', true);
                    update_playlists();
                }
                if (ui.item.closest('table').attr('id') == "edit-favorites-table") {
                    $(ui.item).attr('data-append', true);
                    update_favorites();
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
                copyHelper = li.clone().insertAfter(li);
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

                $('.dragging .active input:checked').attr('checked', false);
            },
            stop: function (event, ui) {
                if (ui.item.closest('table').attr('id') == "buffer") {
                    update_buffer();
                }
                if (ui.item.closest('table').attr('id') == "edit-playlists-table") {
                    $(ui.item).attr('data-append', true);
                    update_playlists();
                }
                if (ui.item.closest('table').attr('id') == "edit-favorites-table") {
                    $(ui.item).attr('data-append', true);
                    update_favorites();
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
                copyHelper = li.clone().insertAfter(li);
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

                $('.dragging .active input:checked').attr('checked', false);
            },
            stop: function (event, ui) {
                if (ui.item.closest('table').attr('id') == "buffer") {
                    update_buffer();
                }
                if (ui.item.closest('table').attr('id') == "edit-playlists-table") {
                    update_playlists();
                }
                if (ui.item.closest('table').attr('id') == "edit-favorites-table") {
                    update_favorites();
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
                copyHelper = li.clone().insertAfter(li);
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

                $('.dragging .active input:checked').attr('checked', false);
            },
            stop: function (event, ui) {
                if (ui.item.closest('table').attr('id') == "buffer") {
                    update_buffer();
                }
                if (ui.item.closest('table').attr('id') == "edit-playlists-table") {
                    update_playlists();
                }
                if (ui.item.closest('table').attr('id') == "edit-favorites-table") {
                    update_favorites();
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
                $('.dragging .active input:checked').attr('checked', false);

            },
            stop: function (event, ui) {

                update_buffer();
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

                $('.dragging .active input:checked').attr('checked', false);
            },
            stop: function (event, ui) {
                if (ui.item.closest('table').attr('id') == "edit-playlists-table") {
                    ui.item.closest('tbody').find('tr[data-remove=true]').remove();
                    ui.item.attr('data-move', true);
                }
                update_playlists();
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

                $('.dragging .active input:checked').attr('checked', false);
            },
            stop: function (event, ui) {

                if (ui.item.closest('table').attr('id') == "edit-favorites-table") {
                    ui.item.closest('tbody').find('tr[data-remove=true]').remove();
                    ui.item.attr('data-move', true);
                }
                update_favorites();
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

                $('.dragging .active input:checked').attr('checked', false);
            },
            stop: function (event, ui) {

            }

        })
        .disableSelection();


//        $.extend($.expr[":"], {
//            "containsIN": function(elem, i, match, array) {
//                return (elem.textContent || elem.innerText || "").toLowerCase().indexOf((match[3] || "").toLowerCase()) >= 0;
//            }
//        });
//
//        $('#textBoxID').keyup(function(){
//            $('td').css("background-color",'');
//            var value= $(this).val();
//            $('td:containsIN("'+value+'")').css("background-color",'red');
//        });
//
//                    $('#groupsearch').keyup(
//                            function(){
//                                var searchText = $(this).val();
//
//                                if (searchText.length > 0) {
//                                    $('#group tbody tr').hide();
//                                    $('#group tbody td:containsIN(' + searchText +')').each(function() {
//                                        $(this).closest('tr').show();
//                                    });
////                                    $('#group td:not(:containsIN('+searchText+'))')
////                                            .css('background-color','transparent');
//
//                                }
//
//                                if (searchText.length == 0) {
//                                    $('#group tbody tr').show();
//                                }
//                            });

}


function update_group(page, prev) {
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
        data: $('#groupsearch-form').serialize() + "&stream_id="+window.stream_id,
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
                $('.group-body').html(tmpl(
                    'template-buffer',
                    data
                ));
                $('.sort-table').html(tmpl(
                    'template-sort-table',
                    data
                ));

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
                    UI.updateRepeats(window.selected_repeats);
                });

                $('.format-duration').each(function (index) {
                    $(this).html(format_seconds($(this).data('duration') / 1000000000));
                });
                do_draggable();
            }

            UI.fill();
            $("#group").loading_stop();

        }
    });
}


function update_playlists() {
    if ($("#edit-playlists").is_loading())
        return;
    $("#edit-playlists").loading();

    var data = $('#edit-playlistssearch-form').serializeObject();

    data['stream_id'] = $('#stream').data('id');
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
            UI.playlist('edit-playlists');
        }
    });
}

function update_favorites() {

    $("#edit-favorites").loading();

    var data = $('#edit-favoritessearch-form').serializeObject();


    data['stream_id'] = $('#stream').data('id');
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
            UI.favorites('edit-favorites');
        }
    });
}

function paste_into(e) {
    $("#edit-playlists").loading();
    var data = $('#edit-playlistssearch-form').serializeObject();

    data["i"] = [];
    data["elems"] = [];
    data["action"] = 'paste-into';
    data['stream_id'] = $('#stream').data('id');
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
            UI.displayPlaylists('edit-playlists');
        }
    });
}

function sort(elem, sort) {
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
}


function next_page(obj, page) {
    var id = $(obj).closest('table').attr('id');
    if (id == "group") {
        update_group(page, false);
    } else if (id == "playlists-table") {
        $(obj).closest('.tab-pane').find('> form input[name=page]').val(page+1);
        UI.playlist('playlists');
    } else if (id == "edit-playlists-table") {
        $(obj).closest('.tab-pane').find('> form input[name=page]').val(page+1);
        UI.playlist('edit-playlists');
    } else if (id == "favorites-table") {
        $(obj).closest('.tab-pane').find('> form input[name=page]').val(page+1);
        UI.playlist('favorites');
    } else if (id == "edit-favorites-table") {
        $(obj).closest('.tab-pane').find('> form input[name=page]').val(page+1);
        UI.playlist('edit-favorites');
    }
}
function prev_page(obj, page) {
    var id = $(obj).closest('table').attr('id');
    if (id == "group") {
        update_group(page, true);
    } else if (id == "playlists-table") {
        $(obj).closest('.tab-pane').find('> form input[name=page]').val(page-1);
        UI.playlist('playlists');
    } else if (id == "edit-playlists-table") {
        $(obj).closest('.tab-pane').find('> form input[name=page]').val(page-1);
        UI.playlist('edit-playlists');
    } else if (id == "favorites-table") {
        $(obj).closest('.tab-pane').find('> form input[name=page]').val(page-1);
        UI.playlist('favorites');
    } else if (id == "edit-favorites-table") {
        $(obj).closest('.tab-pane').find('> form input[name=page]').val(page-1);
        UI.playlist('edit-favorites');
    }
}

function paste_above_buffer(e) {
    $(e).closest('tr').before($('.dragging .active input:checked').closest('tr').clone());
    update_buffer();
}
function remove_from_buffer(e) {
    $(e).closest('tr').remove();
    update_buffer();
}
function paste_above_playlists(e) {
    var elms = $('.dragging .active input:checked').closest('tr').clone();
    elms.attr('data-append', true);
    $(e).closest('tr').before(elms);
    update_playlists();
}
function remove_from_playlists(e) {
    $(e).closest('tr').attr('data-remove', true);
    $(e).closest('tr').hide();
    update_playlists();
}
function paste_above_favorites(e) {
    var elms = $('.dragging .active input:checked').closest('tr').clone();
    elms.attr('data-append', true);
    $(e).closest('tr').before(elms);
    update_favorites();
}
function remove_from_favorites(e) {
    $(e).closest('tr').attr('data-remove', true);
    $(e).closest('tr').hide();
    update_favorites();
}

function create_playlist() {
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
}

function do_create_playlist() {
    $("#edit-playlists").loading();

    var data = $('#edit-playlistssearch-form').serializeObject();

    data['stream_id'] = $('#stream').data('id');
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
            create_playlist();
            $("#edit-playlists").loading_stop();
            UI.playlist('edit-playlists');
        }
    });
}

function do_remove_playlist(e) {
    $("#edit-playlists").loading();

    var data = $('#edit-playlistssearch-form').serializeObject();

    data['group_id'] = $(e).closest('tr').prev().attr('id');
    data['stream_id'] = $('#stream').data('id');
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
            UI.playlist('edit-playlists');
        }
    });
}
function remove_playlist(e) {
    var playlist_id = $(e).closest('tr').attr('id');

    swipe('left', $(e).closest('tr'));

}

function do_edit_playlist(e) {
    $("#edit-playlists").loading();

    var data = $('#edit-playlistssearch-form').serializeObject();

    data['group_id'] = $(e).closest('tr').prev().prev().attr('id');
    data['stream_id'] = $('#stream').data('id');
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
            UI.playlist('edit-playlists');
        }
    });
}

function edit_playlist(e) {
    var playlist_id = $(e).closest('tr').attr('id');

    swipe('right', $(e).closest('tr'));

}


function swipe(direction, otr) {

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
}

function unswipe(e) {
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
}

function on_start() {

    $(document).ready(function () {
        init_updates();
    });
}

function generateUUID(){
    var d = new Date().getTime();
    var uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        var r = (d + Math.random()*16)%16 | 0;
        d = Math.floor(d/16);
        return (c=='x' ? r : (r&0x7|0x8)).toString(16);
    });
    return uuid;
}


function tags(e) {


    $.ajax({
        type: 'GET',
        url: "/stream/tags.json",
        data: {
            stream_id: $('#stream').data('id'),
            media_id: $(e).closest('tr').attr('id')
        },
        success: function (data) {

            UI.dialog("Tags "+data['media']['original_filename'], tmpl('template-stream-edit-tags', data));
            $('.main').loading_stop();
        },
        error: function (data) {
            $('.main').loading_stop();
        }
    });

}

function select_all(e) {
    if ($(e).closest('table').find('input[type=checkbox]:checked').length) {
        $(e).closest('table').find('input[type=checkbox]').prop('checked', false);
    } else {
        $(e).closest('table').find('input[type=checkbox]').prop('checked', true);
    }
}

function delete_selected(e) {
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
    UI.dialog(
        'Delete tracks',
       tmpl(
            'template-delete-tracks',
           {
               tracks: tracks
           }
       ));
}

function do_delete(e) {


    $(".dialog").loading();

    var data = {};

    var elems = [];
    $(e).closest('form').find('input[name=elems\\[\\]]').each(function () {
        elems.push($(this).val());
    });
    data['elems'] = elems;
    data['stream_id'] = $('#stream').data('id');
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
            update_group();
            $(".dialog").find('.close').click();
        }
    });
}