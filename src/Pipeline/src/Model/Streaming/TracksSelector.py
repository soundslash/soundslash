#!/usr/bin/env python

"""
Select tracks from database (in Playlist readable format)
"""

from mongokit import *
import datetime
import random
from collections import OrderedDict
from Queue import Queue
import time
from multiprocessing.synchronize import BoundedSemaphore
from threading import Thread
import copy

from Framework.Base import *
from Model.BaseThreaded import BaseThreaded
from bson.objectid import ObjectId

__author__ = "Michal Bystricky"
__copyright__ = "Copyright 2013, Michal Bystricky"
__status__ = "Prototype"


class TracksSelector(Base):

    def __init__(self, stream):
        super(TracksSelector, self).__init__()

        self.stream = unicode(stream)

    @asynchronous
    def select_by_ids(self, ids, respond):

        or_query = []
        for i in range(len(ids)):
            try:
                or_query.append({"_id":ObjectId(ids[i])})
            except:
                pass


        if or_query == []:
            respond([])
        else:

            medias = yield task(self.query, self.db.media.find, {
                                                    "$or": or_query
                                                },
                                                {
                                                    "_id": 1,
                                                    "artist": 1,
                                                    "album": 1,
                                                    "title": 1,
                                                    "file_id": 1,
                                                    "tags.duration": 1,
                                                    })
            medias = list(medias)

            medias_new = []
            for i in range(len(ids)):
                for media in medias:
                    if (unicode(media["_id"]) == ids[i]):
                        medias_new.append(copy.copy(media))
                        break
            del medias
            respond(medias_new)

    @asynchronous
    def select_by_groups(self, respond, groups = [], sorted = True, limit = 1000):
        if sorted:
            all_medias = []
            for group in groups:
                partial_limit = limit - len(all_medias)
                if partial_limit == 0: break
                medias = yield task(self.query, self.db.media.find, {
                                                                 "stream_id": self.stream,
                                                                 "groups.id": group
                                                             },
                    {
                        "_id": 1,
                        "artist": 1,
                        "album": 1,
                        "title": 1,
                        "file_id": 1,
                        "tags.duration": 1,
                    },
                    limit=partial_limit, sort=[("groups.weight", 1)])
                all_medias += list(medias)


            respond(all_medias)

        else:
            # random attribute
            # http://cookbook.mongodb.org/patterns/random-attribute/

            rand = float(random.uniform(0,1))

            medias = yield task(self.query, self.db.media.find, {
                                                             "stream_id": self.stream,
                                                             "groups.id": {"$in": groups},
                                                             "random": {"$gte": rand}
                                                         },
                                                         {
                                                             "_id": 1,
                                                             "artist": 1,
                                                             "album": 1,
                                                             "title": 1,
                                                             "file_id": 1,
                                                             "tags.duration": 1,
                                                             },
                                                         limit=limit)
            medias = list(medias)

            if len(medias) < limit:

                medias2 = yield task(self.query, self.db.media.find, {
                                                                 "stream_id": self.stream,
                                                                 "groups.id": {"$in": groups},
                                                                 "random": {"$lt": rand}
                                                             },
                                                             {
                                                                 "_id": 1,
                                                                 "artist": 1,
                                                                 "album": 1,
                                                                 "title": 1,
                                                                 "file_id": 1,
                                                                 "tags.duration": 1,
                                                                 },
                                                             limit=limit-len(medias))
                medias2 = list(medias2)


            else:
                medias2 = []
            respond(medias + medias2)
