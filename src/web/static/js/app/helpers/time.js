
window.format_seconds = function (seconds, h) {
    var hours = Math.floor(seconds / 60 / 60 % 60);
    var minutes = Math.floor(seconds / 60 % 60);
    var seconds = Math.ceil(seconds % 60);
    if (minutes <= 9) minutes = "0"+minutes;
    if (seconds <= 9) seconds = "0"+seconds;
    if (h) {
        return hours + ":" + minutes + ":" + seconds;
    } else {
        return minutes + ":" + seconds;
    }
};

window.format_epoch = function (seconds) {
    var d = new Date(seconds*1000);
    var hours = d.getHours();
    var minutes = d.getMinutes();
    var seconds = d.getSeconds();
    if (hours <= 9) hours = "0"+hours;
    if (minutes <= 9) minutes = "0"+minutes;
    if (seconds <= 9) seconds = "0"+seconds;
    return hours + ":" + minutes + ":" + seconds;
};

