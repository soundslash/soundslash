define('router', ['router-lib'], function (router) {

    router
        .registerRoutes({
            main: { path: '/',              moduleId: 'controller/Radio' },
            listen: { path: '/listen.html', moduleId: 'controller/Listen' },
            radio: { path: '/radio.html',   moduleId: 'controller/Radio' },
            user: { path:   '/user.html',    moduleId: 'controller/User' },
            stream: { path: '/stream.html',    moduleId: 'controller/Stream' }
        });

    return router;

});