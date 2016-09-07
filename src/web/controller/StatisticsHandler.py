
__version__ = "0.2"

import tornado.web
import tornado.gen
import motor
from bson.objectid import ObjectId
import datetime
from bson.son import SON
import calendar

from controller.admin.AdminHandler import AdminHandler


class StatisticsHandler(AdminHandler):
    @tornado.web.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):

        stream_id = self.get_argument("stream_id")

        stream = yield motor.Op(self.db.streams.find_one, {"_id": ObjectId(stream_id)},
                                {
                                    "name": 1,
                                    "reencoding": 1,
                                    "_id": 0,
                                    })

        now = datetime.datetime.now()
        month_before = datetime.datetime.now()
        month_before -= datetime.timedelta(days=28)
        while now.day != month_before.day:
            month_before -= datetime.timedelta(days=1)

        self.write({
            "last_month": unicode(month_before.day)+"."+unicode(month_before.month)+"."+unicode(month_before.year),
            "stream": stream,
            "stream_id": stream_id
        })
        self.finish()

class TagsHandler(AdminHandler):

    @tornado.web.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):

        stream_id = self.get_argument("stream_id")

        stream = yield motor.Op(self.db.streams.find_one, {"_id": ObjectId(stream_id)},
                                {
                                    "tags": 1,
                                    "_id": 0,
                                    })
        stream['_id'] = stream_id

        if self.get_argument("media_id", None) is not None:

            media = yield motor.Op(self.db.media.find_one, {"_id": ObjectId(self.get_argument("media_id"))},
                                    {
                                        "tags": 1,
                                        "artist": 1,
                                        "album": 1,
                                        "title": 1,
                                        "quality": 1,
                                        "size": 1,
                                        "original_filename": 1,
                                        "_id": 0,
                                        })
            media['_id'] = self.get_argument("media_id")
        else:
            media = None


        self.write({
            "stream": stream,
            "media": media
        })
        self.finish()


    @tornado.web.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self):

        stream_id = self.get_argument("stream_id")
        action = self.get_argument("action")

        if action == "create":
            name = self.get_argument("name")
            update = {"tags": name}
            update = yield motor.Op(self.db.streams.update, {"_id":ObjectId(stream_id)}, {"$push": update}, upsert=False, multi=False)
        elif action == "delete":
            name = self.get_argument("name")
            update = {"tags": name}
            update = yield motor.Op(self.db.streams.update, {"_id":ObjectId(stream_id)}, {"$pull": update}, upsert=False, multi=False)
        elif action == "rename":

            name = self.get_argument("name")
            update = {"tags": name}
            stream = yield motor.Op(self.db.streams.find_one, {"_id": ObjectId(stream_id)},
                                    {
                                        "tags": 1,
                                        "_id": 0,
                                        })
            tags = stream['tags']
            for i in range(len(tags)):
                if tags[i] == self.get_argument("name"):
                    tags[i] = self.get_argument("new_name")

            update = {'tags': tags}
            update = yield motor.Op(self.db.streams.update, {"_id":ObjectId(stream_id)}, {"$set": update}, upsert=False, multi=False)
        elif action == "tags":

            media_id = self.get_argument("media_id")
            media = yield motor.Op(self.db.media.find_one, {"_id": ObjectId(media_id)},
                                    {
                                        "tags": 1,
                                        "_id": 0,
                                        })
            update = {
                'artist': self.get_argument("artist"),
                'title': self.get_argument("title"),
                'tags': media['tags']
            }

            names = self.request.arguments['tag-name[]']
            values = self.request.arguments['tag-value[]']

            for i in range(len(names)):
                update['tags'][names[i]] = values[i]

            update = yield motor.Op(self.db.media.update, {"_id":ObjectId(media_id)}, {"$set": update}, upsert=False, multi=False)



        self.finish()




class ListenersStatisticsHandler(AdminHandler):

    # @tornado.web.authenticated
    # @tornado.web.asynchronous
    # @tornado.gen.coroutine
    # def get(self):
    #
    #     stream_id = self.get_argument("stream_id")
    #     now = datetime.datetime.now()-datetime.timedelta(days=165)
    #
    #     for i in range(1000):
    #         now = now+datetime.timedelta(hours=random.randint(1, 10))
    #         insert = {
    #             "stream_id": stream_id,
    #             "datetime": datetime.datetime(now.year, now.month, now.day, now.hour),
    #             "year": now.year,
    #             "month": now.month,
    #             "day": now.day,
    #             "hour": now.hour,
    #             "listeners": random.randint(1, 100)
    #         }
    #
    #         response = yield motor.Op(self.db.statistics.insert, insert)
    #
    #     self.write({"msg":"OK"})
    #     self.finish()



    @tornado.web.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self):

        if "stream_ids[]" not in self.request.arguments:
            raise tornado.web.HTTPError(400)

        stream_ids = self.request.arguments["stream_ids[]"]

        range = self.get_argument("range")

        day = self.get_argument("day")
        try:
            # if True:
            day = day.split(".")
            since = datetime.datetime(int(day[2]), int(day[1]), int(day[0]))
            if range == "day":
                until = since+datetime.timedelta(days=1)
            if range == "month":
                until = self.add_months(since, 1)
            if range == "year":
                until = self.add_months(since, 12)
        except:
            raise tornado.web.HTTPError(400)


        for stream_id in stream_ids:
            if range == "month":
                yield self.update_cache(stream_id, "day")
            if range == "year":
                yield self.update_cache(stream_id, "day")
                yield self.update_cache(stream_id, "month")

        streams = {}

        x = []
        y = []
        legend = []


        for stream_id in stream_ids:

            streams[stream_id] = yield motor.Op(self.db.streams.find_one, {"_id":ObjectId(stream_id)},
                                                {"name":1, "_id": 0})

            legend.append(streams[stream_id]["name"])

        # "x": [
        #          ["2012-10-8 00:00:00", "2012-10-9 00:00:00", "2012-10-10 00:00:00", "2012-10-11 00:00:00", "2012-10-12 00:00:00", "2012-10-13 00:00:00", "2012-10-14 00:00:00"],
        #          ["2012-10-8 00:00:00", "2012-10-9 00:00:00", "2012-10-10 00:00:00", "2012-10-11 00:00:00", "2012-10-12 00:00:00", "2012-10-13 00:00:00", "2012-10-14 00:00:00"],
        #          ["2012-10-8 00:00:00", "2012-10-9 00:00:00", "2012-10-10 00:00:00", "2012-10-11 00:00:00", "2012-10-12 00:00:00", "2012-10-13 00:00:00", "2012-10-14 00:00:00"]
        #      ],
        # "y": [
        #          [5, 90, 0, 00, 10, 50, 10],
        #          [0, 10, 20, 5, 20, 60, 1],
        #          [10, 10, 20, 45, 10, 10, 10]
        #      ],
        # "legend": [ "odoslane", "zrusene", "dokoncene"],

        for stream_id in stream_ids:

            query = {
                "stream_id": stream_id,
                "datetime": {"$gte": since, "$lte": until}
            }

            if range == "day":
                query["month"] = {"$exists": True}
                query["day"] = {"$exists": True}
                query["hour"] = {"$exists": True}
            if range == "month":
                query["month"] = {"$exists": True}
                query["day"] = {"$exists": True}
                query["hour"] = {"$exists": False}
            if range == "year":
                query["month"] = {"$exists": True}
                query["day"] = {"$exists": False}
                query["hour"] = {"$exists": False}

            x_sub = []
            y_sub = []
            cursor = self.db.statistics.find(query, {
                "_id": 0,
                "datetime": 1,
                "listeners": 1
            }, sort=[('datetime', 1)])


            results = yield motor.Op(cursor.to_list, self.batch_size)

            since_temp = datetime.datetime(since.year, since.month, since.day)
            until_temp = datetime.datetime(until.year, until.month, until.day)

            for result in results:

                while since_temp < result["datetime"]:

                    x_sub.append(since_temp.strftime("%Y-%m-%d %H:%M:%S"))
                    y_sub.append(0)

                    if range == "day":
                        since_temp+=datetime.timedelta(hours=1)
                    if range == "month":
                        since_temp+=datetime.timedelta(days=1)
                    if range == "year":
                        since_temp = self.add_months(since_temp, 1)

                x_sub.append(result["datetime"].strftime("%Y-%m-%d %H:%M:%S"))
                y_sub.append(result["listeners"])

                if range == "day":
                    since_temp+=datetime.timedelta(hours=1)
                if range == "month":
                    since_temp+=datetime.timedelta(days=1)
                if range == "year":
                    since_temp = self.add_months(since_temp, 1)


            while since_temp < until_temp:

                x_sub.append(since_temp.strftime("%Y-%m-%d %H:%M:%S"))
                y_sub.append(0)

                if range == "day":
                    since_temp+=datetime.timedelta(hours=1)
                if range == "month":
                    since_temp+=datetime.timedelta(days=1)
                if range == "year":
                    since_temp = self.add_months(since_temp, 1)


            x.append(x_sub)
            y.append(y_sub)

        self.write({"x":x, "y":y, "legend":legend})
        self.finish()

    @tornado.gen.coroutine
    def update_cache(self, stream_id, range="day"):

        # cache by days
        now = datetime.datetime.now()
        today = datetime.datetime(now.year, now.month, now.day)
        this_month = datetime.datetime(now.year, now.month, 1)
        if range == "day":
            last_cache = yield motor.Op(self.db.statistics.find_one,
                                        {"stream_id": stream_id, "hour": {"$exists": False}},
                                        {"datetime":1, "_id": 0}, sort=[("datetime", -1)])
        if range == "month":
            last_cache = yield motor.Op(self.db.statistics.find_one,
                                        {"stream_id": stream_id, "hour": {"$exists": False}, "day": {"$exists": False}},
                                        {"datetime":1, "_id": 0}, sort=[("datetime", -1)])

        if last_cache is not None:
            if range == "day":
                last_cached_diff = today-last_cache["datetime"]
                if last_cached_diff >= datetime.timedelta(days=1):
                    cache_since = last_cache["datetime"]+datetime.timedelta(days=1)
                    recache = True
                else:
                    recache = False

            if range == "month":
                if this_month.year != last_cache["datetime"].year or this_month.month != last_cache["datetime"].month:

                    added_month = self.add_months(last_cache["datetime"], 1)

                    cache_since = datetime.datetime(added_month.year, added_month.month, 1)
                    recache = True
                else:
                    recache = False
        else:
            cache_since = datetime.datetime(2000,1,1)
            recache = True

        if range == "day":
            now = datetime.datetime.now()
            cache_until = datetime.datetime(now.year, now.month, now.day)-datetime.timedelta(days=1)
        if range == "month":
            now = datetime.datetime.now()
            cache_until = self.substract_months(datetime.datetime(now.year, now.month, now.day), 1)


        if recache:
            if range == "day":
                query = yield motor.Op(self.db.command,
                                       SON([
                                           ("aggregate", "statistics"),
                                           ("pipeline", [
                                               {"$match": {
                                                   "stream_id": stream_id,
                                                   "datetime": {"$gt": cache_since, "$lt": cache_until}}},
                                               {"$project": {"stream_id": 1, "year": 1, "month": 1, "day": 1, "hour": 1,
                                                             "listeners": 1}},
                                               {"$group": {
                                                   "stream_id": {"$first": "$stream_id"},
                                                   "_id": {"year": "$year", "month": "$month", "day": "$day"},
                                                   "listeners": {"$sum": "$listeners"}}},
                                               {"$sort": SON([("_id.year", 1), ("_id.month", 1), ("_id.day", 1)])},
                                               {"$project": {
                                                   "_id": 0,
                                                   "stream_id": 1,
                                                   "year": "$_id.year",
                                                   "month": "$_id.month",
                                                   "day": "$_id.day",
                                                   "listeners": 1}},
                                               ])
                                       ]))

                if query is not None and "result" in query and len(query["result"]) >= 1:

                    for item in query["result"]:
                        item["datetime"] = datetime.datetime(item["year"], item["month"], item["day"])
                    # print "INSERT"
                    # print query["result"]
                    yield motor.Op(self.db.statistics.insert, query["result"])

            if range == "month":
                query = yield motor.Op(self.db.command,
                                       SON([
                                           ("aggregate", "statistics"),
                                           ("pipeline", [
                                               {"$match": {
                                                   "stream_id": stream_id,
                                                   "hour": {"$exists": False},
                                                   "datetime": {"$gt": cache_since, "$lt": cache_until}}},
                                               {"$project": {"stream_id": 1, "year": 1, "month": 1, "day": 1,
                                                             "listeners": 1}},
                                               {"$group": {
                                                   "stream_id": {"$first": "$stream_id"},
                                                   "_id": {"year": "$year", "month": "$month"},
                                                   "listeners": {"$sum": "$listeners"}}},
                                               {"$sort": SON([("_id.year", 1), ("_id.month", 1)])},
                                               {"$project": {
                                                   "_id": 0,
                                                   "stream_id": 1,
                                                   "year": "$_id.year",
                                                   "month": "$_id.month",
                                                   "listeners": 1}},
                                               ])
                                       ])
                )
                if query is not None and "result" in query and len(query["result"]) >= 1:

                    for item in query["result"]:
                        item["datetime"] = datetime.datetime(item["year"], item["month"], 1)
                    # print "INSERT"
                    # print query["result"]
                    yield motor.Op(self.db.statistics.insert, query["result"])



    def add_months(self, sourcedate, months):

        # append 1 month
        month = int(sourcedate.month - 1 + months)
        year = int(sourcedate.year + month / 12)
        month = int(month % 12 + 1)
        day = min(sourcedate.day,calendar.monthrange(year,month)[1])

        return datetime.datetime(year, month, day)

    def substract_months(self, sourcedate, months):

        # append 1 month
        month = int(sourcedate.month - 1 - months)
        year = int(sourcedate.year + month / 12)
        month = int(month % 12 + 1)
        day = min(sourcedate.day,calendar.monthrange(year,month)[1])

        return datetime.datetime(year, month, day)

