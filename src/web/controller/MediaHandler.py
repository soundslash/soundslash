
__version__ = "0.2"

from controller.BaseHandler import BaseHandler
import tornado.web
import tornado.gen
import motor
from bson.objectid import ObjectId
from helpers.string import transliterate

class MediaHandler(BaseHandler):

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self, file_id):

        media = yield motor.Op(self.db.media.find_one, {"file_id": file_id}, {"artist": 1, "title": 1, "_id": 0})
        artist = transliterate(media["artist"])
        title = transliterate(media["title"])
        filename = artist+"-"+title+".ogg"

        self.set_header('Content-Type', 'application/ogg')
        self.set_header('Content-Disposition', 'attachment; filename="'+filename+'"')
        self.set_header('Content-Transfer-Encoding', 'binary')

        fs = motor.MotorGridFS(self.db)
        gridout = yield motor.Op(fs.get, ObjectId(file_id))
        content = yield motor.Op(gridout.read)

        self.write(content)
        self.finish()

