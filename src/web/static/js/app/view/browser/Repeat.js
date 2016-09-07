define(function (require) {
    "use strict";

    var user = require('model/User'),
        frameView = require('view/Frame'),
        Buffer = require('view/Buffer'),
        dialog = require('view/Dialog'),
        Stream = require('model/Stream');

    return extend.View(function () {

        this.databaseRepeats = function(a, repeats) {
            var _this = this;

            $('.db-menu a.active').removeClass('active');
            $(a).addClass('active');
            $(a).tab('show');
            this.repeats(repeats);
            frameView.fill();
            return false;
        };
        this.repeats = function(repeats) {
            if (repeats == 'init') {
                $('#group').hide();
                this.selectedRepeats($('.program-repeats .navigation'), repeats);
                return;
            }
            // if any repeats exists by default e.g. editing program
            if (repeats !== undefined) {
                if (repeats) {
                    $('#selected-repeats').hide();
                    this.selectedRepeats($('.program-repeats .navigation'), repeats);
                } else {
                    $('#group').hide();
                    this.selectedRepeats($('.program-repeats .navigation'), repeats);
                }
            }
            if (repeats === undefined && $('#selected-repeats tr').length == 0 && $('#group tr').length == 0) {
                $('#group').hide();
                this.selectedRepeats($('.program-repeats .navigation'), repeats);
            }
        };
        this.selectedRepeats = function(a, repeats) {
            if ($('#selected-repeats').is(":hidden")) {
                $(a).find('span').html("MEDIA");
                $('#group').hide();
                $('#groupsearch-form').hide();
                $('#database > p').hide();
                $('#selected-repeats').show();

                if ($('#selected-repeats tr').length == 0) {
                    this.updateRepeats(repeats);
                }
            } else {

                $(a).closest('.navigation').find('span').html("YOUR SELECTED REPEATS");
                $('#group').show();
                $('#groupsearch-form').show();
                $('#database > p').show();
                $('#selected-repeats').hide();

                if ($('#group tr').length == 0) {
                    this.update_group();
                }
            }
            frameView.fill();
            return false;
        };
        this.updateRepeats = function (repeats) {

            var v = new View(), _this = this;
            v.wrap_el = false;
            v.template = 'stream-program-selected';
            v.append = '#selected-repeats .selected-repeats-body';
            v.afterRender(function () {

                $('#selected-repeats .repeats select.repeating').chosen({
                    disable_search_threshold: 99999,
                    width: "100%"
                });
                $('#selected-repeats .repeats select.repeating').change(function() {

                    if (!window.selected_repeats) {
                        window.selected_repeats = [];
                    }
                    var id = $(this).closest('tr').attr('id');
                    for (var i in window.selected_repeats) {
                        console.log(window.selected_repeats[i]['id']+"===="+id);
                        if (window.selected_repeats[i]['id'] == id) {
                            window.selected_repeats[i]['repeating'] = $(this).closest('tr').find('select.repeating').val();
                        }
                    }
                    _this.updateRepeats(window.selected_repeats);
                    _this.update_group();
                });

                $('.format-duration').each(function (index) {
                    $(this).html(format_seconds($(this).data('duration') / 1000000000));
                });
                frameView.fill();
            });
            v.render({
                "repeats": repeats,
                "show_repeats": true
            });


        };


    });
});
