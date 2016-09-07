
__version__ = "0.2"

import tornado.web
import tornado.gen
from concurrent.futures import ThreadPoolExecutor
import tornado.ioloop
import tornado.web
import motor
import pygst
pygst.require("0.10")
import gst, datetime
from bson.objectid import ObjectId
from PIL import Image
import base64
import StringIO

from controller.BaseHandler import BaseHandler
from helpers.genres import is_in_genres

class ValidatorHandler(BaseHandler):

    @tornado.web.asynchronous
    @tornado.web.authenticated
    @tornado.gen.coroutine
    def post(self):

        t1 = self.get_argument("stream-terms1")
        t1 = 'true'
        t2 = self.get_argument("stream-terms2")

        if t1 == 'true' and t2 == 'true':
            self.write({})
        else:
            self.write({"error": "Please accept terms and conditions"})

        self.finish()

class UploadHandler(BaseHandler):

    @tornado.web.asynchronous
    @tornado.web.authenticated
    @tornado.gen.coroutine
    def post(self):

        posted_file = self.request.files['files[]'][0]
        posted_file_size = len(posted_file["body"])
        original_filename = posted_file['filename']

        if not self.get_current_user():
            self.write({"files": [
                {
                    "fileId": self.get_argument("fileId"),
                    "name": original_filename,
                    "error": "Not allowed to upload file "+original_filename
                }
            ]})
            self.finish()
        else:

            stream_id = self.get_argument("streamId")
            stream = yield motor.Op(self.db.streams.find_one, {"_id":ObjectId(stream_id)}, {"user_id":1, "_id": 0})
            if stream is None or not stream["user_id"] == self.get_current_user():
                raise tornado.web.HTTPError(403)

            group_id = self.get_argument("groupId")
            group = yield motor.Op(self.db.groups.find_one, {"_id":ObjectId(group_id)}, {"stream_id":1, "_id": 0})
            if group is None or not unicode(group["stream_id"]) == str(stream_id):
                raise tornado.web.HTTPError(403)

            if self.get_argument("streamCreate", "true") == "true":
                name = self.get_argument("streamName", default=None)
                if name is not None:
                    if int(self.get_argument("streamPublic")) == 1:
                        public = True
                    else:
                        public = False

                    stream_genres = self.get_argument("streamGenre")

                    if not stream_genres:
                        stream_genres = []
                    else:
                        stream_genres = stream_genres.split(",")

                        for genre in stream_genres:
                            if not is_in_genres(genre):
                                stream_genres.remove(genre)

                    if not name:
                        name = "Noname"

                    set = {
                        "name": name,
                        "genres": stream_genres,
                        # "cover_image": self.get_argument("streamCoverImage"),
                        "public": public,
                        "users": [{"password": self.get_argument("streamPassword")}],
                        "description": self.get_argument("streamDescription")
                    }
                    yield motor.Op(self.db.streams.update, {"_id":ObjectId(stream_id)},
                                   {"$set":set}, upsert=False, multi=False)

            user = yield motor.Op(self.db.users.find_one, {"_id":ObjectId(self.get_current_user())},
                                  {"size":1, "max_size": 1, "_id": 0})
            stream = yield motor.Op(self.db.streams.find_one, {"_id":ObjectId(stream_id)},
                                    {"size":1, "max_size": 1, "quality": 1, "_id": 0})

            size = user["size"]+posted_file_size
            max_size = user["max_size"]
            stream_size = stream["size"]+posted_file_size
            stream_max_size = stream["max_size"]
            if size > max_size or stream_size > stream_max_size:
                self.write({"files": [
                    {
                        "fileId": self.get_argument("fileId"),
                        "name": original_filename,
                        "error": "Cannot save file "+original_filename+": Maximum allowed size exceeded"
                    }
                ]})
                self.finish()
            else:

                if posted_file["content_type"].startswith("audio/"):
                    user_id = self.get_current_user()
                    yield motor.Op(self.db.users.update, {"_id":ObjectId(user_id)},
                                   {"$inc":{"size": posted_file_size}}, upsert=False, multi=False)
                    yield motor.Op(self.db.streams.update, {"_id":ObjectId(stream_id)},
                                   {"$inc":{"size": posted_file_size}}, upsert=False, multi=False)
                    q = {
                        "filename": original_filename,
                        "body": posted_file['body'],
                        "user_id": self.get_current_user(),
                        "stream_id": stream_id,
                        "group_id": group_id,
                        "title": self.get_argument("title").strip(),
                        "artist": self.get_argument("artist").strip(),
                        "quality": max(stream["quality"])
                    }
                    if self.get_argument("weight", None) is not None:
                        q["weight"] = int(self.get_argument("weight"))
                    yield tornado.gen.Task(self.add_to_process_queue, q)

                    response = {"files": [
                        {
                            "fileId": self.get_argument("fileId"),
                            "name": original_filename,
                            "size": posted_file_size,
                            "streamId": stream_id
                        }
                    ]}

                    self.write(response)
                    self.finish()

                # # TODO This is so far disabled
                # elif posted_file["content_type"].startswith("image/"):
                #
                #
                #     ti = ThumbImage()
                #     img = ti.process(posted_file['body'],
                #          format="binary>json",
                #          tags=[],
                #          attrs={"filename": original_filename,"random": random.uniform(0,1)},
                #          template="player-photos")
                #
                #     image_id = yield motor.Op(self.db.images.insert, img)
                #
                #     response = yield motor.Op(self.db.streams.update, {"_id":ObjectId(stream_id)},
                #                           {"$push":{"images":unicode(image_id)}}, upsert=False, multi=False)
                #
                #     response = {"files": [
                #         {
                #             "fileId": self.get_argument("fileId"),
                #             "name": original_filename,
                #             "size": posted_file_size,
                #             "streamId": stream_id
                #         }
                #     ]}
                #
                #     self.write(response)
                #     self.finish()

                else:
                    self.write({"files": [
                        {
                            "fileId": self.get_argument("fileId"),
                            "name": original_filename,
                            "error": "Cannot save file "+original_filename+": File format not supported"
                        }
                    ]})
                    self.finish()



    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def new_stream(self, name, genre, callback):

        stream = {
            "name": self.get_argument("name"),
            "genre": self.get_argument("genre").split(','),
            }
        response = yield motor.Op(self.db.streams.insert, stream)

        callback(response)

    @tornado.web.asynchronous
    def add_to_process_queue(self, file, callback):

        self.settings["upload_processor"]["lock"].acquire()

        self.settings["upload_processor"]["connection"].send(file)
        self.settings["upload_processor"]["lock"].release()

        callback()


def make_thumb(data, width=500, height=500):
    imageFile = StringIO.StringIO(data)

    im1 = Image.open(imageFile)

    result_width = width
    result_height = height

    # new size according width
    new_width = result_width
    new_height = int(im1.size[1]*result_width/im1.size[0])

    # is image bigger?
    if new_width < result_width or new_height < result_height:
        # new size according height
        new_width = int(im1.size[0]*result_height/im1.size[1])
        new_height = result_height

    im1 = im1.resize((new_width, new_height), Image.ANTIALIAS)

    # by width
    if result_width == new_width:
        top = int(new_height/2-result_height/2)
        box = (0, top, result_width, result_height+top)
    else:
        left = int(new_width/2-result_width/2)
        box = (left, 0, left+result_width, result_height)

    im1 = im1.crop(box)

    output = StringIO.StringIO()
    im1.save(output, format="JPEG")
    data = output.getvalue()
    output.close()
    return "data:image/jpeg;base64,"+base64.b64encode(data)


class StatusHandler(BaseHandler):

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self):

        stream = yield motor.Op(self.db.streams.find_one, {"_id":ObjectId(self.get_argument("streamId"))},
                                {"status":1, "_id": 0})

        if stream is None:
            self.write({"status": "unknown"})
        else:
            self.write({"status": stream["status"]})

        self.finish()



class MetaHandler(BaseHandler):

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self):

        stream = yield motor.Op(self.db.streams.find_one, {"_id":ObjectId(self.get_argument("stream_id"))},
                                {"current":1, "name": 1, "user_id": 1, "_id": 0})

        user = yield motor.Op(self.db.users.find_one, {"_id":ObjectId(stream['user_id'])},
                                {"name": 1, "email": 1, "_id": 0})

        self.write({"stream": stream, "user": user})
        self.finish()







