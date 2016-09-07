
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

class AboutStreamAdminHandler(AdminHandler):

    @tornado.web.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self, stream_id):

        stream = yield motor.Op(self.db.streams.find_one, {"_id": ObjectId(stream_id)},
                                {
                                    "reencoding":1,
                                    "name": 1,
                                    "description": 1,
                                    "genres": 1,
                                    "count": 1,
                                    "_id": 0,
                                    "status": 1,
                                    "size": 1,
                                    "max_size": 1,
                                    "quality": 1,
                                    "public": 1,
                                    "users": 1,
                                })


        self.template_vars["stream"] = stream
        self.template_vars["menu"] = "streams"
        self.template_vars["submenu"] = "about"
        self.template_vars["stream_id"] = stream_id

        self.template_vars["genres"] = genres

        self.render("admin/about.html", **self.template_vars)

    @tornado.web.asynchronous
    @tornado.web.authenticated
    @tornado.gen.engine
    def post(self, stream_id):

        name = self.get_argument("stream-name")
        description = self.get_argument("stream-description")

        if 'stream-genre' in self.request.arguments:
            stream_genres = self.request.arguments['stream-genre']
        else:
            stream_genres = []


        for genre in stream_genres:
            if not is_in_genres(genre):
                stream_genres.remove(genre)

        public = int(self.get_argument("stream-public"))
        password = self.get_argument("stream-password", "")

        block = self.get_argument("block", False)

        if block == "on":
            public = 0
            password = ''.join(random.choice(string.ascii_lowercase) for x in range(4))

            stream = yield motor.Op(self.db.streams.find_one, {"_id": ObjectId(stream_id)},
                                    {
                                        "user_id": 1,
                                        "_id": 0,
                                        "name": 1,
                                        })

            user = yield motor.Op(self.db.users.find_one, {"_id": ObjectId(stream["user_id"])},
                                    {
                                        "name": 1,
                                        "email": 1,
                                        "_id": 0,
                                        })

            new_email = EmailWrapper()
            new_email.set_subject("Your stream "+stream["name"]+" at SoundSlash.com was set to private")
            new_email.set_sender("noreply@soundslash.com")
            new_email.add_recipient(user["email"])
            new_email.set_body("email/set_to_private_stream.html", args = {
                "name": user["name"],
                "stream_name": stream["name"],
                "password":password,
            })

            yield tornado.gen.Task(self.unblock, function=new_email.send, parameters={})



        reencoding = self.get_argument("reencoding", False)
        q0 = self.get_argument("quality-0", False)
        q0_2 = self.get_argument("quality-0-2", False)
        q0_4 = self.get_argument("quality-0-4", False)
        q0_6 = self.get_argument("quality-0-6", False)
        q0_8 = self.get_argument("quality-0-8", False)
        q1 = self.get_argument("quality-1", False)
        max_size = int(self.get_argument("max-size"))*1048576

        update = {
            "name": name,
            "description": description,
            "genres": stream_genres,
            "public": public,
            "users": [{"password": password}]
        }

        if reencoding == "on": reencoding = True
        else: reencoding = False
        update["reencoding"] = reencoding



        quality = []
        if q0 == "on": quality.append(float(0))
        if q0_2 == "on": quality.append(float(0.2))
        if q0_4 == "on": quality.append(float(0.4))
        if q0_6 == "on": quality.append(float(0.6))
        if q0_8 == "on": quality.append(float(0.8))
        if q1 == "on": quality.append(float(1))

        stream = yield motor.Op(self.db.streams.find_one, {"_id":ObjectId(stream_id)}, {"reencoding":1,"_id":0}, upsert=False, multi=False)

        if stream["reencoding"] is False and reencoding:
            pass
        else:
            update["quality"] = quality

        update["max_size"] = max_size

        update = yield motor.Op(self.db.streams.update, {"_id":ObjectId(stream_id)}, {"$set": update}, upsert=False, multi=False)

        if "err" in update:
            response = {"error": update["err"]}
        else:
            response = {"msg": "Successfully saved"}

        self.write(response)
        self.finish()

