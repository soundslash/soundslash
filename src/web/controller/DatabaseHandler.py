
__version__ = "0.2"

import tornado.web
import tornado.gen
import motor
from bson.objectid import ObjectId
from bson.son import SON
import urllib
import json
import time

from controller.admin.AdminHandler import AdminHandler
from controller.PipelineRouter import PipelineRouter


class SearchDatabaseHandler(AdminHandler):

    @tornado.web.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self):

        stream_id = self.get_argument("stream_id")
        group_id = self.get_argument("group_id", None)
        if group_id == 'null': group_id = None
        search = self.get_argument("search")
        asc = int(self.get_argument('asc', 1))
        order = self.get_argument("order", "groups.weight")
        avail_order = ['artist', 'title', 'album', 'created_at']

        page_user = self.get_argument("page", 1)
        page = int(page_user)-1
        per_page = 10
        skip = int(page*per_page)

        if self.get_argument("groups", None) is not None and self.get_argument("groups") != "true":

            query = {"_id": ObjectId(group_id)}
            nav = yield motor.Op(self.db.groups.find_one, query, {
                "_id": 1,
                "parent_group_id": 1,
                "name": 1,
                })
            nav['_id'] = unicode(nav['_id'])
        else:
            nav = None

        if self.get_argument("groups", "false") == "true":

            query = {}
            query["user_id"] = self.get_current_user()
            query['name'] = {'$regex': search}

            cursor = self.db.groups.find(query, {
                "_id": 1,
                "name": 1,
            }, skip=skip, limit=per_page)

            groups = yield motor.Op(cursor.to_list, self.batch_size)
            for i in range(len(groups)):
                groups[i]["_id"] = unicode(groups[i]["_id"])

        else:
            groups = None


        query = {}

        # if self.get_argument("favorites", None) is not None:
        #     pass
        #     # query['is_favorite'] = True
        # else:
        query["groups.id"] = group_id

        query["stream_id"] = stream_id

        artist_or = []
        # album_or = []
        title_or = []
        artist_and = []
        # album_and = []
        title_and = []

        search = search.split(' ')
        for word in search:
            word = "(?i)"+word

            artist_or.append({"artist": {'$regex': word}})
            # album_or.append({"album": {'$regex': word}})
            title_or.append({"title": {'$regex': word}})

            artist_and.append({"artist": {'$regex': word}})
            # album_and.append({"album": {'$regex': word}})
            title_and.append({"title": {'$regex': word}})

        query["$or"] = []

        query_arr_and = []
        query_and = {"$and": query_arr_and}
        query_arr_and.append({"$or":artist_or})
        # query_arr_and.append({"$or":album_or})
        query_arr_and.append({"$or":title_or})
        # concat
        query["$or"].append(query_and)

        # single
        query["$or"].append({"$and":artist_and})
        # query["$or"].append({"$and":album_and})
        query["$or"].append({"$and":title_and})

        if order == "artist":
            order_by = [("artist", asc), ("album", 1), ("title", 1)]
        elif order == "title":
            order_by = [("title", asc)]
        elif order == "album":
            order_by = [("album", asc), ("title", 1)]
        elif order == "created_at":
            order_by = [("created_at", asc)]
        elif order == "groups.weight":
            order_by = [("groups.weight", asc)]

        # cursor = self.db.media.find(query, {
        #     "_id": 1,
        #     "artist": 1,
        #     "title": 1,
        #     "tags.duration": 1,
        #     "groups": 1,
        #     "album": 1,
        #     "file_id": 1
        # }, limit=per_page, skip=skip).sort(order_by)

        if groups is None:
            # results = yield motor.Op(cursor.to_list, self.batch_size)

            query = yield motor.Op(self.db.command,
                                   SON([
                                       ("aggregate", "media"),
                                       ("pipeline", [
                                           {"$match": query},
                                           {"$project": {
                                                   "_id": 1,
                                                   "artist": 1,
                                                   "title": 1,
                                                   "tags.duration": 1,
                                                   "groups": 1,
                                                   "album": 1,
                                                   "file_id": 1,
                                               }},
                                           {"$unwind": "$groups"},
                                           {"$match": {"groups.id": group_id}},
                                           {"$sort": SON(order_by)},
                                           {"$skip": skip },
                                           {"$limit": per_page },


                                           ])
                                   ]))

            if query is not None and "result" in query and len(query["result"]) >= 1:
                results = query["result"]
            else:
                results = []
            print results

        else: results = []

        for i in range(len(results)):
            results[i]["_id"] = unicode(results[i]["_id"])
            results[i]["duration"] = results[i]["tags"]["duration"]
            if group_id is not None:
                # grp = (group for group in results[i]["groups"] if group["id"] == group_id).next()
                results[i]["weight"] = results[i]["groups"]["weight"]
            else:
                results[i]["weight"] = "null"


        if int(page_user) == 1:
            first_page = True
        else:
            first_page = False

        if groups:
            if len(groups) < per_page:
                last_page = True
            else:
                last_page = False

        else:
            if len(results) < per_page:
                last_page = True
            else:
                last_page = False

        self.write({
            "order": order,
            "avail_order": avail_order,
            "asc": asc,
            "results": results,
            "page": page_user,
            "first_page": first_page,
            "last_page": last_page,
            "groups": groups,
            "nav": nav})
        self.finish()



class PlaylistDatabaseHandler(AdminHandler):

    @tornado.web.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self):

        data = json.loads(self.get_argument("data"))

        stream_id = data["stream_id"]
        group_id = data["group_id"]
        action = data["action"]
        action_i = data["i"]
        elems = data["elems"]


        if action == "create":
            name = data["name"]
            group = {
                'user_id': self.get_current_user(),
                'name': name,
                'stream_id': stream_id,
                'fade_in': float(0),
                'fade_out': float(0),
                'playlist': 'sequence'
            }

            yield motor.Op(self.db.groups.insert, group)

        if action == "rename":
            name = data["name"]
            query = {
                '_id': ObjectId(group_id)
            }
            set = {
                'name': name,
            }

            update = yield motor.Op(self.db.groups.update,
                                    query,
                                    {"$set": set}, upsert=False, multi=False)


        if action == "delete-track":

            for i in range(len(elems)):
                elems[i] = ObjectId(elems[i])

            yield motor.Op(self.db.media.remove, {"_id": {"$in": elems}}, multi=True)

        if action == "delete":

            query = {
                '_id': ObjectId(group_id)
            }

            yield motor.Op(self.db.groups.remove, query)

            update = yield motor.Op(self.db.media.update,
                                    {},
                                    {"$pull": {
                                        "groups": {
                                            "id": group_id,
                                        }
                                    }}, upsert=False, multi=True)


        if action == "paste-into":
            for elem in elems:
                update = yield motor.Op(self.db.media.update,
                                        {"_id":ObjectId(elem['id'])},
                                        {"$push": {
                                            "groups": {
                                                "id": group_id,
                                                "weight": elem['weight']
                                            }
                                        }}, upsert=False, multi=False)


        if action == "move":
            #remove and append
            elem = elems[action_i[0]]
            update = yield motor.Op(self.db.media.update,
                                    {"_id":ObjectId(elem['id'])},
                                    {"$pull": {
                                        "groups": {
                                            "id": group_id,
                                            "weight": float(elem['weight'])
                                        }
                                    }}, upsert=False, multi=False)
            action = "append"


        if action == "append" or action == "favorites-append":
            first = action_i[0]
            last = action_i[-1]

            # Try find previous element to append between weights

            if len(elems) == len(action_i):
                #first
                i = int(time.time())+1
                for a_i in action_i:
                    new_weight = i
                    id = elems[a_i]['id']
                    update = yield motor.Op(self.db.media.update,
                                            {"_id":ObjectId(id)},
                                            {"$push": {
                                                "groups": {
                                                    "id": group_id,
                                                    "weight": new_weight
                                                }
                                            }}, upsert=False, multi=False)
                    i+=1

            elif (last+1) <= len(elems)-1:
                below = elems[last+1]
                # elem = yield motor.Op(self.db.media.find_one,
                #                       {
                #                           "stream_id": stream_id,
                #                           "groups": {"$in": [
                #                               {"id": group_id,
                #                                "weight": {"$lt": float(below['weight'])}
                #                               }]}
                #                       }, {"groups":1, "_id": 0}, sort=[('groups.weight', -1)])


                query = yield motor.Op(self.db.command,
                                       SON([
                                           ("aggregate", "media"),
                                           ("pipeline", [
                                               {"$match": {
                                                   "stream_id": stream_id,
                                                   "groups.id": group_id,
                                               }},
                                               {"$project": {
                                                   "_id": 0,
                                                   "groups": 1,
                                                   }},
                                               {"$unwind": "$groups"},
                                               {"$match": {
                                                   "groups.id": group_id,
                                                   "groups.weight": {"$lt": float(below['weight'])}
                                                   }},
                                               {"$sort": SON([('groups.weight', -1)])},
                                               {"$limit": 1 },
                                               ])
                                       ]))

                if query is not None and "result" in query and len(query["result"]) >= 1:
                    elem = query["result"][0]
                else:
                    elem = None

                # Append between elem and below
                if elem:
                    weight_from = float(elem['groups']['weight'])
                else:
                    # it's last
                    weight_from = float(below['weight'])-1
                weight_to = float(below['weight'])
                append_count = float(len(action_i))
                portion = (weight_to-weight_from)/(append_count+1)

                i = 1
                for a_i in action_i:
                    new_weight = weight_from+(i*portion)
                    id = elems[a_i]['id']
                    print(new_weight, id)
                    update = yield motor.Op(self.db.media.update,
                                            {"_id":ObjectId(id)},
                                            {"$push": {
                                                "groups": {
                                                    "id": group_id,
                                                    "weight": new_weight
                                                }
                                            }}, upsert=False, multi=False)
                    i+=1

            # Try find next element to append between weights
            elif 0 <= (first-1) and (first-1) <= len(elems)-1:
                above = elems[first-1]
                # elem = yield motor.Op(self.db.media.find_one,
                #                       {
                #                           "stream_id": stream_id,
                #                           "groups": {"$in": [
                #                               {"id": group_id,
                #                                "weight": {"$gt": float(above['weight'])}
                #                               }]}
                #                       }, {"groups":1, "_id": 0}, sort=[('groups.weight', 1)])



                query = yield motor.Op(self.db.command,
                                       SON([
                                           ("aggregate", "media"),
                                           ("pipeline", [
                                               {"$match": {
                                                   "stream_id": stream_id,
                                                   "groups.id": group_id
                                               }},
                                               {"$project": {
                                                   "_id": 0,
                                                   "groups": 1,
                                                   }},
                                               {"$unwind": "$groups"},
                                               {"$match": {
                                                   "groups.id": group_id,
                                                   "groups.weight": {"$gt": float(above['weight'])}}},
                                               {"$sort": SON([('groups.weight', 1)])},
                                               {"$limit": 1 },
                                               ])
                                       ]))

                if query is not None and "result" in query and len(query["result"]) >= 1:
                    elem = query["result"][0]
                else:
                    elem = None

                    # Append between above and elem
                weight_from = float(above['weight'])
                if elem:
                    weight_to = float(elem['groups']['weight'])
                else:
                    weight_to = float(above['weight'])+1
                append_count = float(len(action_i))
                portion = (weight_to-weight_from)/(append_count+1)
                i = 1
                for a_i in action_i:
                    new_weight = weight_from+(i*portion)
                    id = elems[a_i]['id']
                    print(new_weight, id)
                    update = yield motor.Op(self.db.media.update,
                                            {"_id":ObjectId(id)},
                                            {"$push": {
                                                "groups": {
                                                    "id": group_id,
                                                    "weight": new_weight
                                                }
                                            }}, upsert=False, multi=False)
                    i+=1

        elif action == "remove" or action == "favorites-remove":
            elem = elems[action_i[0]]
            update = yield motor.Op(self.db.media.update,
                                    {"_id":ObjectId(elem['id'])},
                                    {"$pull": {
                                        "groups": {
                                            "id": group_id,
                                            "weight": float(elem['weight'])
                                        }
                                    }}, upsert=False, multi=False)

        self.write({})
        self.finish()

class DatabaseHandler(AdminHandler):

    @tornado.web.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):

        stream_id = self.get_argument("stream_id")

        stream = yield motor.Op(self.db.streams.find_one, {"_id": ObjectId(stream_id)},
                                {"reencoding":1, "name": 1, "default_program_id": 1, "fav_group_id": 1, "_id": 1})
        stream["_id"] = unicode(stream["_id"])

        program = yield motor.Op(self.db.programs.find_one, {"_id": ObjectId(stream["default_program_id"])},
                                 {"groups":1, "selection": 1, "_id": 0})
        # basic mode pick first, in extended mode there is different situation where user selecting the group
        group_id = program["groups"][0]

        cursor = self.db.media.find({"stream_id": stream_id,
                                     "groups.id": group_id}, {
                                        "_id": 1,
                                        "artist": 1,
                                        "title": 1,
                                        "tags.duration": 1,
                                        "groups.weight": 1,
                                        "file_id": 1
                                    }, sort=[('groups.weight', 1)])

        results = yield motor.Op(cursor.to_list, self.batch_size)
        media = self.list_normalize(results)

        group = yield motor.Op(self.db.groups.find_one, {"_id": ObjectId(group_id)},
                               {"fade_in":1, "fade_out": 1, "_id": 0})


        self.write({
            "stream": stream,
            "media": media,
            "group_id": group_id,
            "group": group,
            "program": program
        })
        self.finish()

    @tornado.web.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self):

        stream_id = self.get_argument("stream-id")
        group_id = self.get_argument("group-id")


        ids = self.request.arguments['group[]'][1:-1]
        artists = self.request.arguments['artist[]']
        title = self.request.arguments['title[]']
        remove = self.request.arguments['remove[]']

        dec_count = 0
        dec = 0

        for i in range(len(ids)):
            try:
                id = ObjectId(ids[i])

            except:
                id = None

            if id is not None:
                if remove[i] == "1":
                    yield motor.Op(self.db.media.update, {"_id":id,
                                                          "groups.id": group_id},
                                   {"$pull": { "groups": {"id": group_id} }},
                                   upsert=False, multi=False)

                    group = yield motor.Op(self.db.media.find_one, {"_id": id},
                                           {"groups": 1, "file_id": 1, "size": 1, "_id":0})

                    dec_count += 1
                    dec += group["size"]


                    if len(group["groups"]) == 0:
                        yield motor.Op(self.db.files.remove, {"_id": ObjectId(group["file_id"])})
                        yield motor.Op(self.db.media.remove, {"_id": id})

                else:
                    set = {
                        "artist": artists[i],
                        "title": title[i],
                        "groups.$.weight": i
                    }
                    yield motor.Op(self.db.media.update, {"_id":id,
                                                          "groups.id": group_id},
                                   {"$set":set},
                                   upsert=False, multi=False)


        if dec > 0:
            self.db.users.update({"_id":ObjectId(self.get_current_user())},
                                 {"$dec":{"size": dec}}, upsert=False, multi=False)
            # self.db.streams.update({"_id":ObjectId(stream_id)},
            #                        {"$dec":{"size": group["size"]}}, upsert=False, multi=False)
            self.db.streams.update({"_id":ObjectId(stream_id)},
                                   {"$dec":{"count": dec_count, "size": dec}}, upsert=False, multi=False)



        stream_obj = yield motor.Op(self.db.streams.find_one, {"_id":ObjectId(stream_id)},
                                    {"status": 1, "pipeline_server": 1, "_id": 0})

        if stream_obj["pipeline_server"] is not None:

            pipeline = yield motor.Op(self.db.servers.find_one, {"_id":ObjectId(stream_obj["pipeline_server"])},
                                      {"local_ip": 1, "port": 1, "_id": 0})

            post_args = {
                "stream": stream_id,
                "group": group_id
            }

            pr = PipelineRouter(self.db, None)
            url = pr.get_playlist_update_url(pipeline)

            yield tornado.gen.Task(pr.request, url=url, post_args=post_args)




        self.write({"msg": "Successfully saved"})
        self.finish()

