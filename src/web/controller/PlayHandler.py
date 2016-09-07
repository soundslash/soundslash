
__version__ = "0.2"

import tornado.web
import tornado.gen
import tornado.ioloop
import tornado.web
import tornado.httpclient
import motor
import pygst
pygst.require("0.10")
import gst
from bson.objectid import ObjectId
import urllib
import simplejson as json
import random

from controller.BaseHandler import BaseHandler
from controller.PipelineRouter import PipelineRouter

class RandomPlayHandler(BaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self):
        try:
            self.random_play_count
            if random.randint(0, 10) == 5:
                raise Exception('Recount number of streams')
        except:
            count = yield motor.Op(self.db.streams.count)
            self.random_play_count = count

        skip = random.randint(0, self.random_play_count-1)

        stream = yield motor.Op(self.db.streams.find_one, {}, {"_id": 1}, skip=skip)
        self.write({"random":unicode(stream["_id"])})
        self.finish()

class PlayHandler(BaseHandler):

    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self):

        stream = yield motor.Op(self.db.streams.find_one,
                                { "_id": ObjectId(self.get_argument("streamId")) },
                                {   "name": 1,
                                    "description": 1,
                                    "genres": 1,
                                    "status": 1,
                                    "public": 1,
                                    "cover_image": 1,
                                    "picture": 1,
                                    "user_id": 1,
                                    "pipeline_server": 1,
                                    "quality": 1,
                                    "reencoding": 1,
                                    "users": 1,
                                    "_id": 0})

        if stream is None:
            raise tornado.web.HTTPError(500)

        if stream["user_id"] == self.get_current_user():
            stream["password"] = stream["users"][0]["password"]
        del stream["users"]

        user = yield motor.Op(self.db.users.find_one, {"_id": ObjectId(stream["user_id"])},
                                  {
                                      "name": 1,
                                      "email": 1,
                                      "picture": 1,
                                      "site": 1,
                                      "country": 1,
                                      "_id": 1})

        del stream["user_id"]
        user["id"] = unicode(user["_id"])
        del user["_id"]

        final_response = {}
        final_response["user"] = user
        final_response["stream"] = stream

        if stream["status"] == "ready":

            pipeline = yield motor.Op(self.db.servers.find_one,
                                      { "type": "pipeline", "level": {"$lte": 9}, "down": False},
                                      {"local_ip":1, "port":1}, sort=[('level', -1)])



            if pipeline is None:
                final_response["error"] = "Not enough Pipeline servers"
                self.write(final_response)
                self.finish()
            else:
                post_args = {
                    "stream": self.get_argument("streamId")
                }
                if stream["reencoding"]:
                    post_args["quality"] = self.get_argument("quality", None)
                if "quality" not in post_args:
                    post_args["quality"] = min(stream['quality'])
                if post_args["quality"] is None:
                    post_args["quality"] = min(stream['quality'])


                pr = PipelineRouter(self.db, unicode(self.get_argument("streamId")))
                url = pr.get_start_streaming_url(pipeline)

                response = yield tornado.gen.Task(pr.request, url=url, post_args=post_args)

                # try again
                if "error" in response:

                    if not (response["error"] == 'No such stream' and not stream['reencoding']):
                    # mark server as down
                        response = yield motor.Op(self.db.servers.update, {"_id":pipeline["_id"]}, {"$set":{"down": True}}, upsert=False, multi=False)

                    # try again with different server
                    pipeline = yield motor.Op(self.db.servers.find_one,
                                                  { "type": "pipeline", "level": {"$lte": 9}, "down": False},
                                                  {"local_ip":1, "port":1}, sort=[('level', -1)])


                if pipeline is None:
                    final_response["error"] = "Not enough Pipeline servers"
                    self.write(final_response)
                    self.finish()
                else:

                    if "error" in response:
                        response = yield tornado.gen.Task(pr.request, url=url, post_args=post_args)

                    final_response = dict(final_response.items() + response.items())

                    self.write(final_response)
                    self.finish()

        elif stream["status"] == "steady" or stream["status"] == "playing":

            query = {"type": "streaming", "streaming.streaming": True, "level": {"$lte": 9}, "down": False, "streaming.stream": self.get_argument("streamId")}
            if stream["reencoding"]:
                # print "QUALUTY "+unicode(float(self.get_argument("quality")))
                query["streaming.quality"] = self.get_argument("quality", None)

                if query["streaming.quality"] is None:
                    query["streaming.quality"] = min(stream['quality'])



            streaming_server = yield motor.Op(self.db.servers.find_one,
                                      query,
                                      {"public_ip":1, "port":1, "streaming.mount": 1}, sort=[('level', -1)])

            if streaming_server is None:

                pipeline = yield motor.Op(self.db.servers.find_one,
                                          { "_id": ObjectId(stream["pipeline_server"]) },
                                          {"local_ip":1, "port":1, "_id":0})

                post_args = {
                    "stream": self.get_argument("streamId")
                }
                if stream["reencoding"]:
                    post_args["quality"] = self.get_argument("quality", None)
                if "quality" not in post_args:
                    post_args["quality"] = min(stream['quality'])
                if post_args["quality"] is None:
                    post_args["quality"] = min(stream['quality'])


                pr = PipelineRouter(self.db, unicode(self.get_argument("streamId")))
                url = pr.get_scale_url(pipeline)

                response = yield tornado.gen.Task(pr.request, url=url, post_args=post_args, raw_result=True)

                if self.is_error(response):
                    yield motor.Op(self.db.streams.update, {"_id": ObjectId(self.get_argument("streamId"))},
                                                {"$set":{"status": "ready"}}, multi=True)

                    yield motor.Op(self.db.servers.update, {
                                                    "streaming.stream": (self.get_argument("streamId")),
                                                    "streaming.streaming": True},
                                                {"$set":{"streaming.streaming": False}}, multi=True)

                    #TODO
                    yield motor.Op(self.db.servers.update, {"_id":ObjectId(stream["pipeline_server"])},
                                   {"$set":{"down": True}}, upsert=False, multi=False)

                reset_state = False
                try:
                    if response.error:
                        response = {"error": "Error while connecting to backend"}
                    else:
                        response = json.loads(unicode(response.body))
                        if "error" in response and response["error"] == "No such stream":
                            reset_state = True
                except:
                    response = {"error": "Error while parsing response from backend"}

                if reset_state:
                    yield motor.Op(self.db.streams.update, {"_id": ObjectId(self.get_argument("streamId"))},
                                                   {"$set":{"status": "ready"}}, multi=True)

                final_response = dict(final_response.items() + response.items())

                self.write(final_response)
                self.finish()
            else:

                response = {
                    "public_ip": streaming_server["public_ip"],
                    "port": streaming_server["port"],
                    "mount": streaming_server["streaming"]["mount"],
                    }
                final_response = dict(final_response.items() + response.items())

                self.write(final_response)
                self.finish()


        else:
            final_response["error"] = "Unknown state of stream"
            self.write(final_response)
            self.finish()


    def is_error(self, response):
        try:
            if response.error:
                return True
            else:
                return False
        except:
            return True
        return False

