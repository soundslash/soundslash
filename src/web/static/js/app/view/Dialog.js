define(function (require) {
    "use strict";

    var frameView = require('view/Frame');

    return extend.View('singleton', function () {

        this.show = function(title, html, beforeClose) {

            if (beforeClose === undefined)
                beforeClose = function (dialog) {
                    return true;
                };
            var dialog = $('<div class="dialog"></div>');
            dialog.html('<div class="close"></div><div class="title"></div><div class="content"></div>');
            dialog.find('.title').html(title);
            dialog.find('.content').html(html);
            if ($('#top-menu').css('position') == "fixed") {
                dialog.css('top', $('#content').scrollTop()-$('#toolbar').height()+20);
            } else {
                dialog.css('top', 20);
            }
            var loading = $("<div>").attr("class", "loading-bg").hide();
            $('.main').append(loading);
            loading.fadeIn(500);
            var loading = $("<div>").attr("class", "loading-bg").hide();
            $('.footer').append(loading);
            loading.fadeIn(500, function () {

                frameView.fill();
            });

            dialog.hide();
            dialog.appendTo('.main').fadeIn(500);
            dialog.find('.close').click(function () {
                var res = beforeClose(dialog);
                if (res === false) return;
                dialog.remove();
                $('.main .loading-bg').remove();
                $('.footer .loading-bg').remove();
                frameView.fill();
            });

        };



    });
});