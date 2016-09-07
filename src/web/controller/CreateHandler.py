
__version__ = "0.2"

import tornado.web
import tornado.gen
import motor
import sys
import random
from bson.objectid import ObjectId


from controller.BaseHandler import BaseHandler
from controller.ThumbImage import ThumbImage

class CreateHandler(BaseHandler):

    @tornado.web.asynchronous
    @tornado.web.authenticated
    @tornado.gen.coroutine
    def post(self):

        user = yield motor.Op(self.db.users.find_one, {"_id":ObjectId(self.get_current_user())}, {"max_streams":1, "_id": 0})
        streams = yield motor.Op(self.db.streams.find({"user_id":self.get_current_user(), "status": {"$ne": None}}).count)

        if user["max_streams"] < (streams+1):
            response = {"error": "Maximum number of streams reached"}

        else:

            stream = {
                # "name": self.get_argument("streamName"),
                # "genres": self.get_argument("streamGenre").split(','),
                "name": "Noname",
                "genres": [],
                # "cover_image": self.get_argument("streamCoverImage"),
                "public": True,
                "users": [{"password": ""}],
                "description": "",
                "reencoding": False,
                "status": None,
                "user_id": self.get_current_user(),
                "size": 0,
                "max_size": 52428800,
                "count": 0,
                "default_program_id": None,
                # "public": False,
                "quality": [float(0)],
                "pipeline_server": None,
                "tags": ["Album", "Year"],
                "active": True
            }

            stream_id = yield motor.Op(self.db.streams.insert, stream)


            group_favorites = {
                "stream_id": stream_id,
                "user_id": self.get_current_user(),
                }

            group_favorites_id = yield motor.Op(self.db.groups.insert, group_favorites)
            group_favorites_id = unicode(group_favorites_id)

            group = {
                "stream_id": stream_id,
                "user_id": self.get_current_user(),
            }

            group_id = yield motor.Op(self.db.groups.insert, group)
            group_id = unicode(group_id)


            program = {
                "name": "Default",
                "groups": [unicode(group_id)],
                "selection": "sequence",
                "start": None,
                "end": None,
                "force_start": False,
                "repeating": None,
                "jukebox": False,
                "fade_in": 0,
                "fade_out": 0
                #     sequence / shuffle
            }

            default_program_id = yield motor.Op(self.db.programs.insert, program)
            default_program_id = unicode(default_program_id)

            yield motor.Op(self.db.streams.update, { "_id": stream_id }, { "$set": { "default_program_id": default_program_id,
                                                                                     "fav_group_id": group_favorites_id }}, upsert=False, multi=False)

            stream_id = unicode(stream_id)

            response = {"streamId": stream_id, "groupId": group_id, "groupFavId": group_favorites_id}

        self.write(response)
        self.finish()



class CoverHandler(BaseHandler):

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):

        cursor = self.db.images.find({"tags": {"$all": ["player", "cover"]}}, {"_id": 1})

        self.write(self.dict_normalize({
            "covers": (yield motor.Op(cursor.to_list, self.batch_size))
        }))
        self.finish()

class UploadCoverHandler(BaseHandler):

    def get(self):

        self.render("upload_cover.html")

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self):

        posted_file = self.request.files['file'][0]
        original_filename = posted_file['filename']

        ti = ThumbImage()
        result = {}
        try:
            img_cover = ti.process(posted_file['body'], format="binary>json", tags=["player", "cover"],
                                   attrs={"filename": original_filename, "random": random.uniform(0,1)},
                                   template="player-cover")
        except Exception, e:
            result = {"error": unicode(e)}

        if "error" not in result:
            image_id = yield motor.Op(self.db.images.insert, img_cover)
            result = {"image_id": unicode(image_id)}

        self.write(result)
        self.finish()
