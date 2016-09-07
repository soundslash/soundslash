
jQuery.fn.colorinput = function (inputName, defaultColor, availColors, beforeAll, onStart, onEnd) {

    beforeAll();
    var that = this;

    $('<input type="hidden" name="'+inputName+'" value="'+defaultColor+'">').appendTo(this);

    $(document).on('mousedown.color-input, touchend.color-input', function (e) {
        // This condition was inspired by bootstrap-datepicker.
        // The element the timepicker is invoked on is the input but it has a sibling for addon/button.
        if (!(that.find(e.target).length)) {
            that.find('.color-choose').remove();
        }
    });

    function update() {
        var color = that.find('input[name="'+inputName+'"]').val();
        console.log(color);
        that.find('.current').css('background', color);
    }
    function showDialog() {
        if (that.find('.color-choose').length >= 1) return;
        var dialog = $('<div class="color-choose bootstrap-timepicker-widget dropdown-menu timepicker-orient-left timepicker-orient-top open" style="z-index:100">');

        dialog.css('top', '32px');
        dialog.css('left', '0px');
        that.append(dialog);
        var cols = [];
        for (var i in availColors) {
            var col = $('<div class="color-item" data-color="'+availColors[i]+'" style="background:'+availColors[i]+'"></div>');
            col.click(function () {
                that.find('input[name="'+inputName+'"]').val($(this).data('color'));
                update();
                that.find('.color-choose').remove();
            });
            cols.push(col);
            var j = i;
            if ((j%2)===1) {
                var new_col = $('<div>');
                new_col.append(cols);
                that.find('.color-choose').append(new_col);
                cols = [];
            }
        }
    }

    update();

    this.find('.add-on').click(function () {
        showDialog();
    });

    return this;
}