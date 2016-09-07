define(function (require) {
    "use strict";

    /*
    This is unused.
     */
    return extend.View('singleton', function () {

        this.template = 'roller';
        this.append = '#content';
        this.replace = false;

        this.events = function () {

            var _this = this;
            this.roller = $('.roller');

            $('#open-left').click(function () {
                if (_this.roller.is(':hidden')) {

                    _this.roller.css('z-index', 1001);

                    var that = this;
                    _this.roller.find('.bottom-roll-up').click(function () {
                        that.click();
                    });

                    _this.roller.find('> div').css( 'overflow', 'hidden');
                    _this.roller.find('> div').css( 'height', '0px');
                    _this.roller.find('> div').css( 'transition', 'height 1s');

                    _this.roller.show();

                    _this.roller.find('> div').css( 'height', $(window).height()-($('#toolbar').height()-50)+'px');
                    var show = setInterval(function () {
                        clearInterval(show);

                        if (_this.roller.find('> div').height() != 0) {
                            _this.roller.find('> div').css( 'height', 'auto');
                            _this.roller.find('> div').css( 'height', _this.roller.find('> div').height()+'px');
                        }
                    }, 1000);

                } else {

                    _this.roller.find('> div').css( 'overflow', 'hidden');
                    _this.roller.find('> div').css( 'height', '0px');

                    var hide = setInterval(function () {
                        clearInterval(hide);
                        if (!_this.roller.is(':hidden'))
                            _this.roller.hide();
                    }, 1000);

                }
            });
        };

    });
});