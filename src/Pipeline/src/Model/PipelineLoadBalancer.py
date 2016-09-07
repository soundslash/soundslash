#!/usr/bin/env python

"""
PipelineLoadBalancer detects CPU changes and updates database in order to another instances could safely send their tasks to another Pipeline.
"""

import time
from bson.objectid import ObjectId
import psutil
from threading import Thread

from Framework.Base import *
from Model.BaseThreaded import BaseThreaded
from Model.Db import Db

__author__ = "Michal Bystricky"
__copyright__ = "Copyright 2013, Michal Bystricky"
__credits__ = ["Michal Bystricky", "Samuel Stehlik"]
__status__ = "Prototype"

class PipelineLoadBalancer(Base, Thread):

    def __init__(self, pipeline_server_id):
        super(PipelineLoadBalancer, self).__init__()

        self.cpu_history = []
        # self.db = Db()
        self.pipeline_id = pipeline_server_id
        self.stopped = False

    def run(self):

        sum = 0
        count = 0
        append = True
        last_level = 0

        sleep = 1
        until = 5

        while not self.stopped:

            current_cpu = psutil.cpu_percent()

            if count >= until:
                avg = float(sum)/float(count)
                # print str(avg)
                if abs(avg - current_cpu) > 20 or current_cpu > 70:
                    append = True
                else:
                    append = False

                level = avg/10
                if level >= 8:
                    level = float(10.0)
                level_change = abs(level-last_level)
                if level_change >= 1.5:
                    last_level = level
                    self.db.servers.update({"_id": ObjectId(self.pipeline_id)},
                                           {"$set":{"level": level}}, multi=False)


            if append:

                if count >= until:
                    cpu = self.cpu_history.pop(0)
                    sum -= cpu
                else:
                    count += 1

                self.cpu_history.append(current_cpu)
                sum += current_cpu

            time.sleep(sleep)
