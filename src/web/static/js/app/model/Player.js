
define(function (require) {
    "use strict";

    return extend.Model(function () {

        this._state = 'stopped';
        this._volume = 80;
        this._object = null;
        this._force_flash = false;
        this._artist = null;
        this._title = null;
        this._stream = null;
        this._user = null;

        this.stateChanged = new app.model.Event(this);
        this.volumeChanged = new app.model.Event(this);
        this.metadataChanged = new app.model.Event(this);

        var _this = this;

        this.stop = function () {
            this._state = 'stopped';
        };

        this.play = function () {
            this._state = 'playing';
        };

        this.pause = function () {
            this._state = 'paused';
        };

        this.get_metadata = function () {
            return {
                'artist': _this._artist,
                'title':  _this._title,
                'stream': _this._stream,
                'user':   _this._user
            };
        };

        this.set_metadata = function (metadata) {
            var key;
            for (key in metadata) {
                _this["_"+key] = metadata[key];
            }
            _this.metadataChanged.notify(metadata);
        };

        this.events = function () {
            _this.watch('_state', function (prop, oldval, val) {
                _this.stateChanged.notify({
                    'oldval': oldval,
                    'val': val
                });
                return val;
            });

            _this.watch('_volume', function (prop, oldval, val) {
                _this.volumeChanged.notify({
                    'oldval': oldval,
                    'val': val
                });
                return val;
            });
        };

    });
});