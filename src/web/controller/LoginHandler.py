
__version__ = "0.2"

import tornado.web
import tornado.gen
from tornado import gen
import hashlib, uuid
import re
import motor
import tornado.auth
import facebook
import functools
import tornado.httpclient
import random
from bson.objectid import ObjectId
import string

from controller.BaseHandler import BaseHandler
from controller.ThumbImage import ThumbImage
from helpers.countries import countries
from controller.EmailWrapper import EmailWrapper
from admin.AdminHandler import AdminHandler

EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")

class LoginHandler(AdminHandler):

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):

        confirm_key = self.get_argument('confirm-key', None)
        user_id = self.get_argument('user-id', None)
        confirmed = None
        try:
            if not confirm_key is None and not user_id is None:
                user = yield motor.Op(self.db.users.find_one, {"_id": ObjectId(user_id), "confirm_key": confirm_key},
                                      {"confirmed": 1,"_id":0, "waiting_email": 1})
                if user is not None:
                    if user["confirmed"]:
                        yield motor.Op(self.db.users.update, {"_id":ObjectId(user_id)},
                                       {"$set":{"confirmed":True, "email": user["waiting_email"]}},
                                       upsert=False, multi=False)
                    else:
                        yield motor.Op(self.db.users.update, {"_id":ObjectId(user_id)},
                                       {"$set":{"confirmed":True}}, upsert=False, multi=False)
                    confirmed = True
                else:
                    confirmed = False
        except:
            confirmed = False


        sign_up = self.get_argument('sign-up', '')
        self.template_vars["sign_up"] = sign_up
        self.template_vars["confirmed"] = confirmed
        self.template_vars["session"] = self.get_argument('session', None)

        self.render("admin/login.html", **self.template_vars)

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self):
        email = self.get_argument('email', '')
        password = self.get_argument('password', '')

        response = yield motor.Op(self.db.users.find_one, {"email": email},
                                  {"password": 1, "salt": 1, "confirmed": 1, "_id": 1})

        if not response:
            login_response = {
                'error': True,
                'msg': 'User doesn\'t exist.'
            }
        elif not response["confirmed"]:
            login_response = {
                'error': True,
                'msg': 'Account is not confirmed.'
            }
        else:
            hashed_password = hashlib.sha512(password + response["salt"]).hexdigest()
            if response["password"] == hashed_password:

                yield self.new_session(unicode(response["_id"]))

                login_response = {
                    "user": unicode(response["_id"]),
                    "email": email
                }

            else:
                login_response = {
                    'error': True,
                    'msg': 'Incorrect password.'
                }

        self.write(login_response)
        self.finish()


class FBLoginHandler(BaseHandler, tornado.auth.FacebookGraphMixin):


    @tornado.web.asynchronous
    @tornado.gen.engine
    def post(self):

        cookies = dict((n, self.cookies[n].value) for n in self.cookies.keys())

        cookie = yield gen.Task(self.unblock, function=self.get_user_from_cookie,
                       parameters={
                           "cookies": cookies,
                           "facebook_api_key": self.settings["facebook_api_key"],
                           "facebook_secret": self.settings["facebook_secret"]
                       })

        def get_graph(cookie):
            return facebook.GraphAPI(cookie["access_token"])
        graph = yield gen.Task(self.unblock, function=get_graph, parameters={"cookie":cookie})

        def get_profile(graph):
            return graph.get_object("me",
                                    fields="id,username,name,first_name,last_name,email,picture.width(9999).height(9999)")
        profile = yield gen.Task(self.unblock, function=get_profile, parameters={"graph":graph})


        if "email" in profile:

            response = yield motor.Op(self.db.users.find_one, {"email": profile["email"]}, {"_id": 1})
            if not (not response):
                # user exists

                yield self.new_session(unicode(response["_id"]))
                self.write({"user_id": unicode(response["_id"])})
                self.finish()

            else:
                # Download profile picture
                url = profile["picture"]["data"]["url"]
                tornado.httpclient.AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient")
                http_client = tornado.httpclient.AsyncHTTPClient()
                req = tornado.httpclient.HTTPRequest(url, method="GET")
                cb = functools.partial(self.on_image, profile = profile)
                http_client.fetch(req, callback = cb)
                # yield tornado.gen.Task(http_client.fetch, req, callback = cb)


        else:
            login_response = {"error": "Something went wrong"}
            self.write(login_response)
            self.finish()

    def get_user_from_cookie(self, cookies, facebook_api_key, facebook_secret):

        cookie = facebook.get_user_from_cookie(
            cookies, facebook_api_key, facebook_secret)

        return cookie


    @tornado.web.asynchronous
    @tornado.gen.engine
    def on_image(self, response, profile):

        ti = ThumbImage()
        img = ti.process(response.body,
                               format="binary>binary",
                               tags=["profile"],
                               attrs={"random": random.uniform(0,1)},
                               template="profile")


        image_id = yield motor.Op(self.db.images.insert, img)

        user = {
            "email": profile["email"],
            "fb_id": profile["id"],
            "fb_username": profile["username"],
            "fb_first_name": profile["first_name"],
            "fb_last_name": profile["last_name"],
            "fb_name": profile["name"],
            "name": profile["name"],
            "picture": unicode(image_id),
            "size": 0,
            "max_size": 50000000,
            "confirmed": True,
            "random": random.uniform(0,1),
            "privileges": []
        }


        user_id = yield motor.Op(self.db.users.insert, user)

        yield motor.Op(self.db.images.update, {"_id":ObjectId(image_id)},
                       {"$set":{"user_id":unicode(user_id)}}, upsert=False, multi=False)

        yield self.new_session(unicode(user_id))
        self.write({"user_id": unicode(user_id)})
        self.finish()




class LogoutHandler(BaseHandler):

    @tornado.gen.coroutine
    def get(self):
        yield self.destroy_session()
        self.write({})
        self.finish()

class SignupHandler(BaseHandler):

    def get(self):
        self.clear_cookie("profile_picture")
        self.render("sign_up.html", countries=countries)

    @tornado.web.asynchronous
    @tornado.gen.engine
    def post(self):
        email = self.get_argument('s_email', '')
        response = yield motor.Op(self.db.users.find_one, {"email": email}, {"_id": 1})

        password = self.get_argument('s_password', '')
        password_check = self.get_argument('s_password_check', '')

        # profile_picture_id = self.get_cookie('profile_picture')
        # profile_picture = yield motor.Op(self.db.images.find_one, {"_id":ObjectId(profile_picture_id)}, {})

        country = self.get_argument('s_country', '')
        name = self.get_argument('s_name', '')
        site = self.get_argument('s_site', '')
        if not site:
            site = "Unknown"

        countries["Unknown"] = "Unknown"

        if not email:
            sign_up_response = {
                'error': True,
                'msg': 'Please enter your email address.'
            }
        # elif not name:
        #     sign_up_response = {
        #         'error': True,
        #         'msg': 'Please enter your name.'
        #     }
        # elif not country:
        #     sign_up_response = {
        #         'error': True,
        #         'msg': 'Please select your country.'
        #     }
        # elif country not in countries.values():
        #     sign_up_response = {
        #         'error': True,
        #         'msg': 'Please select your country from list of countries.'
        #     }
        elif not EMAIL_REGEX.match(email):
            sign_up_response = {
                'error': True,
                'msg': 'The email address is invalid.'
            }
        # elif profile_picture is None:
        #     sign_up_response = {
        #         'error': True,
        #         'msg': 'Please upload profile picture.'
        #     }
        elif not password or not password_check or password != password_check:
            sign_up_response = {
                'error': True,
                'msg': 'The passwords do not match.'
            }
        elif len(password) < 5:
            sign_up_response = {
                'error': True,
                'msg': 'The password is the wrong length. Minimum 6 characters.'
            }
        elif not (not response):
            sign_up_response = {
                'error': True,
                'msg': 'User exists.'
            }
        else:

            salt = uuid.uuid4().hex
            hashed_password = hashlib.sha512(password + salt).hexdigest()
            confirm_key = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(32))
            user = {
                "email": email,
                "salt": salt,
                "password": hashed_password,
                "size": 0,
                "max_size": 50000000,
                "max_streams": 1,
                "name": name,
                "country": country,
                # "picture": profile_picture_id,
                "site": site,
                "confirm_key": confirm_key,
                "confirmed": False,
                "random": random.uniform(0,1),
                "privileges": []
            }

            user_id = yield motor.Op(self.db.users.insert, user)

            # yield motor.Op(self.db.images.update, {"_id":ObjectId(profile_picture_id)},
            #                           {"$set":{"tags": "profile"}}, upsert=False, multi=False)


            new_email = EmailWrapper()
            new_email.set_subject("Confirm your SoundSlash.com account")
            new_email.set_sender("noreply@soundslash.com")
            new_email.add_recipient(email)
            new_email.set_body("email/index.html", args = {
                "name":name,
                "email": email,
                "password":password,
                "key": confirm_key,
                "user_id": user_id
            })

            yield gen.Task(self.unblock, function=new_email.send, parameters={})

            yield self.new_session(unicode(user_id))

            sign_up_response = {
                'user': unicode(user_id),
                'error': False
            }

        self.write(sign_up_response)
        self.finish()



class TermsHandler(BaseHandler):

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        self.render("terms.html")