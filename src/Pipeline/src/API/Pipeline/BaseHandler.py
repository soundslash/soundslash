import tornado.web
import tornado.gen
# import asyncmongo
import motor
import uuid
from datetime import datetime
from datetime import timedelta
from tornado.options import define, options
from concurrent.futures import ThreadPoolExecutor
from functools import partial, wraps


class BaseHandler(tornado.web.RequestHandler):

    @property
    def db(self):
        if not hasattr(self, '_db'):
            self._db = self.settings['db']
        return self._db

    def get_current_user(self):
        return self.get_secure_cookie("user")


    def unblock(self, function, parameters, callback):
        """
        This will unblock function. Parameters are dict.
        """
        self.settings["executor"].submit(
            partial(function, **parameters)
        ).add_done_callback(
            lambda future: tornado.ioloop.IOLoop.instance().add_callback(
                partial(callback, future.result())))



class BaseWebSocketHandler(tornado.websocket.WebSocketHandler):
    pass