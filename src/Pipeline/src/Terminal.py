#!/usr/bin/env python

"""
Terminal class handle access through console (e.g. Bash, SSH).
"""

from threading import Thread
import logging
import readline
from bson.objectid import ObjectId
from bson.objectid import InvalidId
from multiprocessing.synchronize import BoundedSemaphore

from Framework.Base import *

__author__ = "Michal Bystricky"
__copyright__ = "Copyright 2013, Michal Bystricky"
__credits__ = ["Michal Bystricky", "Samuel Stehlik"]
__status__ = "Prototype"

BOLD = '\033[1m'
DARK_GREEN = '\033[32m'
DARK_BLUE = '\033[34m'
ENDC = '\033[0m'

class Terminal(Base, Thread):
    def __init__(self):
        super(Terminal, self).__init__()

        self.__stream = None
        self.stopped = False

        self.connect(
            handler= self.parse_and_execute,
            signal= "run_command"
        )

    @asynchronous
    def run(self):
        while not self.stopped:
            command = raw_input(BOLD+DARK_GREEN+"pipeline "+DARK_BLUE+"$ "+ENDC)

            if command:

                yield task(self.send, message={"signal": "run_command", "command": command})


    @asynchronous
    def parse_and_execute(self, command, respond):

        logging.getLogger('pipeline').debug("Terminal: Trying to run commands "+command)

        subcommands = command.split(";")
        result = []

        for command in subcommands:

            command_splitted = command.split()
            try:
                execute = command_splitted[0].strip()
                args = command_splitted[1:]
            except:
                continue


            #
            # if execute == "help":
            #     result.append(self.__director.help())

            if execute == "use":
                if len(args) >= 1:
                    try:
                        ObjectId(args[0])
                        self.__stream = args[0]
                        result.append({"msg": "Stream is "+args[0]})
                    except InvalidId:
                        err = "InvalidId: "+args[0]+" is not a valid ObjectId"
                        result.append({"error": err})
                else:
                    err = "Stream _id is required (hint: use _id)"
                    result.append({"error": err})

            elif self.__stream is None:
                err = "Stream _id is required (hint: use _id)"
                result.append({"error": err})

            elif execute == "dump_dot_file":
                sub_result = yield task(self.send, message={"signal": "dump_dot_file", "stream": self.__stream}, unblock=True)
                result.append(sub_result)

            elif execute == "start":
                # TODO 0? FAIL
                response = yield task(self.send, message={"signal": "start", "stream": self.__stream, "quality": float(0)}, unblock=True)
                result.append(response)
                # result.append(self.__director.start_streaming(self.__stream, 0))

            elif execute == "stop":
                response = yield task(self.send, message={"signal": "stop", "stream": self.__stream}, unblock=True)
                result.append(response)
                # result.append(self.__director.stop_streaming(self.__stream))

            elif execute == "next":
                response = yield task(self.send, message={"signal": "next", "stream": self.__stream}, unblock=True)
                result.append(response)
                # result.append(self.__director.next(self.__stream))

            elif execute == "scale":
                if len(args) == 1:
                    quality = float(args[0])
                else:
                    quality = None
                response = yield task(self.send, message={"signal": "scale", "stream": self.__stream, "quality": quality}, unblock=True)
                result.append(response)
                # result.append(self.__director.scale_streaming(self.__stream, quality))


            elif execute == "rescale":
                if len(args) == 1 and args[0] == "force":
                    stop = True
                else:
                    stop = False

                response = yield task(self.send, message={"signal": "rescale", "stream": self.__stream, "stop": stop}, unblock=True)
                result.append(response)

                # result.append(self.__director.rescale_streaming(self.__stream, stop))

            elif execute == "playlist":
                response = yield task(self.send, message={"signal": "print_playlist", "stream": self.__stream}, unblock=True)
                result.append(response)

            else:
                err = "pipeline: "+execute+": command not found"

                result.append({"error": err})

        logging.getLogger('pipeline').debug("Terminal: Result "+unicode(result))

        respond({"result": result})
