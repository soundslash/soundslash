define(function (require) {
    "use strict";

    var frameView = require('view/Frame');

    return extend.View(function () {

        this.template = 'stream-list';
        this.append = '#popular';

        this.afterRenderCb = [
            function () {
                frameView.fill();
            }];

        this.loadMore = function (data) {
            this.replace = false;
            this.$el = $('<div/>');
            this.append += ' > div > div.row:first';
            this.render(data);
            return this;
        };

        this.events = function () {
            $('.lightblue-menu a').removeClass('active');
            $('.lightblue-menu a[href="#popular"]').addClass('active');
            $('.lightblue-menu a[href="#popular"]').tab('show');

            $('#popular .show-more').click(function () {
                $(this).closest('.row').remove();
                url('/listen.html', $.extend(url.get()['args'], { page: parseInt($(this).data('page'))+1 }));
            });
        };

    });
});
