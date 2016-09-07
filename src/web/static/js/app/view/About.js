
define(function (require) {
    "use strict";

    var Stream = require('model/Stream'),
        frameView = require('view/Frame'),
        _ = require('lib/chosen.jquery.min'),
        _ = require('lib/ajaxinput'),
        _ = require('lib/jquery.autosize.min');

    return extend.View(function () {

        this.template = 'stream-about';
        this.append = '#radio-content';

        this.postinitialize = function (data) {

            $('.lightblue-menu h1.menu-title').html('About');

            $('#radio-content textarea').autosize({append: ""});

            var stream = new Stream();
            stream.getGenresHtml().done(function (streamGenre) {

                $(".stream-genre").append(streamGenre);

                for (var i in data.stream.genres) {
                    $('#radio-content .chosen-select option[value="'+data.stream.genres[i]+'"]')
                        .prop('selected', true);
                }

                $("#radio-content .chosen-select").chosen({
                    no_results_text: "Oops, nothing found!",
                    width: "100%"
                });


                $("#picture-wrap").ajaxinput("picture", '/stream/picture.json', function () {

                    if (data.stream.picture === undefined) {
                        $("#picture-show").html('No image');
                    } else {
                        var img = $("<img>");
                        img.attr("src", "/image.jpg?id="+data.stream.picture+"&thumb=160x160");
                        $("#picture-show").html(img);
                    }

                }, function () {
                    $('#stream-form').loading();
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
                        $('#stream-form').loading_stop();
                    }
                }, false, true);

                $("#background-picture-wrap").ajaxinput("background-picture", '/stream/bg-picture.json', function () {

                    if (data.stream.cover_image === undefined) {
                        $("#background-picture-show").html('No image');
                    } else {
                        var img = $("<img>");
                        img.attr("src", "/image.jpg?id="+data.stream.cover_image+"&thumb=256x160");
                        $("#background-picture-show").html(img);
                    }
                }, function () {
                    $('#stream-form').loading();
                }, function (data) {
                    if (!data.error) {
                        var img = $("<img>");
                        img.attr("src", data.data);
                        $("#background-picture-show").html(img);
//                            $('#radio-content input[name="background-picture"]').remove();
//                            var input = $("<input>");
//                            input.attr("type", "hidden");
//                            input.attr("name", "background-picture");
//                            input.attr("value", data.image_id);
//                            $('#stream-form').append(input);
                        $('#stream-form').loading_stop();
                    }
                }, false, true);


                $('input[name="stream-public"]').click(function() {
                    if ($(this).val() == "1") {
                        $('input[name="stream-password"]').parent().hide();
                    } else {
                        $('input[name="stream-password"]').parent().show();
                    }
                });

                $('#stream-form').submit(function() {

                    $('.main').loading_center();
                    $.ajax({
                        type: 'POST',
                        url: "/stream/about.json",
                        data: $('#stream-form').serialize()+"&stream_id="+$('#stream').data('id'),
                        success: function (data) {

                            $('.top-right').notify({
                                type: 'success',
                                message: { text: "Successfully saved" },
                                fadeOut: { enabled: true, delay: 5000 }
                            }).show();

                            $('.main').loading_stop();
                        }
                    });
                    return false;
                });

                frameView.fill();

            });

            $('.main').loading_stop();
        };

    });
});