
__version__ = "0.2"

import tornado.web
import tornado.gen
import motor

from controller.admin.AdminHandler import AdminHandler


class SearchUsersAdminHandler(AdminHandler):

    @tornado.web.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self):

        search = self.get_argument("search")

        page_user = self.get_argument("page", 1)
        page = int(page_user)-1
        per_page = 10
        skip = int(page*per_page)

        query = {"$or": [{
            "name": {'$regex': search}
        },{
            "email": {'$regex': search}
        }]}
        # query["confirmed"] = True

        cursor = self.db.users.find(query, {
                                              "_id": 1,
                                              "name": 1,
                                              "email": 1,
                                              "confirmed": 1,
                                              "size": 1,
                                              "max_size": 1,
        }, limit=per_page, skip=skip)


        results = yield motor.Op(cursor.to_list, self.batch_size)

        for i in range(len(results)):
            results[i]["_id"] = unicode(results[i]["_id"])
            results[i]["free_mb"] = round(float(results[i]["max_size"]-results[i]["size"])/1048576, 2)

        if int(page_user) == 1:
            first_page = True
        else:
            first_page = False

        if len(results) < per_page:
            last_page = True
        else:
            last_page = False

        self.write({"results": results, "page": page_user, "first_page": first_page, "last_page": last_page})
        self.finish()




class UsersAdminHandler(AdminHandler):

    @tornado.web.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):

        if not self.is_allowed("admin"):
            self.redirect("/admin/")


        self.template_vars["menu"] = "users"

        self.render("admin/users.html", **self.template_vars)

class LogAsUserAdminHandler(AdminHandler):

    @tornado.web.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self, user_id):

        if not self.is_allowed("admin"):
            self.redirect("/admin/")

        yield self.new_session(unicode(user_id), self.get_current_user())

        self.redirect("/admin/")


class LogAsMeAdminHandler(AdminHandler):

    @tornado.web.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):

        session = yield motor.Op(self.db.sessions.find_one,
                                 {"user_id": self.get_current_user(), "session_id": self.get_current_session()},
                                 {"logged_as": 1, "_id": 0})

        if session["logged_as"] is not None:
            yield self.new_session(session["logged_as"])

        self.redirect("/admin/users.html")

