
jQuery.fn.ajaxinput = function (inputName, action, beforeAll, onStart, onEnd, multiple, imagesOnly) {

    if (typeof multiple === 'undefined')
        multiple = true;

    if (typeof imagesOnly === 'undefined')
        imagesOnly = true;

    beforeAll();

    var that = this;

    this.on('change', function() {

        console.log('File changed');

        var id = new Date().getTime();

        onStart();

        var iframe = $("<iframe>");
        iframe.attr("style", "display:none;visibility:hidden;");
//            iframe.attr("style", "width:800px;height:300px;border: 3px solid green");
        iframe.attr("id", id+"-target");
        iframe.attr("name", id+"-target");
        iframe.attr("src", "#");
        $("body").append(iframe);

        $('#'+id+'-target').load(function() {
            var result = $.parseJSON($("#"+id+"-target").contents().text());
//            var result = {};
            $('#'+id+'-target').remove();
            onEnd(result);
        });

        var xsrf = $("<input>");
        xsrf.attr("name", "_xsrf");
        xsrf.attr("value", $('form > input[name="_xsrf"]').val());

        var form = $("<form>");
        form.attr("style", "display:none;visibility:hidden;");
        form.attr("action", action);
        form.attr("method", "POST");
        form.attr("enctype", "multipart/form-data");
        form.attr("target", id+"-target");

        var hidden = $("<input>");
        hidden.attr("type", "hidden");
        hidden.attr("name", "filename");
        hidden.attr("value", inputName);

        var input = that.find("input");
        console.log(input);
        form.append(hidden);
        form.append(xsrf);
        form.append(input);
        $("body").append(form);
        form.submit();

        newInput();
    });

    function newInput() {
        console.log('Creating new input');

        var newInput = $("<input>");
        newInput.attr("type", "file");
        newInput.attr("id", inputName);

        if (multiple) {
            newInput.attr("name", inputName + '[]');
            newInput.attr("multiple", "multiple");
        } else {
            newInput.attr("name", inputName);
        }
        that.html(newInput);
        $(".bootstrap-filestyle", $(that)).remove();
        var button_text = (multiple) ? ((imagesOnly) ? 'Choose pictures' : 'Choose files')
            : ((imagesOnly) ? 'Choose picture' : 'Choose file');
        newInput.filestyle({input: false, classButton: "upload", buttonText: button_text} );
    }
    newInput();

    return this;
}
