
__version__ = "0.2"

import tornado.web
import tornado.gen
import tornado.websocket
import motor
from bson.objectid import ObjectId
import simplejson as json
import random
import string

from controller.admin.AdminHandler import AdminHandler
from helpers.genres import genres
from helpers.genres import is_in_genres
from controller.EmailWrapper import EmailWrapper

class AboutStreamHandler(AdminHandler):

    @tornado.web.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self):

        stream_id = self.get_argument("stream_id")
        name = self.get_argument("stream-name")
        description = self.get_argument("stream-description")
        active = int(self.get_argument("stream-active"))
        if active == 1: active = True
        else: active = False

        if 'stream-genre' in self.request.arguments:
            stream_genres = self.request.arguments['stream-genre']
        else:
            stream_genres = []


        for genre in stream_genres:
            if not is_in_genres(genre):
                stream_genres.remove(genre)

        public = int(self.get_argument("stream-public"))
        password = self.get_argument("stream-password", "")

        update = {
            "name": name,
            "description": description,
            "active": active,
            "genres": stream_genres,
            "public": public,
            "users": [{"password": password}]
        }

        picture = self.get_cookie("stream-picture")
        if picture is not None:
            update['picture'] = picture
            image = yield motor.Op(self.db.images.update, {"_id":ObjectId(update['picture']), "tags": {"$in": ["delete"]}},
                                   {"$set":{"tags": ["stream_profile"]}}, upsert=False, multi=False)

        self.clear_cookie("stream-picture")
        cover_image = self.get_cookie("stream-background-picture")
        if cover_image is not None:
            update['cover_image'] = cover_image
            image = yield motor.Op(self.db.images.update, {"_id":ObjectId(update['cover_image']), "tags": {"$in": ["delete"]}},
                                   {"$set":{"tags": ["stream_cover"]}}, upsert=False, multi=False)
        self.clear_cookie("stream-background-picture")

        update = yield motor.Op(self.db.streams.update, {"_id":ObjectId(stream_id)}, {"$set": update}, upsert=False, multi=False)

        if "err" in update:
            response = {"error": update["err"]}
        else:
            response = {"msg": "Successfully saved"}

        self.write(response)
        self.finish()


    @tornado.web.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):

        stream_id = self.get_argument("stream_id")

        stream = yield motor.Op(self.db.streams.find_one, {"_id": ObjectId(stream_id)},
                                {
                                    "reencoding":1,
                                    "name": 1,
                                    "description": 1,
                                    "picture": 1,
                                    "cover_image": 1,
                                    "genres": 1,
                                    "count": 1,
                                    "_id": 0,
                                    "status": 1,
                                    "size": 1,
                                    "max_size": 1,
                                    "quality": 1,
                                    "public": 1,
                                    "active": 1,
                                    "users": 1,
                                    })


        self.write({"stream": stream, "genres": genres})
        self.finish()