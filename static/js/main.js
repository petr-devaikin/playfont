function parseUrl(val) {
    result = {};
    location.search.substr(1).split("&").forEach(function (item) {
        tmp = item.split("=");
        result[tmp[0]] = decodeURIComponent(tmp[1]);
    });
    return result;
}

$(document).ready(function() {
    var body = $('#content-frame').contents().find('body');
    $("a", body).css("color", "red");
});