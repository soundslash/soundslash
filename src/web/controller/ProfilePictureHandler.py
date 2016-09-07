
__version__ = "0.2"

import tornado.web
import tornado.gen
import motor
import random
import simplejson as json
from datetime import datetime, timedelta

from controller.BaseHandler import BaseHandler
from controller.ThumbImage import ThumbImage


class ProfilePictureHandler(BaseHandler):

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self):

        posted_file = self.request.files['profile'][0]
        original_filename = posted_file['filename']

        ti = ThumbImage()
        result = {}
        try:
            img_cover = ti.process(posted_file['body'], format="binary>json", tags=["delete"],
                                   attrs={"filename": original_filename, "random": random.uniform(0,1)},
                                   template="profile")
        except Exception, e:
            result = {"error": unicode(e)}

        if "error" not in result:
            image_id = yield motor.Op(self.db.images.insert, img_cover)
            self.set_cookie("profile_picture", unicode(image_id))
            result = {"image_id": unicode(image_id), "data": img_cover["data-160x160"]}


        # once a time remove images marked to delete
        if random.randint(0, 9) == 9:
            created_at = datetime.utcnow()-timedelta(minutes=60)
            yield motor.Op(self.db.images.remove, {"tags": {"$in": ["delete"]}, "created_at": {"$lte": created_at}})

        self.set_header("Content-Type", "text/plain")
        self.write(json.dumps(result))
        self.finish()



class StreamPictureHandler(BaseHandler):

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self):

        if 'picture' in self.request.files:
            pid = 'picture'
        elif 'background-picture' in self.request.files:
            pid = 'background-picture'
        elif 'picture-wide' in self.request.files:
            pid = 'picture-wide'

        posted_file = self.request.files[pid][0]
        original_filename = posted_file['filename']

        ti = ThumbImage()
        result = {}
        try:
            img_cover = ti.process(posted_file['body'], format="binary>json", tags=["delete"],
                                   attrs={"filename": original_filename, "random": random.uniform(0,1)},
                                   template="profile")
        except Exception, e:
            result = {"error": unicode(e)}

        if "error" not in result:
            image_id = yield motor.Op(self.db.images.insert, img_cover)
            self.set_cookie("stream-"+pid, unicode(image_id))
            if 'background-picture' in self.request.files:
                result = {"image_id": unicode(image_id), "data": img_cover["data-256x160"]}
            elif 'picture-wide' in self.request.files:
                result = {"image_id": unicode(image_id), "data": img_cover["data-160x90"]}
            else:
                result = {"image_id": unicode(image_id), "data": img_cover["data-160x160"]}


        # once a time remove images marked to delete
        if random.randint(0, 9) == 9:
            created_at = datetime.utcnow()-timedelta(minutes=60)
            yield motor.Op(self.db.images.remove, {"tags": {"$in": ["delete"]}, "created_at": {"$lte": created_at}})

        self.set_header("Content-Type", "text/plain")
        self.write(json.dumps(result))
        self.finish()

