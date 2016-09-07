
from concurrent.futures import ThreadPoolExecutor
import sys
from pymongo import MongoClient
import logging
from functools import partial

from Framework.Application import Application
from Framework.Modules.BaseModule import BaseModule


def query(obj, fn, *args, **kwargs):

    def handle_response(future, callback):
        callback(future.result())

    callback = kwargs["callback"]
    del kwargs["callback"]

    obj.o_settings["db_executor"].submit(
        fn, *args, **kwargs
    ).add_done_callback(partial(handle_response, callback=callback))


class PyMongoDriver(BaseModule):

    def __init__(self, host, port, user, password, database, max_pool_size=100, max_workers=5):

        self.db = MongoClient(
            host='mongodb://'+user+':'+password+'@'+host+'/'+database,
            port=port,
            max_pool_size=max_pool_size,
            )[database]

        self.db_executor = ThreadPoolExecutor(max_workers=max_workers)

    def register(self):
        logging.getLogger('system').debug(self.id+" registering PyMongoDriver")
        self.add_settings_variable("db_executor", self.db_executor)

        self.add_attribute("db", self.db)
        self.add_attribute("syncdb", self.db)
        self.add_attribute("batch_size", sys.maxint)

        self.add_method(query)


    @property
    def id(self):
        return self.__class__.__name__+"_"+str(id(self))
