
__version__ = "0.2"

import re
from controller.BaseHandler import BaseHandler
from helpers.genres import genres
import tornado.web
import tornado.gen
import random
import motor
from bson.son import SON
from collections import OrderedDict
from bson.objectid import ObjectId
from helpers.countries import countries

class MainHandler(BaseHandler):

    def get(self):
        self.render("base.html")

class StreamGenresHandler(BaseHandler):

    def get(self):
        self.render("_stream_genre.html",
            genres= genres)


class SettingsHandler(BaseHandler):

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):

        session = self.get_argument("session", default=False)

        confirm_key = self.get_argument('confirm-key', None)
        user_id = self.get_argument('user-id', None)
        confirmed = None
        try:
            if not confirm_key is None and not user_id is None:
                user = yield motor.Op(self.db.users.find_one, {"_id": ObjectId(user_id), "confirm_key": confirm_key},
                                      {"confirmed": 1,"_id":0, "waiting_email": 1})
                if user is not None:
                    if user["confirmed"]:
                        yield motor.Op(self.db.users.update, {"_id":ObjectId(user_id)},
                                       {"$set":{"confirmed":True, "email": user["waiting_email"]}},
                                       upsert=False, multi=False)
                    else:
                        yield motor.Op(self.db.users.update, {"_id":ObjectId(user_id)},
                                       {"$set":{"confirmed":True}}, upsert=False, multi=False)

                        yield self.new_session(unicode(user_id))

                    confirmed = True
                else:
                    confirmed = False
        except:
            confirmed = False

        self.write({
            "session_file_no": 0,
            "user": self.current_user if self.current_user else False,
            "genres": genres,
            "session": session,
            "confirmed": confirmed
        })
        self.finish()



class ListenHandler(BaseHandler):

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):

        self.write({})
        self.finish()

class SearchHandler(BaseHandler):

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):

        search = self.get_argument("search", default='')
        sort = self.get_argument("sort", default='listeners')

        query = {
            "status": {"$ne": None},
            "$or": [
                { "name": re.compile('.*'+search+'.*', re.IGNORECASE) },
                { "genres": {'$in': [search] } }
            ]
        }
        select = {
            "name":1,
            "description":1,
            "picture": 1,
            "cover_image":1,
            "genres":1,
            "public":1,
            "_id": 1}

        page = int(self.get_argument("p", default='1'))
        per_page = 10
        skip = (page-1)*10

        cursor = self.db.streams.find(query, select).sort([(sort, -1)]).skip(skip).limit(per_page)
        data = yield motor.Op(cursor.to_list, length=per_page)

        for i in xrange(len(data)):
            data[i]["_id"] = unicode(data[i]["_id"])

        if not search:
            if sort == "_id":
                title = 'Recently created'
            else:
                title = 'The most popular of today'
        else:
            title = 'Showing results for "{}"'.format(search)


        self.write({
            'title': title,
            'streams': data,
            'search': search,
            'page': page
        })
        self.finish()


class GenresHandler(BaseHandler):

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):

        # count
        query = yield motor.Op(self.db.command,
                               SON([
                                   ("aggregate", "streams"),
                                   ("pipeline", [
                                       {"$project": {"_id": 0, "genres": 1}},
                                       {"$unwind": '$genres'},
                                       {
                                           "$group": {
                                               '_id': "$genres",
                                               'count': { "$sum": 1}
                                           },
                                       },
                                       # {
                                       #     "$sort": SON([("_id.count", 1)])
                                       # }
                                       ])
                               ]))

        # display only streams, which contain at least one stream
        genres_grouped = {}
        for genre in query['result']:
            for parent, child in genres.items():
                if genre['_id'] in child:
                    if parent not in genres_grouped:
                        genres_grouped[parent] = {}
                    genres_grouped[parent][genre['_id']] = { "count": genre['count'] }
                    break

        # sort
        genres_grouped = OrderedDict(sorted(genres_grouped.iteritems(), key=lambda x: x[0]))
        for key in genres_grouped:
            genres_grouped[key] = OrderedDict(sorted(genres_grouped[key].iteritems(), key=lambda x: x[0]))

        self.write({
            'genres': genres_grouped
        })
        self.finish()

class RadioHandler(BaseHandler):

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):


        stream = yield motor.Op(self.db.streams.find_one,
                              {"user_id": self.get_current_user()},
                              {
                                  "name": 1,
                                  "_id": 1})

        if stream:
            stream['_id'] = unicode(stream['_id'])

        self.write({
            "stream": stream,
            "session_file_no": 0,
            "user": self.current_user if self.current_user else False,
            "genres": genres
        })
        self.finish()


class UserProfileHandler(BaseHandler):

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):

        user = yield motor.Op(self.db.users.find_one,
                                                    {"_id": ObjectId(self.get_current_user())},
                                                    {
                                                        "email": 1,
                                                        "name": 1,
                                                        "country": 1,
                                                        "_id": 0})
        if user is None: user = False
        self.write({
            "user": user,
            "countries": countries
        })
        self.finish()

class RandomUsersHandler(BaseHandler):

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):

        limit = 10

        # random attribute
        # http://cookbook.mongodb.org/patterns/random-attribute/

        rand = random.uniform(0,1)

        query = {"confirmed": True,
            "random": {"$gte": rand}}
        select = {"picture":1, "_id": 1}

        cursor = self.db.users.find(query, select).limit(limit)
        data1 = yield motor.Op(cursor.to_list, length=limit)

        if len(data1) < limit:
            query["random"] = {"$lt": rand}
            cursor = self.db.users.find(query, select).limit(limit-len(data1))

            data2 = yield motor.Op(cursor.to_list, length=limit-len(data1))
        else:
            data2 = []

        data = data1 + data2

        for i in xrange(len(data)):
            data[i]["_id"] = unicode(data[i]["_id"])

        random.shuffle(data)

        self.write({"users": data})
        self.finish()


class MainRedirectHandler(BaseHandler):

    def get(self):

        self.redirect("/index.html")