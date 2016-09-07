
__version__ = "0.2"

import re
from controller.BaseHandler import BaseHandler
from helpers.genres import genres
import tornado.web
import tornado.gen
import datetime
import random
import motor
from bson.son import SON
from collections import OrderedDict
from bson.objectid import ObjectId
from helpers.countries import countries
import json

class ProgramHandler(BaseHandler):

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self):


        data = json.loads(self.get_argument("data"))
        stream_id = self.get_argument("stream_id")


        if data['shuffle']:
            selection = 'shuffle'
        else:
            selection = 'sequence'

        start_arr = data['start'].split(':')
        end_arr = data['end'].split(':')

        day = data['day']

        now = datetime.datetime.now()
        if now.strftime("%A") == day:
            day = now
        else:
            i = 1
            find = now
            while find.strftime("%A") != day:
                print find
                find += datetime.timedelta(days=1)
                if i == 7: break
                i += 1
            day = find

        start = datetime.datetime(day.year, day.month, day.day, int(start_arr[0]), int(start_arr[1]), 0)
        # day += datetime.timedelta(days=1)
        end = datetime.datetime(day.year, day.month, day.day, int(end_arr[0]), int(end_arr[1]), 0)

        if start > end:
            temp = end
            end = start
            start = temp

        valid = True

        s = datetime.datetime(day.year, day.month, day.day, 0, 0, 0)
        e = datetime.datetime(day.year, day.month, day.day, 23, 59, 59)
        cursor = self.db.programs.find({"start": {"$gte": s}, "end": {"$lte": e}}, {
            "_id": 1, "name": 1, "start": 1, "end": 1
        })
        today_programs = yield motor.Op(cursor.to_list, self.batch_size)
        collides = False
        for p in today_programs:
            if self.get_argument("program_id", None) is not None:
                if (self.get_argument("program_id") == unicode(p['_id'])): continue

            if (p['start'] < start and start < p['end']) or (p['start'] < end and end < p['end']):
                collides = True
                collides_with = p['name']

        if data['name'] == "":
            valid = False
            error = "Please fill in name of program"
        elif end-start < datetime.timedelta(minutes=15):
            valid = False
            error = "Program must be more than 15 minutes long"
        elif 'playlist' not in data:
            valid = False
            error = "You must select program"
        elif collides:
            valid = False
            error = "Program "+collides_with+" collide with this program"



        if valid:
            program = {
                "fade_in" : 0,
                "fade_out" : 0,
                # "user_id": self.get_current_user(),
                "stream_id": stream_id,
                "force_start" : data['exact'],
                "groups" : [
                    data['playlist']
                ],
                "color" : data['color'],
                "jukebox" : False,
                "name" : data['name'],
                "repeating" : [{'media_id': repeat['id'], 'repeating': int(repeat['repeating'])} for repeat in data['repeats']],
                "selection" : selection,
                "start" : start,
                "end" : end,
                "weight" : 1
            }

            if 'picture' in data and data['picture'] != 'undefined':
                image = yield motor.Op(self.db.images.update, {"_id":ObjectId(data['picture']), "tags": {"$in": ["delete"]}},
                                       {"$set":{"tags": ["program_cover"]}}, upsert=False, multi=False)
                program['picture'] = data['picture']

            if self.get_argument("program_id", None) is not None:
                yield motor.Op(self.db.programs.update, {"_id": ObjectId(self.get_argument("program_id"))}, {"$set": program})
            else:
                yield motor.Op(self.db.programs.insert, program)

            if self.get_argument("remove", False) == 'true':
                yield motor.Op(self.db.programs.remove, {"_id": ObjectId(self.get_argument("program_id"))})

            self.write({
                'program': self.dict_normalize(program)
            })
            self.finish()
        else:

            self.write({
                'error': error
            })
            self.finish()

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):

        if self.get_argument("program_id", None) is not None:

            stream_id = self.get_argument("stream_id")
            program = yield motor.Op(self.db.programs.find_one, {"_id": ObjectId(self.get_argument("program_id"))},
                {
                    '_id': 1,
                    'name': 1,
                    'start': 1,
                    'selection': 1,
                    'force_start': 1,
                    'end': 1,
                    'repeating': 1,
                    'picture': 1,
                    'groups': 1,
                    'color':1
                })

            if len(program['repeating']) > 0:
                repeating_q = []
                for repeat in program['repeating']:
                    repeating_q.append(
                        {
                            "_id": ObjectId(repeat['media_id'])
                        }
                    )

                cursor = self.db.media.find({"$or": repeating_q}, {
                    "_id": 1, "weight": 1, "artist": 1, "title": 1, "tags": 1
                })

                repeating = yield motor.Op(cursor.to_list, self.batch_size)
                for repeat in repeating:
                    repeat['id'] = repeat['media_id'] = repeat['_id']
                    for r in program['repeating']:
                        if str(r['media_id']) == str(repeat['id']):
                            repeat['repeating'] = r['repeating']
                            break
                    repeat['duration'] = repeat['tags']['duration']
            else:
                repeating = []


            group = yield motor.Op(self.db.groups.find_one, {"_id": ObjectId(program['groups'][0])},
                                     {
                                         '_id': 1,
                                         'name': 1,
                                     })
            group['id'] = group['_id']


            stream = yield motor.Op(self.db.streams.find_one, {"_id": ObjectId(stream_id)},
                                    {"default_program_id": 1, "_id": 0})

            default_program = yield motor.Op(self.db.programs.find_one, {"_id": ObjectId(stream["default_program_id"])},
                                     {"groups":1, "selection": 1, "_id": 0})
            # basic mode pick first, in extended mode there is different situation where user selecting the group
            group_id = default_program["groups"][0]

            self.write({
                'program': self.dict_normalize(program),
                'repeating': self.list_normalize(repeating),
                'group': self.dict_normalize(group),
                'group_id': group_id
            })
            self.finish()
        else:

            stream_id = self.get_argument("stream_id")
            day = self.get_argument("day")

            now = datetime.datetime.now()
            if now.strftime("%A") == day:
                day = now
            else:
                i = 1
                find = now
                while find.strftime("%A") != day:
                    find += datetime.timedelta(days=1)
                    if i == 7: break
                    i += 1
                day = find

            start = datetime.datetime(day.year, day.month, day.day, 0, 0, 0)
            # day += datetime.timedelta(days=1)
            end = datetime.datetime(day.year, day.month, day.day, 23, 59, 59)

            cursor = self.db.programs.find({
                                            "stream_id": stream_id,
                                            "$or": [
                                                # middle
                                                {
                                                    "start": {
                                                        "$gte": start,
                                                        "$lte": end
                                                    },
                                                    "end": {
                                                        "$gte": start,
                                                        "$lte": end
                                                    },
                                                },
                                                # left
                                                {
                                                    "start": {
                                                        "$lte": start,
                                                    },
                                                    "end": {
                                                        "$gte": start,
                                                        "$lte": end
                                                    },
                                                },
                                                # right
                                                {
                                                    "start": {
                                                        "$gte": start,
                                                        "$lte": end
                                                        },
                                                    "end": {
                                                        "$gte": end
                                                    },
                                                },
                                                # above
                                                {
                                                    "start": {
                                                        "$lte": start,
                                                    },
                                                    "end": {
                                                        "$gte": end
                                                    },
                                                },
                                            ]
                                         }, {
                                            "_id": 1,
                                            "start": 1,
                                            "end": 1,
                                            "name": 1,
                                            "color": 1,
                                            "picture": 1,
                                            "weight": 1
                                        }, sort=[('weight', -1), ('start', 1)])

            results = yield motor.Op(cursor.to_list, self.batch_size)
            program = self.list_normalize(results)


            self.write({
                'program': program,
                'day': start.strftime("%Y-%m-%d")
            })
            self.finish()