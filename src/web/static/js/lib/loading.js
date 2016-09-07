
jQuery.fn.is_loading = function () {
    if (this.find(".loading-bg").length != 0) {
        return true;
    } else {
        return false;
    }
}


jQuery.fn.loading = function () {
    this.css("position", "relative");
    var loading = $("<div>");
    loading.attr("class", "loading-bg");

    var text = $("<div>");
//    var text_height = 20;
//    var text_width = 50;
    var text_height = 0;
    var text_width = 0;
    text.attr("class", "loading-info");
    text.css("top", this.height()/2-text_height/2 + "px");
    text.css("left", this.width()/2-text_width/2 + "px");
    text.html('<img src="/static/img/ajax-loader2.gif">');


    this.append(loading);
    this.append(text);
    return this;
}

jQuery.fn.loading_center = function () {
    this.css("position", "relative");
    var loading = $("<div>");
    loading.attr("class", "loading-bg");

    var text = $("<div>");
//    var text_height = 20;
//    var text_width = 50;
    var text_height = 0;
    var text_width = 0;
    text.attr("class", "loading-info");
    var ho = ($('#toolbar').height()+$('#top-menu').height()+parseInt($('.main').css("margin-top").replace("px", "")));
    text.css("top",  $('#content').scrollTop()+($(window).height()/2)-ho-16 + "px");
    text.css("left", this.width()/2 + "px");
    text.html('<img src="/static/img/ajax-loader2.gif">');


    this.append(loading);
    this.append(text);
    return this;
}


jQuery.fn.loading_stop = function () {
    this.find(".loading-bg").hide();
    this.find(".loading-bg").remove();
    this.find(".loading-info").hide();
    return this;
}