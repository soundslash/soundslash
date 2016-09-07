from Framework.Application import Application

class BaseModule(object):

    def add_attribute(self, key, value):
        Application().settings["attributes"].append((key, value))

    def add_method(self, method):
        Application().settings["methods"].append(method)

    def add_settings_variable(self, key, value):
        Application().settings[key] = value