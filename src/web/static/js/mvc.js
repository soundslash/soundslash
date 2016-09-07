define(function (require) {
    "use strict";

    var tmpl = require('tmpl');
    var tmpls = require('tmpls');

    window.Model = function () {
        'use strict';

        this.ajax = function (settings) {
            if (settings.cache) {

                var cache = settings.cache;
                delete settings.cache;

                var settingsSerialized = JSON.stringify(settings);
                var cacheObj = JSON.parse(localStorage.getItem(settingsSerialized));
                if (cacheObj) {
                    if ((new Date()).getTime() - cacheObj._cache_start < cache * 1000) {
                        cacheObj.done = function (f) {
                            f(cacheObj.data);
                        };
                        return cacheObj;
                    } else {
                        localStorage.removeItem(settingsSerialized);
                    }
                }

                var ajax = $.ajax(settings);
                ajax.done(function (data) {
                    var new_data = {
                        data: data,
                        _cache_start: (new Date()).getTime()
                    };
                    localStorage.setItem(settingsSerialized, JSON.stringify(new_data));
                });
                return ajax;

            } else {
                return $.ajax(settings);
            }
        };

    };


    window.View = function () {
        'use strict';

        this.$el = $('<div></div>');
        this.wrap_el = true;
        this.beforeRenderCb = [];
        this.tmpl = tmpl;
        this.tmpls = tmpls;
        // use compiled templates, please run compile_tpl.sh
        this.tmpl_js = true;

        this.replace = true;

        this.rendered = false;
        this.loadingTarget = '.main';

        this.initialize = function () {

        };
        this.events = function () {

        };
        this._events = function (f) {

        };

        this.beforeRender = function (f) {
            this.beforeRenderCb.push(f);
        };
        this.afterRender = function (f) {
            if (typeof this.afterRenderCb === "undefined") {
                this.afterRenderCb = [];
            }
            this.afterRenderCb.push(f);
            if (this.rendered === true) {
                this.do_afterRender();
            }
        };

        this.render = function (args, html) {
            var obj_args = this.args, _this = this;

            $(_this.loadingTarget).loading();

            if (this.beforeRenderCb.length >= 1) {
                for (var cb in this.beforeRenderCb) {
                    this.beforeRenderCb[cb](args, html);
                }
            }

            // use compiled templates
            if (this.tmpl_js) {

                var template = this.tmpls(this.template, $.extend({}, obj_args, args));

                if (this.$el)
                    this.$el.attr('data-view', _this.template);

                if (!(typeof _this.append === 'undefined')) {
                    if (_this.replace) {
                        if (this.wrap_el)
                            _this.$el.html(template);
                        else
                            _this.$el = template;
                        $(_this.append).html(_this.$el);
                    } else {
                        if (this.wrap_el)
                            _this.$el.html(template);
                        else
                            _this.$el = template;
                        $(_this.append).append(_this.$el);
                    }
                }

                _this.do_afterRender();

            } else {


                if (html === undefined) {

                    require(['tmpl', "text!tpl/"+this.template+".html"], function (tmpl, template) {

//                        var s = (new Date()).getTime();
                        var func = _this.tmpl(template);
//                        console.log('Rendering took ', (new Date()).getTime()-s);
                        var template = func($.extend({}, obj_args, args));

                        if (_this.wrap_el)
                            _this.$el.attr('data-view', _this.template);

                        if (!(typeof _this.append === 'undefined')) {
                            if (_this.replace) {
                                if (this.wrap_el)
                                    _this.$el.html(template);
                                else
                                    _this.$el = template;
                                $(_this.append).html(_this.$el);
                            } else {
                                if (this.wrap_el)
                                    _this.$el.html(template);
                                else
                                    _this.$el = template;
                                $(_this.append).append(_this.$el);
                            }
                        }

                        _this.do_afterRender();

                    });

                } else {

                    var func = _this.tmpl(html);
                    var template = func($.extend({}, obj_args, args));

                    if (this.wrap_el)
                        _this.$el.attr('data-view', '?');

                    if (!(typeof _this.append === 'undefined')) {
                        if (_this.replace) {
                            if (this.wrap_el)
                                _this.$el.html(template);
                            else
                                _this.$el = template;
                            $(_this.append).html(_this.$el);
                        } else {
                            if (this.wrap_el)
                                _this.$el.html(template);
                            else
                                _this.$el = template;
                            $(_this.append).append(_this.$el);
                        }
                    }

                    _this.do_afterRender();

                }

            }
            return this;

        };

        this.do_afterRender = function (args, html) {

            if ((typeof this.afterRenderCb !== "undefined") && this.afterRenderCb.length >= 1) {
                for (var cb in this.afterRenderCb) {
                    this.afterRenderCb[cb](args, html);
                }
            }

            this.initialize();
            this._events();
            this.events();

            $(this.loadingTarget).loading_stop();

            this.rendered = true;
        };

        this.remove = function () {
            this.$el.remove();
        };

    };


    window.Controller = function () {
        'use strict';

        this.actionRequire = {};

        this.load = function (action, args) {

            var _this = this;
            _this.requireRendered = [];

            if ((!(typeof _this.actionRequire[action] === 'undefined')) ||
                (!(typeof _this.actionRequire['*'] === 'undefined'))) {

                var requires = [], actionFullName;

                if (!(typeof _this.actionRequire[action] === 'undefined')) {
                    requires = requires.concat(_this.actionRequire[action]);
                }
                if (!(typeof _this.actionRequire['*'] === 'undefined')) {
                    requires = requires.concat(_this.actionRequire['*']);
                }
                for (var i in requires) {

                    actionFullName = "action" + requires[i]['action'].charAt(0).toUpperCase() + requires[i]['action'].slice(1);
                    this[actionFullName].nextCb = requires[parseInt(i)+parseInt(1)];
                    this[actionFullName].done = function () {
                        if (this.nextCb) {
                            var afn = "action" + this.nextCb['action'].charAt(0).toUpperCase() + this.nextCb['action'].slice(1);

                            if (this.nextCb.isRendered()) {
//                                console.log(afn, 'skipped');
                                _this[afn].done();
                            } else {
//                                console.log(afn);
                                _this[afn](args);
                            }
                        } else {
                            var af = "action" + action.charAt(0).toUpperCase() + action.slice(1);
//                            console.log('FINAL', af);
                            _this[af](args);
                        }
                    };
                }

                var firstActionFullName = "action" + requires[0]['action'].charAt(0).toUpperCase() + requires[0]['action'].slice(1);
                if (requires[0].isRendered()) {
//                    console.log(firstActionFullName, 'skipped');
                    this[firstActionFullName].done();
                } else {
//                    console.log(firstActionFullName, 'render');
                    this[firstActionFullName](args);
                }

//                for (var i in requires) {
//
//                    actionFullName = "action" + requires[i]['action'].charAt(0).toUpperCase() + requires[i]['action'].slice(1);
//
//                    _this[actionFullName].i = i;
//                    _this[actionFullName].done = function () {
//
//                        var next = false, my_i = this.i;
//
//                        if (!my_i) my_i = requires.length-1;
//                        console.log('CURRENT', my_i);
//
////                        _this.doneLoading(requires[my_i]['action'], action, args);
//                        _this.requireRendered.push(requires[my_i]['action']);
//                        if (_this.requireRendered.length === requires.length) {
//                            console.log('RUN FINAL ACTION');
//                            var af = "action" + action.charAt(0).toUpperCase() + action.slice(1);
//                            _this[af](args);
//                            _this.requireRendered = [];
//                        } else {
//
//                            if (requires.length > parseInt(my_i)+parseInt(1))
//                                next = requires[parseInt(my_i)+parseInt(1)];
//
//                            if (next) {
//
//                                var afn = "action" + next['action'].charAt(0).toUpperCase() + next['action'].slice(1);
//
//                                if (!(typeof next.isRendered === 'undefined')) {
//                                    if (next.isRendered()) {
//                                        console.log('Skip loading prerequisites ', next['action']);
//                                        _this[afn].done();
//                                    } else {
//                                        _this[afn](args);
//                                    }
//                                } else {
//
//                                    _this[afn](args);
//                                }
//
//                            }
//                        }
//
//                    };

                    // fire!
//                    if (parseInt(i) === 0) {
//                        _this[actionFullName](args);
//                    }
//                }

//                actionFullName = "action" + requires[0]['action'].charAt(0).toUpperCase() + requires[0]['action'].slice(1);
//
//                if (!(typeof requires[0].isRendered === 'undefined')) {
//                    if (requires[0].isRendered()) {
//                        console.log('Skip loading prerequisites ', requires[0]['action']);
//                        _this[actionFullName].done();
//                    } else {
//
//                        _this[actionFullName](args);
//                    }
//                } else {
//
//                    _this[actionFullName](args);
//                }

            }
        };

//        this.doneLoading = function (action, run_action, args) {
//            var _this = this,
//                requires = [];
//
//            _this.requireRendered.push(action);
//
//            if (!(typeof _this.actionRequire[action] === 'undefined')) {
//                requires = requires.concat(_this.actionRequire[action]);
//            }
//            if (!(typeof _this.actionRequire['*'] === 'undefined')) {
//                requires = requires.concat(_this.actionRequire['*']);
//            }
//
//            if (_this.requireRendered.length === requires.length) {
//                console.log('RUN FINAL ACTION');
//                var actionFullName = "action" + run_action.charAt(0).toUpperCase() + run_action.slice(1);
//                _this[actionFullName](args);
//                _this.requireRendered = [];
//            } else {
//                // dependencies not yet loaded
//            }
//        };

    };

    window.extend = function (settings, o) {

        var Ext = settings.target,
            singleton = (typeof settings.singleton === 'undefined')?false:settings.singleton;

        if ($.isFunction(o)) {
            if (singleton) {

                o = new o();
                return $.extend(new Ext(), o);

            } else {
                var ext = new Ext();
                for (var property in ext) {
                    if (typeof o[property] === 'undefined') {
                        o.prototype[property] = ext[property];
                    }
                }
                return o;

            }

        } else {
            console.error('I would rather extend constructor');
        }
    };

    window.extend.Model = function (o1, o2) {
        if ($.isFunction(o1)) {
            return extend({'target': Model}, o1);
        } else {
            return extend({'target': Model, 'singleton': true}, o2);
        }
    };

    window.extend.View = function (o1, o2) {
        if ($.isFunction(o1)) {
            return extend({'target': View}, o1);
        } else {
            return extend({'target': View, 'singleton': true}, o2);
        }
    };

    window.extend.Controller = function (o1, o2) {
        if ($.isFunction(o1)) {
            return extend({'target': Controller}, o1);
        } else {
            return extend({'target': Controller, 'singleton': true}, o2);
        }
    };

    window.Event = function (sender) {
        'use strict';

        this._sender = sender;
        this._listeners = [];

        this.attach = function (listener) {
            this._listeners.push(listener);
        };

        this.notify = function (args) {
            var index;

            for (index = 0; index < this._listeners.length; index += 1) {
                this._listeners[index](this._sender, args);
            }
        }

    };

    window.url = function (path, args) {
        var out = [], key;

        for (key in args) {
            out.push(key + '=' + encodeURIComponent(args[key]));
        }

        document.location.hash = path+"?"+out.join('&');
    };


    window.url.get = function () {
        var url = document.location.hash.split('?'),
            args = {}, arg;

        if (url.length === 2) {
            var argsArr = url[1].split('&');

            for (var k in argsArr) {
                arg = argsArr[k].split('=');

                args[arg[0]] = decodeURIComponent(arg[1]);
            }
        }

        return {
            path: url[0],
            args: args
        };
    };


});
