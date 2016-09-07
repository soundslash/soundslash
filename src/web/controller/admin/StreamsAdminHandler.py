
__version__ = "0.2"

import tornado.web
import tornado.gen
import motor
import datetime
from bson.son import SON

from controller.admin.AdminHandler import AdminHandler

class StreamsAdminHandler(AdminHandler):

    @tornado.web.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):

        streams = []


        servers = yield motor.Op(self.db.command,
                               SON([
                                   ("aggregate", "servers"),
                                   ("pipeline", [
                                       {"$match": {
                                           "streaming.streaming": True,
                                           "user_id": self.get_current_user()}},
                                       {"$project": {"_id": 0,
                                                     "stream": "$streaming.stream",
                                                     "listeners": "$streaming.listeners",}},
                                       {"$group": {
                                           "_id": {"stream": "$stream"},
                                           "listeners": {"$sum": "$listeners"}}},
                                       {"$sort": SON([("_id.year", 1), ("_id.month", 1), ("_id.day", 1)])},
                                       {"$project": {
                                           "_id": 0,
                                           "stream": "$_id.stream",
                                           "listeners": 1}}
                                       ])
                               ]))


        cursor = self.db.streams.find({"user_id": self.get_current_user(),
                                       "status": {"$ne": None}
                                      },
                                      {
                                          "_id": 1,
                                          "name": 1,
                                          "cover_image": 1,
                                          "status": 1,
                                          "size": 1,
                                          "max_size": 1,
                                          "reencoding": 1,
                                      }, sort=[("name", 1)])

        results = yield motor.Op(cursor.to_list, self.batch_size)



        or_streams = []
        for stream in results:
            or_streams.append({"stream_id": unicode(stream["_id"])})

        if len(or_streams) > 0:
            yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
            query = {
                "$or": or_streams,
                "year": yesterday.year,
                "month": yesterday.month,
                "day": yesterday.day,
                "hour": {"$exists": False}
                }
            stats = self.db.statistics.find(query, {"_id": 0, "stream_id": 1, "listeners": 1})
            stats = yield motor.Op(stats.to_list, self.batch_size)
        else:
            stats = []




        most_listened = []

        for stream in results:
            if "name" in stream:

                listeners = 0
                for server in servers["result"]:
                    if server["stream"] == unicode(stream["_id"]):
                        listeners = server["listeners"]

                listeners_yesterday = 0
                for stat in stats:
                    if "stream_id" in stat and stat["stream_id"] == unicode(stream["_id"]):
                        listeners_yesterday = stat["listeners"]

                most_listened.append((unicode(stream["_id"]), listeners_yesterday))

                if "cover_image" in stream:
                    cover = stream["cover_image"]
                else:
                    cover = None

                streams.append({
                    "id": unicode(stream["_id"]),
                    "name": stream["name"],
                    "cover_image": cover,
                    "size": stream["size"],
                    "max_size": stream["max_size"],
                    "reencoding": stream["reencoding"],
                    "listeners": listeners,
                    "listeners_yesterday": listeners_yesterday
                })

        now = datetime.datetime.now()
        month_before = datetime.datetime.now()
        month_before -= datetime.timedelta(days=28)
        while now.day != month_before.day:
            month_before -= datetime.timedelta(days=1)
        self.template_vars["last_month"] = unicode(month_before.day)+"."+unicode(month_before.month)+"."+unicode(month_before.year)
        self.template_vars["menu"] = "streams"
        self.template_vars["streams"] = streams

        most_listened = sorted(most_listened, key=lambda x: x[1], reverse=True)

        self.template_vars["most_listened"] = most_listened[:3]

        self.render("admin/streams.html", **self.template_vars)

