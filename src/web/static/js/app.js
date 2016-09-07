
define([], function() {
    'use strict';

    var version = (new Date()).getTime();
    if (window.location.host == "www.soundslash.com" || window.location.host == "dev.soundslash.com") {
        version = "0.2";
    }

    requirejs.config({
        baseUrl: '/static/js',
        // change to v.1.0...
        urlArgs: "v=" +  version,
        map: {
            '*': {
                'adapters/product': 'app/adapters/product-memory',
//                'styles': 'css'
            }
        },
        paths: {
            model: ['app/model'],
            view: ['app/view'],
            controller: ['app/controller'],

            tmpl: ['lib/tmpl.min'],
            tmpls: ['lib/tmpls.min'],
            'router-lib': ['lib/router.min'],
            css: ['lib/css.min'],
            text: ['lib/text'],
            fastclick: ['lib/fastclick'],

            jquery: ['lib/jquery-1.10.1.min'],
            bootstrap: ['lib/bootstrap.min'],
            'bootstrap-slider': ['lib/bootstrap-slider'],
            'bootstrap-notify': ['lib/bootstrap-notify'],
            snap: ['lib/snap'],
            'jquery-scrolltofixed': ['lib/jquery-scrolltofixed']
        }
    });

    /*
     Base deps
     */
    require([
        'jquery',
        'lib/object-watch',
        'mvc',

        'fastclick',
        'tmpls',
    ], function ($, ow, mvc, fastclick, _) {
        'use strict';

        require([
            'router', 'controller/Controller'], function (router) {

            /*
             Route app
             */
            router
                .on('routeload', function(Controller, args) {
                    var actionName,
                        controller = new Controller();

                    if (args.action === undefined) {
                        actionName = "index";
                    } else {
                        actionName = args.action;
                    }

                    controller.load(actionName, args);

                }).init();

        });

        $(function () {
            fastclick.attach(document.body);
        });


    });

});