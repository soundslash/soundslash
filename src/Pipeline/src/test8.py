from __future__ import print_function
import logging
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')
from Framework.Base import *
from Framework.PriorityQueue import PriorityQueue
from Framework.Application import Application
from Framework.Worker import Worker

class StringHandler(Base):
    def __init__(self): super(StringHandler, self).__init__()

    @in_context(["MyContext"])
    def to_uppercase(self, content, respond):
        content = yield task(self.call, in_context=respond.this_context, fn=self.append_everything,
                             content=content)
        respond(content.upper())

    @in_context(["MyContext"])
    def append_everything(self, content, respond):
        respond(content+"42")

@context("MyContext")
class ReadingBook(Base):

    @staticmethod
    def aspects():
        def before_to_uppercase(content, *args, **kwargs):
            print("Content before to_uppercase() is "+str(content))
            return Call.proceed

        aspect = {
            "pointcut": "^to.*",
            "advise": {
                "before": before_to_uppercase
            }
        }

        return [aspect]

    def __init__(self, content):
        super(ReadingBook, self).__init__()
        self.content = content

    @in_context(["MyContext", "AnotherAllowedContext"])
    def read(self, respond):
        sh = StringHandler()
        new_content = yield task(self.call, in_context=respond.this_context, fn=sh.to_uppercase,
                                 content=self.content)
        respond(new_content)

def main():
    # Init framework
    Application({})

    # Run the example code
    book = ReadingBook(content="This is content")
    book.read(respond=lambda result: print(result))


if __name__=="__main__":
    main()



