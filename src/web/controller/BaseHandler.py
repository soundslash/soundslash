__version__ = "0.2"

import tornado.web
import tornado.gen
import motor
import uuid
import random
import sys
from datetime import datetime
from datetime import timedelta
from functools import partial
from bson.objectid import ObjectId
import simplejson as json


class BaseHandler(tornado.web.RequestHandler):

    @tornado.gen.coroutine
    def prepare(self):

        self.template_vars = {}

        # once a time remove sessions marked to delete
        if random.randint(0, 99) == 9:
            created_at = datetime.utcnow()-timedelta(hours=1)
            yield motor.Op(self.db.sessions.remove, {"updated_at": {"$lte": created_at}})

        self.session = yield motor.Op(self.db.sessions.find_one,
                                      {"user_id": self.get_current_user(),
                                       "session_id": self.get_current_session()},
                                      {"updated_at": 1, "logged_as": 1, "_id": 0})

        self.template_vars["session"] = self.session

        if not self.session:
            yield self.destroy_session(redirect=True)
        elif self.session["updated_at"] + timedelta(hours=+1) > datetime.utcnow():
            yield self.renew_session()
        else:
            yield self.destroy_session(redirect=True)


    @tornado.gen.coroutine
    def destroy_session(self, redirect=False):
        if self.get_current_session():
            yield motor.Op(self.db.sessions.remove, {"session_id": self.get_current_session()})
            self.clear_cookie("session_id")
            self.clear_cookie("user_id")
            if redirect:
                self.redirect("/#/user.html?session=expired")


    @tornado.gen.coroutine
    def renew_session(self):
        # it's enough to renew session every half hour
        if self.session["updated_at"] + timedelta(minutes=+30) < datetime.utcnow():
            yield motor.Op(self.db.sessions.update, {"session_id":self.get_current_session()},
                           {"$set":{"updated_at": datetime.utcnow()}}, upsert=False, multi=False)

    @tornado.gen.coroutine
    def new_session(self, user_id, logged_as = None):

        yield self.destroy_session()

        session_id = unicode(uuid.uuid4())
        session = {
            "session_id": session_id,
            "user_id": user_id,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "logged_as": logged_as
        }

        yield motor.Op(self.db.sessions.insert, session)

        self.set_secure_cookie("user_id", user_id)
        self.set_secure_cookie("session_id", session_id)

    @property
    def db(self):
        if not hasattr(self, '_db'):
            self._db = self.settings['db']

        return self._db

    @property
    def batch_size(self):
        return sys.maxint

    def get_current_user(self):
        return self.get_secure_cookie("user_id")

    def get_current_session(self):
        return self.get_secure_cookie("session_id")

    def unblock(self, function, parameters, callback):
        """
        This will unblock function. Parameters are dict.
        """
        self.settings["executor"].submit(
            partial(function, **parameters)
        ).add_done_callback(
            lambda future: tornado.ioloop.IOLoop.instance().add_callback(
                partial(callback, future.result())))

    def dict_normalize(self, dictionary):
        for i in dictionary.keys():
            dictionary[i] = self.__normalize(dictionary[i])
        return dictionary

    def list_normalize(self, l):
        for i in range(len(l)):
            l[i] = self.__normalize(l[i])
        return l

    def __normalize(self, item):
        if isinstance(item, ObjectId):
            item = unicode(item)
        elif isinstance(item, datetime):
            item = item.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(item, list) or isinstance(item, tuple):
            item = self.list_normalize(item)
        elif isinstance(item, dict):
            item = self.dict_normalize(item)
        return item