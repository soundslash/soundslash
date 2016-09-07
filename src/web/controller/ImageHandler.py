
__version__ = "0.2"

import tornado.web
import tornado.gen
import motor
from bson.objectid import ObjectId
import datetime
from bson.binary import Binary

from controller.BaseHandler import BaseHandler
from controller.ThumbImage import ThumbImage

class ImageHandler(BaseHandler):

    def set_cache(self):

        # cache 365 days
        seconds_to_cache = 60*60*24*365
        expires = (datetime.datetime.today()+datetime.timedelta(seconds=seconds_to_cache)).strftime('%a, %d %b %Y %H:%M:%S %Z')
        self.set_header("Expires", expires)
        self.set_header("Pragma", "cache")
        self.set_header("Cache-Control", "max-age="+unicode(seconds_to_cache))


    @tornado.gen.engine
    def get_image(self, to_format, callback):

        error = None
        select = {"data":1, "format": 1, "_id": 0}

        thumbnail = self.get_argument("thumb", default=None)

        try:

            if thumbnail is not None:
                size = thumbnail.split("x")
                width = int(size[0])
                height = int(size[1])
                thumbnail = "data-"+thumbnail
                select[thumbnail] = 1

            else:
                thumbnail = "data"

            image = yield motor.Op(self.db.images.find_one, {"_id":ObjectId(self.get_argument("id"))}, select)

        except:
            error = {"error": "Bad thumb format or db error"}

        if error is not None:
            callback(error)
        elif image is None:
            callback({"error": "Image does not exist"})
        else:

            # If no format, fail
            # if not "format" in image: image["format"] = "json"

            try:
                if thumbnail not in image:
                    timage = ThumbImage()
                    timage.add_custom_template(width, height)
                    set = timage.process(image["data"], format=image["format"]+">"+to_format, template="custom")
                    db_image = timage.get_data(set[thumbnail], from_format=to_format, to_format=image["format"])
                    if image["format"] == "binary": db_image = Binary(db_image)
                    yield motor.Op(self.db.images.update, {"_id":ObjectId(self.get_argument("id"))},
                                   {"$set":{thumbnail: db_image}}, upsert=False, multi=False)
                    callback(set[thumbnail])
                else:
                    timage = ThumbImage()
                    callback(timage.get_data(image[thumbnail], from_format=image["format"], to_format=to_format))

            except Exception,e:
                callback({"error": unicode(e)})





class JSONImageHandler(ImageHandler):

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):

        self.set_cache()

        image = yield tornado.gen.Task(self.get_image, to_format = "json")

        if "error" in image:
            self.write(image)

        else:
            self.write({"data":image})
        self.finish()


class JPGImageHandler(ImageHandler):

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):

        self.set_cache()

        image = yield tornado.gen.Task(self.get_image, to_format = "binary")

        if "error" in image:
            self.write(image)

        else:
            self.set_header("Content-Type", "image/jpg")
            self.write(image)

        self.finish()
