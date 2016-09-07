#!/usr/bin/env python
import os, pwd, grp, sys
import os.path
import tornado.escape
import tornado.web
import tornado.wsgi
import tornado.gen
import motor
from pymongo import MongoClient
import gridfs
import ui_methods
from multiprocessing import Process
from multiprocessing import Pipe
from multiprocessing.synchronize import BoundedSemaphore
from tornado.options import define, options
from concurrent.futures import ThreadPoolExecutor
from functools import partial, wraps
import tornado.ioloop
import tornado.web

# from controller.BaseHandler import BaseHandler
from controller.MainHandler import MainHandler
from controller.MainHandler import ListenHandler
from controller.MainHandler import GenresHandler
from controller.MainHandler import SearchHandler
from controller.MainHandler import RadioHandler
from controller.MainHandler import SettingsHandler
from controller.MainHandler import MainRedirectHandler
from controller.MainHandler import RandomUsersHandler
from controller.MainHandler import UserProfileHandler
from controller.MainHandler import StreamGenresHandler


from controller.LiveHandler import LiveHandler
from controller.LiveHandler import LiveForwarderHandler
from controller.LiveHandler import UpdatesForwarderHandler

from controller.DatabaseHandler import DatabaseHandler
from controller.DatabaseHandler import SearchDatabaseHandler
from controller.DatabaseHandler import PlaylistDatabaseHandler

from controller.AboutHandler import AboutStreamHandler
from controller.ProfilePictureHandler import StreamPictureHandler
from controller.UploadHandler import MetaHandler


from controller.StatisticsHandler import StatisticsHandler
from controller.StatisticsHandler import ListenersStatisticsHandler
from controller.StatisticsHandler import TagsHandler

from controller.ProgramHandler import ProgramHandler

from controller.LoginHandler import LoginHandler
from controller.LoginHandler import FBLoginHandler
from controller.LoginHandler import LogoutHandler
from controller.LoginHandler import SignupHandler
from controller.LoginHandler import TermsHandler
from controller.UploadHandler import UploadHandler
from controller.UploadHandler import ValidatorHandler
from controller.CreateHandler import CreateHandler
from controller.CreateHandler import CoverHandler
from controller.CreateHandler import UploadCoverHandler
from controller.UploadHandler import StatusHandler
from controller.PlayHandler import PlayHandler
from controller.PlayHandler import RandomPlayHandler
from controller.FacebookHandler import ChannelHandler
from controller.ImageHandler import JSONImageHandler
from controller.ImageHandler import JPGImageHandler
from controller.UploadProcessor import UploadProcessor
from controller.ProfilePictureHandler import ProfilePictureHandler
from controller.MediaHandler import MediaHandler

from controller.admin.DashboardAdminHandler import DashboardAdminHandler
from controller.admin.DashboardAdminHandler import MainRedirectAdminHandler
from controller.admin.StreamsAdminHandler import StreamsAdminHandler
from controller.admin.RestartStreamAdminHandler import RestartStreamAdminHandler
from controller.admin.UsersAdminHandler import UsersAdminHandler
from controller.admin.UsersAdminHandler import SearchUsersAdminHandler
from controller.admin.UsersAdminHandler import LogAsUserAdminHandler
from controller.admin.UsersAdminHandler import LogAsMeAdminHandler
from controller.admin.LiveAdminHandler import LiveAdminHandler
from controller.admin.LiveAdminHandler import LiveForwarderAdminHandler
from controller.admin.LiveAdminHandler import UpdatesForwarderAdminHandler
from controller.admin.ProfileAdminHandler import ProfileAdminHandler
from controller.admin.ProfileAdminHandler import ChangePasswordAdminHandler
from controller.admin.ProfileAdminHandler import UserSettingsAdminHandler
from controller.admin.DatabaseAdminHandler import DatabaseAdminHandler
from controller.admin.DatabaseAdminHandler import SearchDatabaseAdminHandler
from controller.admin.AboutStreamAdminHandler import AboutStreamAdminHandler
from controller.admin.AppearanceAdminHandler import AppearanceAdminHandler
from controller.admin.AppearanceAdminHandler import CoverPictureAdminHandler
from controller.admin.CreateStreamAdminHandler import CreateStreamAdminHandler
from controller.admin.StatisticsAdminHandler import ListenersStatisticsAdminHandler
from controller.admin.StatisticsAdminHandler import StatisticsAdminHandler
from controller.admin.TerminalAdminHandler import TerminalAdminHandler

def drop_privileges(uid_name='nobody', gid_name='nogroup'):
    if os.getuid() != 0:
        # We're not root so, like, whatever dude
        return

    # Get the uid/gid from the name
    running_uid = pwd.getpwnam(uid_name).pw_uid
    running_gid = grp.getgrnam(gid_name).gr_gid

    # Remove group privileges
    os.setgroups([])

    # Try setting the new uid/gid
    os.setgid(running_gid)
    os.setuid(running_uid)

    # Ensure a very conservative umask
    old_umask = os.umask(077)

def upload_processor_wrapper(conn):
    os.nice(19)
    #drop_privileges("dash", "users")
    syncdb = MongoClient(host='mongodb://pipeline:horcica7med#vajco1parky@127.0.0.1:27017/pipeline').pipeline
    upload_processor = UploadProcessor(syncdb)
    upload_processor.start()
    while True:
        file = conn.recv()
        upload_processor.cv.acquire()
        upload_processor.queue.append(file)
        upload_processor.cv.notify()
        upload_processor.cv.release()

if __name__ == "__main__":

    parent_conn, child_conn = Pipe()
    p = Process(target=upload_processor_wrapper, args=(child_conn,))
    p.start()

    #drop_privileges("dash", "users")

    settings = {
        "title": u"SoundSlash",
        "template_path": os.path.join(os.path.dirname(__file__), "templates"),
        "xsrf_cookies": False,
        "static_path": os.path.join(os.path.dirname(__file__), "static"),
        "ui_methods": ui_methods,
        "cookie_secret": str("__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__"),
        "login_url": "/admin/login.html",
        "debug": True,
        "db": motor.MotorClient("mongodb://pipeline:horcica7med#vajco1parky@127.0.0.1:27017/pipeline").pipeline,
        "upload_processor": {
            "connection": parent_conn,
            "lock": BoundedSemaphore(value=1)
        },
        "facebook_api_key": "..",
        "facebook_secret": "..",
        "executor": ThreadPoolExecutor(max_workers=4),
        # websockets connection cache for receiving metadata and live
        "ws_cache": {}
    }

    application = tornado.web.Application([

                                              (r"/image.json", JSONImageHandler),
                                              (r"/image.jpg", JPGImageHandler),

                                              (r"/", MainHandler),
                                              (r"/login.json", LoginHandler),
                                              (r"/logout.json", LogoutHandler),
                                              (r"/logout.html", LogoutHandler),
                                              (r"/terms.html", TermsHandler),
                                              (r"/listen.json", ListenHandler),
                                              (r"/search.json", SearchHandler),
                                              (r"/genres.json", GenresHandler),
                                              (r"/radio.json", RadioHandler),
                                              (r"/validate.json", ValidatorHandler),
                                              (r"/profile.json", UserProfileHandler),

                                              (r"/stream/live.json", LiveHandler),
                                              (r"/ws/stream/updates.json", UpdatesForwarderAdminHandler),

                                              (r"/ws/stream/live/data.json", LiveForwarderHandler),
                                              (r"/ws/stream/live/updates.json", UpdatesForwarderHandler),
                                              (r"/stream/database.json", DatabaseHandler),
                                              (r"/stream/database/search.json", SearchDatabaseHandler),
                                              (r"/stream/database/playlist.json", PlaylistDatabaseHandler),
                                              (r"/stream/about.json", AboutStreamHandler),
                                              (r"/stream/picture.json", StreamPictureHandler),
                                              (r"/stream/bg-picture.json", StreamPictureHandler),
                                              (r"/stream/program.json", ProgramHandler),

                                              (r"/sign-up.json", SignupHandler),
                                              (r"/meta.json", MetaHandler),

                                              (r"/stream-genres.html", StreamGenresHandler),

                                              (r"/stream/statistics.json", StatisticsHandler),
                                              (r"/stream/tags.json", TagsHandler),
                                              (r"/statistics/listeners.json", ListenersStatisticsHandler),


                                              (r"/settings.json", SettingsHandler),

                                              (r"/fb-login.json", FBLoginHandler),
                                              (r"/channel.html", ChannelHandler),


                                              (r"/admin/login.html", LoginHandler),

                                              (r"/profile-picture.json", ProfilePictureHandler),
                                              (r"/upload.json", UploadHandler),
                                              (r"/create.json", CreateHandler),
                                              (r"/upload-cover.html", UploadCoverHandler),
                                              (r"/status.json", StatusHandler),
                                              (r"/play.json", PlayHandler),
                                              (r"/random-play.json", RandomPlayHandler),



                                              (r"/media/([a-zA-Z0-9]+).ogg", MediaHandler),


                                              (r"/admin/", MainRedirectAdminHandler),

                                              (r"/admin/streams.html", StreamsAdminHandler),
                                              (r"/admin/users.html", UsersAdminHandler),
                                              (r"/admin/users/search.json", SearchUsersAdminHandler),
                                              (r"/admin/user/me/log-as.html", LogAsMeAdminHandler),
                                              (r"/admin/user/([a-zA-Z0-9]+)/log-as.html", LogAsUserAdminHandler),
                                              (r"/admin/profile.html", ProfileAdminHandler),
                                              (r"/admin/change-password.json", ChangePasswordAdminHandler),
                                              (r"/admin/user-settings.json", UserSettingsAdminHandler),

                                              (r"/admin/stream/([a-zA-Z0-9]+)/about.html", AboutStreamAdminHandler),
                                              (r"/admin/stream/([a-zA-Z0-9]+)/restart.json", RestartStreamAdminHandler),
                                              (r"/admin/stream/([a-zA-Z0-9]+)/terminal.html", TerminalAdminHandler),

                                              (r"/admin/statistics/listeners.json", ListenersStatisticsAdminHandler),


                                              ], **settings)

    print("Starting server at port "+str(sys.argv[1]))
    application.listen(sys.argv[1])
    tornado.ioloop.IOLoop.instance().start()
