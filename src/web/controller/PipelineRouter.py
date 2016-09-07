
__version__ = "0.2"

import tornado.web
import tornado.gen
import tornado.websocket
import motor
from bson.objectid import ObjectId
import simplejson as json
import urllib

class PipelineRouter():

    def __init__(self, db, stream_id):
        self.db = db
        self.stream_id = stream_id

    @tornado.gen.engine
    def get_server(self, callback):

        stream = yield motor.Op(self.db.streams.find_one, {"_id": ObjectId(self.stream_id)},
                                {"pipeline_server":1, "_id": 0})

        if not "pipeline_server" in stream or stream["pipeline_server"] is None:
            server = {"error": "No pipeline server"}
        else:
            server = yield motor.Op(self.db.servers.find_one, {"_id": ObjectId(stream["pipeline_server"])},
                                    {"local_ip":1, "port":1, "_id": 0})

        callback(server)

    def get_live_url(self, server):
        return "ws://"+unicode(server["local_ip"])+":"+unicode(server["port"])+"/live.json"

    def get_updates_url(self, server):
        return "ws://"+unicode(server["local_ip"])+":"+unicode(server["port"])+"/updates.json"

    def get_restart_url(self, server):
        return "http://"+server["local_ip"]+":"+unicode(server["port"])+"/restart.json"

    def get_start_streaming_url(self, server):
        return "http://"+server["local_ip"]+":"+unicode(server["port"])+"/start-streaming.json"

    def get_scale_url(self, server):
        return "http://"+server["local_ip"]+":"+unicode(server["port"])+"/scale.json"

    def get_terminal_url(self, server):
        return "http://"+server["local_ip"]+":"+unicode(server["port"])+"/run-command.json"

    def get_playlist_update_url(self, server):
        return "http://"+server["local_ip"]+":"+unicode(server["port"])+"/playlist-update.json"

    @tornado.gen.engine
    def request(self, callback, url, post_args, attempts=3, raw_result = False):

        for attempt in range(attempts):

            tornado.httpclient.AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient")
            http_client = tornado.httpclient.AsyncHTTPClient()

            req = tornado.httpclient.HTTPRequest(url, body=urllib.urlencode(post_args), method="POST")

            raw_response = yield tornado.gen.Task(http_client.fetch, req)

            if raw_response.error:
                response = {"error": "Error while connecting to backend"}
            else:
                try:
                    response = json.loads(unicode(raw_response.body))
                except:
                    response = {"error": "Error while parsing response from backend"}


            if "error" not in response:
                break


        if raw_result:
            response = raw_response

        callback(response)

    def request_sync(self, url, post_args, attempts=3, raw_result = False):

        for attempt in range(attempts):

            http_client = tornado.httpclient.HTTPClient()

            req = tornado.httpclient.HTTPRequest(url, body=urllib.urlencode(post_args), method="POST")

            raw_response = http_client.fetch(req)


            if raw_response.error:
                response = {"error": "Error while connecting to backend"}
            else:
                try:
                    response = json.loads(unicode(raw_response.body))
                except:
                    response = {"error": "Error while parsing response from backend"}


            if "error" not in response:
                break


        if raw_result:
            response = raw_response

        return response
