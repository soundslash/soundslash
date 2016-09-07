define(function (require) {
    "use strict";

    var frameView = require('view/Frame');

    return extend.View(function () {

        this.template = 'stream-list';
        this.append = '#genre';


        this.afterRenderCb = [
            function () {
                frameView.fill();
            }];

        this.events = function () {
            $('.lightblue-menu a').removeClass('active');
            $('.lightblue-menu a[href="#genre"]').addClass('active');
            $('.lightblue-menu a[href="#genre"]').tab('show');

            $('#genre .show-more').click(function () {
                $(this).closest('.row').remove();
                url('/listen.html', $.extend(url.get()['args'], { page: parseInt($(this).data('page'))+1 }));
            });
        };

    });
});
