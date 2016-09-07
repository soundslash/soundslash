define(function (require) {
    "use strict";

    var user = require('model/User'),
        Stream = require('model/Stream'),
        frameView = require('view/Frame'),
        _ = require('lib/chosen.jquery.min'),
        _ = require('lib/objectid'),
        _ = require('lib/jquery.ui.widget'),
        _ = require('lib/jquery.iframe-transport'),
        _ = require('lib/jquery.fileupload'),
        _ = require('lib/jquery.fileupload-process'),
        _ = require('lib/jquery.fileupload-ui'),
        _ = require('lib/binaryajax'),
        _ = require('lib/id3');



    return extend.View('singleton', function () {

        this.template = 'radio';
        this.append = '.main';

        this.afterRenderCb = [
            function () {
                frameView.fill();
            }];

        var _this = this;

        this.initialize = function () {

            $('#top-menu .icon').removeClass('active');
            $('#top-menu .icon.microphone').addClass('active');

            this._snapper(user._user);
        };

        this.events = function () {

            this.fileupload(true);

            $('.lightblue-menu a[href="#stream-menu"]').click(function () {

                if (this.hasClass('active')) {
                    this.removeClass('active');
                    $('.lightblue-menu .tab-pane.active').hide();
                } else {
                    $('.lightblue-menu a[href="#list-streams"]').removeClass('active');
                    this.addClass('active');
                    $('#stream-menu').show();
                    $('#list-streams').hide();
                }

            });


            $('#sign-up').submit(function() {

                $('#sign-up').loading();

                user.signup($('#sign-up').serialize()).done(function (data) {

                    if (data.error)
                    {
                        $('.top-right').notify({
                            type: 'danger',
                            message: { text: data.msg },
                            fadeOut: { enabled: true, delay: 5000 }
                        }).show();
                    }
                    else
                    {
                        window.logged_in = data.user;

                        $('.top-right').notify({
                            type: 'success',
                            message: { text: "Successfully signed up" },
                            fadeOut: { enabled: true, delay: 5000 }
                        }).show();


                        _this.on_signup();

                    }
                    $('#sign-up').loading_stop();

                });

                return false;
            });

            user.userChanged.attach(function (sender, user) {
                _this._snapper(user['val']);
            });


        };

        this._snapper = function (user) {
            if (user) {
                var snapper = new Snap({
                    element: document.getElementById('content'),
                    'disable': 'left'
                });
                window.snapper = snapper;
            } else {
                if (window.snapper)
                    window.snapper.close();
            }
        };

        this.on_signup = function () {

            $(".upload-button").fadeIn("slow");
            $("#sign-up").hide();

        };

        this.fileupload = function (create) {

            var _this = this;

            if (create === undefined) {
                create = false;
            } else {
                create = true;
            }

            $("#upload_link").on('click', function (e) {
                e.preventDefault();
                $("#upload:hidden").trigger('click');
            });

            // Change this to the location of your server-side upload handler:
            var url = '/upload.json';
            var streamInfo = false;
            $('#fileupload').fileupload({
                url: url,
                dataType: 'json',
                limitConcurrentUploads: 1,
                sequentialUploads: true,
                autoUpload: false,
                //        uploadTemplateId: 'template-upload',
                uploadTemplateId: null,
                downloadTemplateId: null,
                uploadTemplate: function (o) {
                    console.log('adding ' + objectId(o.files[0]));
                    o.fileId = objectId(o.files[0]);
                    if (o.files[0].type.match("^audio/"))
                        o.audio = true;
                    else
                        o.audio = false;

                    var v = new View();
                    v.template = 'upload';
                    var el = $('<div class="upl"/>').hide();
                    $('body').append(el);
                    v.append = 'body > .upl';
                    v.render(o);
                    var html = $('body > .upl').show().html();
                    $('body > .upl').remove();
                    return html;

                },
                done: function (e, data) {
                    $.each(data.result.files, function (index, file) {
                        if (file.error) {
                            $(".success").hide();
                            $(".error").append('<div class="alert alert-danger">' + file.error + '</div>');
                            $(".error").show();
                        }
                    });
                },
                progressall: function (e, data) {
                    var progress = parseInt(data.loaded / data.total * 100, 10);
                    $('.progress .progress-bar').css(
                        'width',
                            progress + '%'
                    );
                    $('.progress .progress-bar').attr('aria-valuenow', progress);
                    $('.progress-create .percent').html(progress);

                    if (progress == 100) {

                        var snapper = new Snap({
                            element: document.getElementById('content'),
                            'disable': 'left'
                        });
                        window.snapper = snapper;

                        $('.top-right').notify({
                            type: 'success',
                            message: { text: 'Your media has been successfully uploaded' },
                            fadeOut: { enabled: true, delay: 2500 }
                        }).show();
                        $('.top-right').notify({
                            type: 'success',
                            message: { text: 'Wait for stream to start' },
                            fadeOut: { enabled: true, delay: 5000 }
                        }).show();

                        $('.progress-create > label').html('<img src="/static/img/ajax-loader2.gif"> Processing your media track ...');
                        $('.progress-create .progress').hide();

                        frameView.fill();
                    }

                }
            });
            $('#fileupload').bind('fileuploadsend', function (e, data) {


            });
            $('#fileupload').bind('fileuploadadd', function (e, data) {

                var proceed = false;
                var ftype, fname;
                for (var i = 0, file; file = data.files[i]; i++) {
                    if (file.type.match("^audio/")) {
                        proceed = true;
                    } else {
                        ftype = file.type;
                        if (ftype == "") ftype = "unknown mime";
                        fname = file.name;
                    }
                }
                if (!proceed) {

                    $('.top-right').notify({
                        type: 'danger',
                        message: { text: 'Unsupported file ' + fname + ' (' + ftype + ')' },
                        fadeOut: { enabled: true, delay: 5000 }
                    }).show();
                    return;
                }
                // first time and login do not exists
                if (!streamInfo && window.logged_in != false) {
                    streamInfo = true;
                    window.dropped = true;
                    if (create) {
                        _this.displaydrop();
                    }
                }
                else if (!streamInfo) {
                    streamInfo = true;
                    window.dropped = true;
                    _this.displaydrop();
                }


                $('#fileupload-more').show();
                $('#create').show();


                frameView.fill();

                // this is an event that sends data when click to the button occurs
                $('#fileupload-submit button').on("click",function(){
                    data.submit();
                });

                function callback(tags, file, fileId) {
                    $('#filetag' + fileId + ' input[name="artist[]"]').val(tags.artist);
                    $('#filetag' + fileId + ' input[name="title[]"]').val(tags.title);
                }

                ID3.readTagsFromFile(data.files[0], objectId(data.files[0]), callback);

            });
            $('#fileupload').bind('fileuploadsubmit', function (e, data) {

                $("#fileupload").hide();
                $(".progress-create").show();

                var fileId = objectId(data.files[0]);
                var titleObj = $('#filetag' + fileId).find('input[name="title[]"]');
                var title = titleObj.val();
                titleObj.prop('disabled', true);

                var artistObj = $('#filetag' + fileId).find('input[name="artist[]"]');
                var artist = artistObj.val();
                artistObj.prop('disabled', true);


                var streamName = $('input[name=stream-name]').val();
                var streamGenre = [];
                $('select[name=stream-genre] :selected').each(function (i, selected) {
                    streamGenre[i] = $(selected).val();
                });
                var streamCoverImage = $('select[name=stream-cover-image] option:selected').val();
                var streamPublic = $('input[name=stream-public]:checked').val();
                var streamPassword = $('input[name=stream-password]').val();
                var streamDescription = $('textarea[name=stream-description]').val();

                var streamCreate = $('input[name=create]').val();

                console.log("uploading " + fileId);


                if (window.start_upload) {
                    window.start_upload = false;
                    var formData = {
                        streamName: streamName,
                        streamGenre: streamGenre,
                        streamCoverImage: streamCoverImage,
                        streamPublic: streamPublic,
                        streamPassword: streamPassword,
                        streamDescription: streamDescription,
                        streamCreate: streamCreate
                    };
                }
                else {
                    var formData = {};
                }

                formData["streamId"] = $('input[name="stream-id"]').val();
                formData["groupId"] = $('input[name="group-id"]').val();
                formData["fileId"] = fileId;
                formData["title"] = title;
                formData["artist"] = artist;
                formData["_xsrf"] = $('#fileupload > input[name="_xsrf"]').val();

                data.formData = formData;

                frameView.fill();

            });


        };

        this.displaydrop = function () {

            $('.start-box').hide();

            $('#fileupload').show();


            var v = new View();
            v.template = 'stream-info';
            v.append = '#stream-info';
            v.render({"genres": window.genres});


            var stream = new Stream();
            stream.getGenresHtml().done(function (data) {

                $(".stream-genre").append(data);

                $("#stream-info .chosen-select").chosen({
                    no_results_text: "Oops, nothing found!",
                    width: "100%"
                });
            });



            window.start_upload = true;

            $('input[name="stream-public"]').click(function () {
                if ($(this).val() == "1") {
                    $('input[name="stream-password"]').parent().hide();
                } else {
                    $('input[name="stream-password"]').parent().show();
                }
            });


            frameView.mode1_2();


            $('#validator').click(function () {

                $.ajax({
                    type: 'POST',
                    url: "/validate.json",
                    data: {
                        'stream-terms1': $("input[name='stream-terms1']").is(':checked'),
                        'stream-terms2': $("input[name='stream-terms2']").is(':checked')
                    },
                    success: function (data) {

                        if (!data.error) {
                            $.ajax({
                                type: 'POST',
                                url: "/create.json",
                                success: function (data) {
                                    if (data.error) {
                                        $(".success").hide();
                                        $(".error").append('<div class="alert alert-danger">' + data.error + '</div>');
                                        $(".error").show();
                                        $(".upload-button").hide();

                                    } else {

                                        $('input[name="stream-id"]').val(data.streamId);
                                        $('input[name="group-id"]').val(data.groupId);
                                        $('input[name="group-fav-id"]').val(data.groupFavId);


                                        var intervalId =
                                            setInterval(function () {
                                                $.ajax({
                                                    type: 'POST',
                                                    url: "/status.json",
                                                    data: {
                                                        streamId: $('input[name="stream-id"]').val()
                                                    },
                                                    success: function (data) {
                                                        if (data.status == "ready") {
                                                            clearInterval(intervalId);

                                                            url('/stream.html', {action: 'live', autoplay: true});

                                                        }
                                                        if ($('input[name="stream-id"]').length === 0) clearInterval(intervalId);
                                                    },
                                                    error: function () {
                                                        if ($('input[name="stream-id"]').length === 0) clearInterval(intervalId);
                                                    }
                                                });
                                                if ($('input[name="stream-id"]').length === 0) clearInterval(intervalId);
                                            }, 4000);

                                        $('#fileupload-submit button').click();
                                    }

                                }
                            });
                        } else {

                            $('.top-right').notify({
                                type: 'danger',
                                message: { text: data.error },
                                fadeOut: { enabled: true, delay: 5000 }
                            }).show();
                        }
                    }
                });


            });
        }

    });


});