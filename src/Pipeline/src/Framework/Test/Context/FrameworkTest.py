from __future__ import print_function
import logging
import time
from threading import Thread


from Framework.Base import *

class FrameworkTest(Base):

    def __init__(self):
        super(FrameworkTest, self).__init__()

        self.connect(self.do_something, signal="on_do_something", sender=self)
        self.connect(self.do_something2, signal={"method": "do_something2", "id": self.id}, sender=self)

    def do_something(self, respond):
        print(self)
        print("#423423")
        a = self.send(message={ "signal": {"method": "do_something2", "id":self.id} })
        print("3242"+a)
        print(self)
        time.sleep(1)

        # line = self.send(message={ "signal": {"method": "do_something2", "id":self.id} })
        # print(line)
        respond("DO SOMETHING!!!!")

    def do_something2(self, respond):
        respond("UFOOOOOOOOOOOO ")



    @asynchronous
    def run(self):

        print(self)

        for i in range(1):
            line = yield task(self.send, message={"signal": "on_do_something"}, unblock=True)
            print(line)

        print(self)
        print("PRED RESPO")
        line = yield task(self.query, self.db.users.find_one, {"email": "trash@mby.sk"}, {"_id": 1})
        print(line)

        print("PO RESP")

        print(time.time())
        line = yield task(self.sleep, 1)
        print(line)
        print(time.time())




        def before_something(*args, **kwargs):
            logging.getLogger('system').debug("BEFORE!!!!!")

        result = yield task(self.send, message={
            "signal": "on_do_something",
            "before": before_something
        }, unblock=True)

        print(self)

        print("Usecase Pride z jeld "+str(result))

        line = yield task(self.send, {"signal": "on_do_something"})
        print("Usecase 2 "+str(line))


        print(self)



class FrameworkTestThread(Base, Thread):

    def __init__(self):
        super(FrameworkTestThread, self).__init__()

        self.connect(self.do_something, signal="on_do_something", sender=self)
        self.connect(self.do_something2, signal={"method": "do_something2", "id": self.id}, sender=self)

    def do_something(self, respond):
        print(self)
        print("#423423")
        a = self.send(message={ "signal": {"method": "do_something2", "id":self.id} })
        print("3242"+a)
        print(self)
        time.sleep(1)

        # line = self.send(message={ "signal": {"method": "do_something2", "id":self.id} })
        # print(line)
        respond("DO SOMETHING!!!!")

    def do_something2(self, respond):
        respond("UFOOOOOOOOOOOO ")


    def run(self):

        print(self)

        for i in range(1):
            line = self.send(message={"signal": "on_do_something"})
            print(line)

        print(self)

        print(time.time())
        time.sleep(1)
        print(time.time())


        def before_something(*args, **kwargs):
            logging.getLogger('system').debug("BEFORE!!!!!")

        result = self.send(message={
            "signal": "on_do_something",
            "before": before_something
        })

        print(self)

        print("Usecase Pride z jeld "+str(result))
