#!/usr/bin/env python

"""
Ear is handling messages coming from Icecast and updates database.
"""

import logging
# logging.basicConfig(level=logging.DEBUG)
from mongokit import *
import tornado.auth
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
from tornado.options import define, options
import xml.etree.ElementTree as ET
import urllib
# from Helpers.ip import local_ip
# from Helpers.ip import public_ip
import Helpers.ip
import motor
from tornado.options import define, options
from concurrent.futures import ThreadPoolExecutor
from functools import partial, wraps

from API.Auth.MountHandler import MountAddHandler
from API.Auth.MountHandler import MountRemoveHandler
from API.Auth.MountHandler import ListenerAddHandler
from API.Auth.MountHandler import ListenerRemoveHandler
from API.Auth.IcecastHandler import IcecastHandler
from API.Auth.Web import Web
from Framework.Application import Application
from Model.Db import Db
from Framework.Modules.PyMongoDriver import PyMongoDriver

__author__ = "Michal Bystricky"
__copyright__ = "Copyright 2013, Michal Bystricky"
__credits__ = ["Michal Bystricky", "Samuel Stehlik"]
__status__ = "Prototype"

def main():

    settings = {
        "unblock_workers": 0
    }
    Application(settings)
    PyMongoDriver(
        host="127.0.0.1",
        port=27017,
        user="pipeline",
        password="horcica7med#vajco1parky",
        database="pipeline").register()

    icecast = IcecastHandler()
    icecast.parse_icecastxml("/etc/icecast2/icecast.xml")
    icecast.update_from_icecast()
    icecast.register_streams(icecast.get_streams())

    web = Web(8888, icecast)
    web.run()

if __name__=="__main__":
    main()
