
__version__ = "0.2"

import tornado.web
import tornado.gen
import motor
import datetime

from controller.BaseHandler import BaseHandler

class ChannelHandler(BaseHandler):

    def get(self):
        seconds_to_cache = 60*60*24*365
        expires = (datetime.datetime.today()+datetime.timedelta(seconds=seconds_to_cache)).strftime('%a, %d %b %Y %H:%M:%S %Z')
        self.set_header("Expires", expires)
        self.set_header("Pragma", "cache")
        self.set_header("Cache-Control", "max-age="+unicode(seconds_to_cache))
        self.write("<script src=\"//connect.facebook.net/en_US/all.js\"></script>")
