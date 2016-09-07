define(function (require) {
    "use strict";

    var user = require('model/User'),
        frameView = require('view/Frame'),
        Buffer = require('view/Buffer'),
        dialog = require('view/Dialog'),
        Stream = require('model/Stream'),
        EditTags = require('view/EditTags');

    return extend.View(function () {

        this.tags = function (e) {
            var _this = this;


            $.ajax({
                type: 'GET',
                url: "/stream/tags.json",
                data: {
                    stream_id: _this.stream_id,
                    media_id: $(e).closest('tr').attr('id')
                },
                success: function (data) {

                    dialog.show("Tags "+data['media']['original_filename'], '<div class="edit-tags-holder"></div>');
                    var et = new EditTags();
                    et.render(data);

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



    });
});