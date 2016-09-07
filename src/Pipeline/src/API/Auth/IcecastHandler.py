
#!/usr/bin/env python

"""
Handle mount/listener add/remove.
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
import Helpers.ip
import motor
import urlparse
from bson.objectid import ObjectId
from tornado.options import define, options
import time
import simplejson as json
import datetime

from Model.Server import Server
from Helpers.level import get_level
from Helpers.level import round_max_listeners
from Model.Db import Db
from Framework.Base import *

__author__ = "Michal Bystricky"
__copyright__ = "Copyright 2013, Michal Bystricky"
__status__ = "Prototype"

class IcecastHandler(Base):

    def __init__(self):
        super(IcecastHandler, self).__init__()
        self.streams = []

    def parse_icecastxml(self, filename):

        tree = ET.parse(filename)
        root = tree.getroot()
        # host = root.findall("./listen-socket/bind-address")[0].text
        local_ip = Helpers.ip.local_ip()
        public_ip = Helpers.ip.public_ip()
        port = int(root.findall("./listen-socket/port")[0].text)
        mounts = root.findall("./mount")
        streams = {}
        for mount in mounts:
            max_listeners = -1
            for child in mount:
                if child.tag == "mount-name":
                    mount_name = child.text
                if child.tag == "password":
                    password = child.text
                if child.tag == "max-listeners":
                    max_listeners = int(child.text)

            streams[mount_name] = {}
            streams[mount_name]["password"] = password
            if max_listeners == -1:
                streams[mount_name]["max_listeners"] = round_max_listeners(int(root.findall("./limits/clients")[0].text))
            else:
                streams[mount_name]["max_listeners"] = round_max_listeners(max_listeners)
            streams[mount_name]["listeners"] = 0
            streams[mount_name]["listeners_last_updated"] = time.time()
            streams[mount_name]["level"] = float(0)
            streams[mount_name]["local_ip"] = local_ip
            streams[mount_name]["public_ip"] = public_ip
            streams[mount_name]["port"] = port
            streams[mount_name]["streaming"] = False
            streams[mount_name]["down"] = False

        self.streams = streams
        return self.streams

    def register_streams(self, streams):
        for (mount, attrs) in streams.items():
            self.update_stream(mount, attrs, streams[mount])
        return streams

    def update_stream(self, mount, attrs, update):


        update = {
            "type": "streaming",
            "streaming.mount": mount,
            "streaming.password": update["password"],
            "streaming.max_listeners": update["max_listeners"],
            "streaming.listeners": update["listeners"],
            "streaming.streaming": update["streaming"],
            "level": update["level"],
            "local_ip": update["local_ip"],
            "public_ip": update["public_ip"],
            "port": update["port"],
            "down": update["down"]
        }

        self.db.servers.update({
                                   "type": "streaming",
                                   "local_ip": attrs["local_ip"],
                                   "port": attrs["port"],
                                   "streaming.mount": mount
                               },
                               {"$set": update},
                               upsert=True, multi=False)

        return True

    def update_from_icecast(self):
        try:
            stream = self.streams.itervalues().next()
            file = urllib.urlopen('http://'+stream["local_ip"]+":"+unicode(stream["port"])+"/listeners.xsl")
            data = file.readlines()
            if len(data) != 2:
                return self.streams
            data = data[1].lstrip().rstrip().split(";")
            data.pop()
            for stream_info in data:
                stream_name, listeners = stream_info.split("=")
                self.streams[stream_name]["listeners"] = int(listeners)
                self.streams[stream_name]["level"] = get_level(self.streams[stream_name]["listeners"], self.streams[stream_name]["max_listeners"])
                self.streams[stream_name]["streaming"] = True
        except:
            return self.streams
        return self.streams

        # self.config.currListeners = [datetime.now().strftime("%Y-%m-%d %H:%M:%S"), data]

    def get_streams(self):
        return self.streams
