from concurrent.futures import ThreadPoolExecutor
from noconflict import classmaker

from Framework.Singleton import Singleton

class Application(Singleton):
    __metaclass__=classmaker()

    def __init__(self, settings):
        if "methods" not in settings:
            settings["methods"] = []
        if "attributes" not in settings:
            settings["attributes"] = []

        # default max workers in unblock=True
        if "unblock_workers" not in settings:
            settings["unblock_workers"] = 5

        settings["executor"] = ThreadPoolExecutor(max_workers=settings["unblock_workers"])
        self.settings = settings

    def register_object(self, o):

        for method in self.settings["methods"]:
            o.add_method(method)

        for attribute in self.settings["attributes"]:
            # key, value
            o.add_attribute(attribute[0], attribute[1])

        o.o_settings = self.settings



