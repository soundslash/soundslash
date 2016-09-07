
__version__ = "0.2"

import os
import time
import tornado.web
import tornado.gen
import uuid
import tornado.ioloop
import tornado.web
import tornado.httpclient
import motor
import gridfs
import pygst
pygst.require("0.10")
import gst
from threading import Condition
from threading import Thread
from bson.objectid import ObjectId
import random
import datetime
import urllib

from controller.TagsExtractor import TagsExtractor
from controller.PipelineRouter import PipelineRouter
from controller.AudioPreprocessor import AudioPreprocessor
from controller.UploadHandler import make_thumb

class UploadProcessor(Thread):


    def __init__(self, syncdb):
        Thread.__init__(self)
        self.db = syncdb
        self.queue = []
        self.cv = Condition()

    def run(self):
        while True:
            self.cv.acquire()
            while not self.queue:
                self.cv.wait()
            file_to_process = self.queue.pop()
            self.cv.release()
            self.process(file_to_process)


    def process(self, original_file):

        # Encode, apply replaygain, extract tags
        (tags, processed_filepath) = self.do_process(original_file['body'], original_file["quality"])

        with open(processed_filepath, "rb") as file:
            size = os.fstat(file.fileno()).st_size
            original_file_size = len(original_file['body'])
            self.save(tags, file, original_file['filename'], size, processed_filepath,
                      original_file["user_id"], original_file["stream_id"], original_file_size,
                      original_file["title"], original_file["artist"], original_file["group_id"],
                      original_file["quality"], original_file)



    def do_process(self, data, quality):

        from_filepath = "/tmp/"+unicode(uuid.uuid4())
        to_filepath = "/tmp/"+unicode(uuid.uuid4())

        # print "Using temp files: "+from_filepath+" and "+to_filepath

        with open(from_filepath, 'wb') as file:
            file.write(data)

        # Extract tags, find out replaygain values
        tags_extractor = TagsExtractor(from_filepath)
        tags_extractor.start()
        tags_extractor.join()

        # Encode, apply replaygain
        audio_preprocessor = AudioPreprocessor(tags_extractor.tags, from_filepath, to_filepath, quality)
        audio_preprocessor.start()
        audio_preprocessor.join()

        # Remove original temp file
        try:
            os.remove(from_filepath)
        except OSError:
            pass

        return audio_preprocessor.tags, to_filepath

    def save(self, tags, file, original_filename, size, processed_filepath, user_id, stream_id,
             original_file_size, title, artist, group_id, quality, original_file):

        # Save file to database
        fs = gridfs.GridFS(self.db)
        file_id = fs.put(file)

        # Format tags in order to database can consume
        tags_db = {}
        for k,v in tags.items():
            if type(v) == gst.Buffer:
                tags_db[unicode(k)] = {}
                try:
                    tags_db[unicode(k)]["data"] = make_thumb(v)
                except:
                    pass
            elif isinstance(v, basestring) or isinstance(v, int) or isinstance(v, float) or isinstance(v, long):
                tags_db[unicode(k)] = v

        if "artist" in tags_db:
            artist = self.__get_most_valid([artist, tags_db["artist"]])
        else:
            artist = self.__get_most_valid([artist])

        if "title" in tags_db:
            title = self.__get_most_valid([title, tags_db["title"]])
        else:
            title = self.__get_most_valid([title])

        if "album" in tags_db:
            album = self.__get_most_valid([tags_db["album"]])
        else:
            album = "Unknown"

        # Insert structure to database, which contains the metatags
        # constructed from tags and available informations about file

        if "weight" in original_file:
            weight = original_file["weight"]
        else:
            weight = self.__get_id()

        file = {
            "user_id": user_id,
            "original_filename": original_filename,
            "file_id": unicode(file_id),
            "size": size,
            "tags": tags_db,
            "title": title,
            "artist": artist,
            "album": album,
            "stream_id": stream_id,
            "played": 0,
            "random": random.uniform(0,1),
            "quality": quality,
            "created_at": datetime.datetime.utcnow(),
            "groups": [
                {
                    "id": group_id,
                    "weight": weight
                }
            ]
        }
        # groups = [
        #   {"id": ObjectId(), "weight": X}
        # ]
        self.db.media.insert(file)

        # Update limits to user
        self.db.users.update({"_id":ObjectId(user_id)},
                             {"$inc":{"size": size-original_file_size}}, upsert=False, multi=False)
        self.db.streams.update({"_id":ObjectId(stream_id)},
                               {"$inc":{"count": 1, "size": size-original_file_size}}, upsert=False, multi=False)

        stream_obj = self.db.streams.find_one({"_id":ObjectId(stream_id)},
                                              {"status": 1, "pipeline_server": 1, "_id": 0},
                                              upsert=False, multi=False)
        # print unicode(stream_obj)
        if stream_obj["status"] is None:
            self.db.streams.update({"_id":ObjectId(stream_id)},
                                   {"$set":{"status": "ready"}}, upsert=False, multi=False)

        if stream_obj["pipeline_server"] is not None:
            # SEND TO PIPE UPDATE PLAYLIST
            pipeline = self.db.servers.find_one({"_id":ObjectId(stream_obj["pipeline_server"])},
                                                {"local_ip": 1, "port": 1, "_id": 0}, upsert=False, multi=False)

            post_args = {
                "stream": stream_id,
                "group": group_id
            }

            pr = PipelineRouter(self.db, None)
            url = pr.get_playlist_update_url(pipeline)

            pr.request_sync(url, post_args)



        # Remove processed temp file, because we no longer need it
        try:
            os.remove(processed_filepath)
        except OSError:
            pass


    def is_error(self, response):
        try:
            if response.error:
                return True
            else:
                return False
        except:
            return True
        return False

    def __get_most_valid(self, possibilities):
        for name in possibilities:
            name = unicode(name)
            if not name or name == "":
                continue
            else:
                return name
        return "Unknown"


    def __get_id(self):
        now = datetime.datetime.now()
        return int(time.mktime(now.timetuple())*1e3 + now.microsecond/1e3 * 1000)
