
__version__ = "0.2"

from controller.BaseHandler import BaseHandler
import tornado.web
import tornado.gen
import motor
from bson.objectid import ObjectId

class AdminHandler(BaseHandler):

    @tornado.gen.coroutine
    def prepare(self):
        yield super(AdminHandler, self).prepare()
        user = yield motor.Op(self.db.users.find_one, {"_id": ObjectId(self.get_current_user())},
                              {"name": 1, "picture": 1, "privileges": 1, "_id": 0})
        if user is not None and "picture" not in user: user["picture"] = None
        self.template_vars["user"] = user

        if hasattr(self, "session") and self.session is not None \
            and "logged_as" in self.session and self.session["logged_as"] is not None:

            user = yield motor.Op(self.db.users.find_one, {"_id": ObjectId(self.session["logged_as"])},
                                  {"privileges": 1, "name": 1, "_id": 0})
            self.privileges = user["privileges"]
            self.template_vars["logged_as"] = user["name"]
        else:
            if user is not None and "privileges" in user:
                self.privileges = user["privileges"]
            else:
                self.privileges = []

        self.template_vars["is_allowed"] = self.is_allowed

    def is_allowed(self, privilege):
        if privilege in self.privileges:
            return True
        else:
            return False
