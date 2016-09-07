define(function (require) {
    "use strict";

    return extend.View(function () {

        this.template = 'listen';
        this.append = '#content .main';

        this.initialize = function () {

            $('#top-menu .icon').removeClass('active');
            $('#top-menu .icon.headphones').addClass('active');
        };

        this.events = function () {


            $("input#search-listen").keyup(function(e) {
                clearTimeout($.data(this, 'timer'));
                var search_string = $(this).val();
                $(this).data('timer', setTimeout(function() {
                    $('.lightblue-menu a[href="#popular"]').tab('show');

                    url('/listen.html', {
                        'action': 'popular',
                        'search_string': search_string,
                        'page': 1
                    });

                }, 200));
            });
        };
    });

});
