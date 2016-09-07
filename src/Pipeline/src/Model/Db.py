from mongokit import *

from config import config
from Model.Server import Server
from Model.Stream import Stream
from Model.File import File
from Model.Media import Media
from Model.Group import Group
from Model.Program import Program

class Db(object):
    def __init__(self):

        self.dbname = "pipeline"

        self.connection = Connection(config["dbhost"], config["dbport"])
        self.connection[self.dbname].authenticate(config["dbuser"], config["dbpass"])

        self.connection.register([Server, Stream, Media, File, Group, Program])

    @property
    def conn(self):
        return self.connection[self.dbname]

    def destroy(self):
        self.__del__()

    def __del__(self):
        self.connection.disconnect()
        self.connection.close()
