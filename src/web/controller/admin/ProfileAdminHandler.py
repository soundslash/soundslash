
__version__ = "0.2"

import tornado.web
import tornado.gen
from tornado import gen
import hashlib, uuid
import motor
import tornado.auth
import facebook
import tornado.httpclient
import random
from bson.objectid import ObjectId
import string

from controller.admin.AdminHandler import AdminHandler
from helpers.countries import countries
from controller.EmailWrapper import EmailWrapper
from controller.LoginHandler import EMAIL_REGEX

class UserSettingsAdminHandler(AdminHandler):

    @tornado.web.authenticated
    @tornado.gen.coroutine
    def post(self):

        update = {
            "max_size": int(self.get_argument('max-size'))*1048576,
            "max_streams": int(self.get_argument('max-streams'))
        }

        confirmed = self.get_argument("confirmed", False)
        if confirmed == "on": confirmed = True
        else: confirmed = False
        update["confirmed"] = confirmed

        yield motor.Op(self.db.users.update, { "_id": ObjectId(self.get_current_user()) },
                                      { "$set": update
                                             }, upsert=False, multi=False)


        if self.get_argument("remove") == "1":
            yield motor.Op(self.db.users.remove, { "_id": ObjectId(self.get_current_user()) })

            stream = yield motor.Op(self.db.streams.find_one, {"user_id": self.get_current_user()}, {"_id": 1})
            if stream is not None:
                stream_id = unicode(stream["_id"])
                yield motor.Op(self.db.streams.remove, { "user_id": self.get_current_user() })
                yield motor.Op(self.db.media.remove, { "stream_id": stream_id })
                self.redirect("/admin/user/me/log-as.html")


        self.write({"msg": "User settings updated successfully."})
        self.finish()

class ChangePasswordAdminHandler(AdminHandler):

    @tornado.web.authenticated
    @tornado.gen.coroutine
    def post(self):

        password = self.get_argument('s_password', '')
        password_check = self.get_argument('s_password_check', '')

        if not password or not password_check or password != password_check:
            response = {
                'error': True,
                'msg': 'The passwords do not match.'
            }
        elif len(password) < 5:
            response = {
                'error': True,
                'msg': 'The password is the wrong length. Minimum 6 characters.'
            }
        else:
            update_user = self.get_current_user()

            salt = uuid.uuid4().hex
            hashed_password = hashlib.sha512(password + salt).hexdigest()

            update = {
                "password": hashed_password,
                "salt": salt,
                }

            yield motor.Op(self.db.users.update, { "_id": ObjectId(update_user) },
                                      { "$set": update }, upsert=False, multi=False)

            response = {
                'msg': 'Password changed successfully.'
            }

        self.write(response)
        self.finish()



class ProfileAdminHandler(AdminHandler):

    @tornado.web.authenticated
    @tornado.gen.coroutine
    def get(self):

        self.template_vars["user"] = yield motor.Op(self.db.users.find_one,
                                                    {"_id": ObjectId(self.get_current_user())},
                                                    {
                                                        "email": 1,
                                                        "name": 1,
                                                         "picture": 1,
                                                         "site": 1,
                                                         "confirmed": 1,
                                                         "country": 1,
                                                         "max_size": 1,
                                                         "max_streams": 1,
                                                         "_id": 0})

        if "picture" not in self.template_vars["user"]: self.template_vars["user"]["picture"] = None

        self.clear_cookie("profile_picture")


        self.template_vars["countries"] = countries
        self.template_vars["menu"] = "profile"

        self.render("admin/profile.html", **self.template_vars)

    @tornado.web.authenticated
    @tornado.gen.coroutine
    def post(self):

        email = self.get_argument('s_email', '')

        profile_picture_id = self.get_argument('picture', None)

        country = self.get_argument('s_country', '')
        name = self.get_argument('s_name', '')
        site = self.get_argument('s_site', '')


        if country in countries.values(): exists_country = True
        elif country == "Unknown": exists_country = True
        else: exists_country = False


        if not email:
            response = {
                'error': True,
                'msg': 'Please enter your email address.'
            }
        elif not name:
            response = {
                'error': True,
                'msg': 'Please enter your name.'
            }
        elif not country:
            response = {
                'error': True,
                'msg': 'Please select your country.'
            }
        elif not exists_country:
            response = {
                'error': True,
                'msg': 'Please select your country from list of countries.'
            }
        elif not EMAIL_REGEX.match(email):
            response = {
                'error': True,
                'msg': 'The email address is invalid.'
            }
        else:

            update_user = self.get_current_user()

            user = yield motor.Op(self.db.users.find_one, {"_id": ObjectId(update_user)}, {"_id": 0, "email": 1})

            update = {
                "name": name,
                }

            confirm_key = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(32))

            if user["email"] != email:
                update["waiting_email"] = email
                update["confirm_key"] = confirm_key

                new_email = EmailWrapper()
                new_email.set_subject("Confirm your new email address at SoundSlash.com")
                new_email.set_sender("noreply@soundslash.com")
                new_email.add_recipient(email)
                new_email.set_body("email/change_email.html", args = {
                    "name":name,
                    "key": confirm_key,
                    "user_id": update_user
                })
                yield gen.Task(self.unblock, function=new_email.send, parameters={})


            if profile_picture_id is not None:
                update["picture"] = profile_picture_id
                yield motor.Op(self.db.images.update, {"_id":ObjectId(profile_picture_id)},
                                          {"$set":{"tags": "profile"}}, upsert=False, multi=False)

            if country is not None:
                update["country"] = country

            if site is not None:
                update["site"] = site


            yield motor.Op(self.db.users.update, { "_id": ObjectId(update_user) },
                                      { "$set": update }, upsert=False, multi=False)


            response = {
                'msg': 'Profile informations successfully saved.'
            }

        self.write(response)
        self.finish()