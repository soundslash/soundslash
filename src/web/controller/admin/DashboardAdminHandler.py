
__version__ = "0.2"

import tornado.web
import tornado.gen
import motor
from controller.admin.AdminHandler import AdminHandler

class DashboardAdminHandler(AdminHandler):

    @tornado.web.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        self.template_vars["menu"] = "dashboard"
        self.render("admin/dashboard.html", **self.template_vars)


class MainRedirectAdminHandler(AdminHandler):

    def get(self):

        self.redirect("/admin/streams.html")
