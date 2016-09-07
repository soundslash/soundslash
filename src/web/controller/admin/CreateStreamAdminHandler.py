__version__ = "0.2"

from helpers.genres import genres
import tornado.web
import tornado.gen
import motor
from controller.admin.AdminHandler import AdminHandler
import simplejson as json

class CreateStreamAdminHandler(AdminHandler):

    @tornado.web.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):

        self.template_vars["session_file_no"] = 0
        self.template_vars["current_user"] = self.current_user
        self.template_vars["genres"] = genres

        self.render("admin/create.html", **self.template_vars)
