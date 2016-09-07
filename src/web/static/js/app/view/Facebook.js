define(function (require) {
    "use strict";

    var user = require('model/User'),
        radioView = require('view/Radio')
        ;

    return extend.View('singleton', function () {

        this.connect = function () {

            $.ajaxSetup({ cache: true });
            $.getScript('//connect.facebook.net/en_UK/all.js', function(){

                if (window.location.port == "") {
                    var url = '//'+window.location.hostname+'/channel.html';
                } else {
                    var url = '//'+window.location.hostname+':'+window.location.port+'/channel.html';
                }

                FB.init({
                    appId: '486579808100437',
                    channelUrl: url,
                    status     : true, // check login status
                    cookie     : true, // enable cookies to allow the server to access the session
                    xfbml      : true  // parse XFBML
                });

                FB.Event.subscribe('auth.authResponseChange', function(response) {
                    if (response.status === 'connected') {
                        if (user._user === false) {
                            user.fblogin(response).done(function (data) {
                                if (!data.error) {

                                    user._user = data.user_id;

                                    if (window.dropped === true) {
                                        radioView.on_signup();
                                    }
                                }
                            });
                        }

                    } else if (response.status === 'not_authorized') {

                    } else {

                    }
                });

            });

            // Here we run a very simple test of the Graph API after login is successful.
            // This testAPI() function is only called in those cases.
//    function testAPI() {
//        console.log('Welcome!  Fetching your information.... ');
//        FB.api('/me', function(response) {
//            console.log('Good to see you, ' + response.name + '.');
//        });
//    }

        }

    });
});