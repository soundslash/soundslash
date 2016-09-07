#!/usr/bin/env python

"""
Main method initializes Workers.
"""

import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s: %(levelname)s: %(message)s')
from mongokit import *
from concurrent.futures import ThreadPoolExecutor
import motor
from pymongo import MongoClient


from Framework.Worker import Worker
from Terminal import Terminal
from Context.StreamManagement import StreamManagement
from API.Pipeline.Web import Web
import Helpers.globals
from Framework.PriorityQueue import PriorityQueue
from Framework.Application import Application
from Framework.Modules.PyMongoDriver import PyMongoDriver
from Framework.Test.Context.FrameworkTest import FrameworkTest
from Framework.Test.Context.FrameworkTest import FrameworkTestThread

__author__ = "Michal Bystricky"
__copyright__ = "Copyright 2013, Michal Bystricky"
__credits__ = ["Michal Bystricky", "Samuel Stehlik"]
__status__ = "Prototype"

WORKERS = 2

def main():

    queue = PriorityQueue()

    for x in range(WORKERS):
        w = Worker(queue)
        w.start()

    settings = {
        "unblock_workers": 5
    }
    Application(settings)
    PyMongoDriver(
        host="127.0.0.1",
        port=27017,
        user="pipeline",
        password="horcica7med#vajco1parky",
        database="pipeline").register()

    test = False
    if test:
        FrameworkTest().run()
        # FrameworkTestThread().start()

    else:

        port = 9999

        StreamManagement(port)

        web_api = Web(port)
        web_api.start()

        Terminal().start()

if __name__=="__main__":
    main()
