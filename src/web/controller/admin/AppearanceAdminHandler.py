
__version__ = "0.2"

import tornado.web
import tornado.gen
import random
import motor
from controller.admin.AdminHandler import AdminHandler
from bson.objectid import ObjectId
from datetime import datetime, timedelta
import simplejson as json

from controller.ThumbImage import ThumbImage

class AppearanceAdminHandler(AdminHandler):

    @tornado.web.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self, stream_id):

        stream = yield motor.Op(self.db.streams.find_one, {"_id": ObjectId(stream_id)},
                                {"reencoding":1, "name": 1, "cover_image": 1, "_id": 1})
        print stream["cover_image"]
        cover_picture = yield motor.Op(self.db.images.find_one, {"_id":ObjectId(stream["cover_image"])},
                                       { "tags": 1, "_id": 0 }, upsert=False, multi=False)

        self.clear_cookie("cover_picture")
        self.clear_cookie("cover_stream_id")

        self.template_vars["menu"] = "appearance"
        self.template_vars["submenu"] = "appearance"
        self.template_vars["stream"] = stream
        self.template_vars["stream_id"] = stream_id
        if cover_picture is not None and "uploaded" in cover_picture["tags"]:
            uploaded = True
        else:
            uploaded = False
        self.template_vars["cover_uploaded"] = uploaded

        self.render("admin/appearance.html", **self.template_vars)

    @tornado.web.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self, stream_id):

        cover = self.get_argument("stream-cover-image")

        image = yield motor.Op(self.db.images.update, {"_id":ObjectId(cover), "tags": {"$in": ["delete"]}},
                           {"$set":{"tags": ["cover", "uploaded"]}}, upsert=False, multi=False)
        if not image["err"] and image["n"] == 1:
            yield motor.Op(self.db.streams.update, {"_id":ObjectId(stream_id)},
                           {"$set":{"cover_image": cover}}, upsert=False, multi=False)

        self.write({"msg": "Successfully saved"})
        self.finish()


class CoverPictureAdminHandler(AdminHandler):

    @tornado.web.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self, stream_id):

        posted_file = self.request.files['cover'][0]
        original_filename = posted_file['filename']

        ti = ThumbImage()
        result = {}
        try:
            img_cover = ti.process(posted_file['body'], format="binary>json", tags=["delete"],
                                   attrs={"filename": original_filename, "random": random.uniform(0,1)},
                                   template="player-cover")
        except Exception, e:
            result = {"error": unicode(e)}

        if "error" not in result:
            image_id = yield motor.Op(self.db.images.insert, img_cover)
            self.set_cookie("cover_picture", unicode(image_id))
            self.set_cookie("cover_stream_id", unicode(stream_id))
            result = {"image_id": unicode(image_id), "data": img_cover["data-332x128"]}

        # once a time remove images marked to delete
        if random.randint(0, 9) == 9:
            created_at = datetime.utcnow()-timedelta(minutes=60)
            yield motor.Op(self.db.images.remove,
                           {"tags": {"$in": ["delete"]}, "created_at": {"$lte": created_at}})

        self.set_header("Content-Type", "text/plain")
        self.write(json.dumps(result))
        self.finish()
