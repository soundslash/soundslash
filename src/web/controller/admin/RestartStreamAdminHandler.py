
__version__ = "0.2"

import tornado.web
import tornado.gen
import motor
from bson.objectid import ObjectId
import simplejson as json

from controller.admin.AdminHandler import AdminHandler
from controller.PipelineRouter import PipelineRouter

class RestartStreamAdminHandler(AdminHandler):

    @tornado.web.authenticated
    @tornado.web.asynchronous
    @tornado.gen.engine
    def post(self, stream_id):


        yield motor.Op(self.db.streams.update,  {"_id":ObjectId(stream_id)},
                       {"$set":{"status": "ready"}}, multi=False)

        stream_obj = yield motor.Op(self.db.streams.find_one, {"_id":ObjectId(stream_id)},
                                    {"pipeline_server": 1, "quality": 1, "_id": 0})

        pr = PipelineRouter(self.db, stream_id)
        server = yield tornado.gen.Task(pr.get_server)

        if "error" in server or server is None:
            server = yield motor.Op(self.db.servers.find_one,
                                      { "type": "pipeline", "level": {"$lte": 9}, "down": False},
                                      {"local_ip":1, "port":1}, sort=[('level', -1)])
        url = pr.get_restart_url(server)

        post_args = {
            "stream": stream_id,
            "quality": min(stream_obj["quality"])
        }

        response = yield tornado.gen.Task(pr.request, url=url, post_args=post_args)

        self.write(response)
        self.finish()

