
__version__ = "0.2"

import tornado.web
import tornado.gen
import motor
from bson.objectid import ObjectId

from controller.BaseHandler import BaseHandler
from controller.admin.AdminHandler import AdminHandler
from controller.PipelineRouter import PipelineRouter

class TerminalAdminHandler(AdminHandler):

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self, stream_id):

        pr = PipelineRouter(self.db, stream_id)
        url = pr.get_terminal_url(
            {"local_ip": self.get_argument("local-ip"), "port": int(self.get_argument("port"))}
        )

        post_args = {
            "command": "use "+stream_id+";"+self.get_argument("command")
        }

        response = yield tornado.gen.Task(pr.request, url=url, post_args=post_args)

        self.write(response)
        self.finish()

    @tornado.web.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self, stream_id):


        stream = yield motor.Op(self.db.streams.find_one, {"_id": ObjectId(stream_id)},
                                {
                                    "name": 1,
                                    "reencoding": 1,
                                    "_id": 0,
                                    "pipeline_server": 1
                                    })

        if not "pipeline_server" in stream or stream["pipeline_server"] is None:
            pipeline = {"local_ip": "", "port": ""}
        else:
            pipeline = yield motor.Op(self.db.servers.find_one, {"_id": ObjectId(stream["pipeline_server"])},
                                  {"local_ip": 1, "port": 1, "_id": 0})

        self.template_vars["pipeline"] = pipeline
        self.template_vars["menu"] = "streams"
        self.template_vars["submenu"] = "terminal"
        self.template_vars["stream_id"] = stream_id
        self.template_vars["stream"] = stream

        self.render("admin/terminal.html", **self.template_vars)
