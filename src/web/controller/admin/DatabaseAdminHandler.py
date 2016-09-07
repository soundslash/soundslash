
__version__ = "0.2"

import tornado.web
import tornado.gen
import motor
from bson.objectid import ObjectId
import urllib

from controller.admin.AdminHandler import AdminHandler
from controller.PipelineRouter import PipelineRouter


class SearchDatabaseAdminHandler(AdminHandler):

    @tornado.web.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self, stream_id):

        group_id = self.get_argument("group_id")
        search = self.get_argument("search")

        page_user = self.get_argument("page", 1)
        page = int(page_user)-1
        per_page = 10
        skip = int(page*per_page)

        query = {}
        query["stream_id"] = stream_id
        query["groups.id"] = group_id

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

        cursor = self.db.media.find(query, {
                                        "_id": 1,
                                        "artist": 1,
                                        "title": 1,
                                        "tags.duration": 1,
                                        "album": 1,
                                        "file_id": 1
                                    }, limit=per_page, skip=skip)

        results = yield motor.Op(cursor.to_list, self.batch_size)

        for i in range(len(results)):
            results[i]["_id"] = unicode(results[i]["_id"])
            results[i]["duration"] = results[i]["tags"]["duration"]

        if int(page_user) == 1:
            first_page = True
        else:
            first_page = False

        if len(results) < per_page:
            last_page = True
        else:
            last_page = False

        self.write({"results": results, "page": page_user, "first_page": first_page, "last_page": last_page})
        self.finish()



class DatabaseAdminHandler(AdminHandler):

    @tornado.web.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self, stream_id):

        stream = yield motor.Op(self.db.streams.find_one, {"_id": ObjectId(stream_id)},
                                {"reencoding":1, "name": 1, "default_program_id": 1, "_id": 1})

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


        self.template_vars["group_id"] = group_id

        self.template_vars["group"] = yield motor.Op(self.db.groups.find_one, {"_id": ObjectId(group_id)},
                                 {"fade_in":1, "fade_out": 1, "_id": 0})

        self.template_vars["program"] = program

        stream["id"] = unicode(stream["_id"])
        self.template_vars["stream"] = stream

        self.template_vars["media"] = results

        self.template_vars["menu"] = "streams"
        self.template_vars["submenu"] = "database"
        self.template_vars["stream_id"] = stream_id

        self.render("admin/database.html", **self.template_vars)

    @tornado.web.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self, stream_id):

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

