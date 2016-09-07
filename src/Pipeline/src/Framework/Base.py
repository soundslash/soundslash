import tornado.gen, time, tornado.web
from pydispatch import dispatcher
import copy
import sys
from functools import partial
import types
from threading import Timer
import simplejson as json
import logging
from threading import Thread
import inspect
import re

from Framework.PriorityQueue import PriorityQueue
from Framework.Application import Application



def tornado_task(*args, **kwargs):
    return tornado.gen.Task(*args, **kwargs)

def make_async(f):
    def make_async_in(*a, **kw):
        async_call(f(*a, **kw))
    return make_async_in

def async_call(it, value=None):
    # This function is the core of async transformation.

    try:
        # send the current value to the iterator and
        # expect function to call and args to pass to it
        if it is None: raise StopIteration()
        x = it.send(value)
    except StopIteration:
        return

    args = x[0]
    kwargs = x[1]

    func = args[0]
    args = list(args[1:])

    # define callback and append it to args
    # (assuming that callback is always the last argument)

    callback = lambda new_value: async_call(it, new_value)
    kwargs["callback"] = callback

    func(*args, **kwargs)

def task(*args, **kwargs):
    return (args, kwargs)


class Call():

    proceed = 1
    stop = 0


    def __init__(self, func, ctx = None, cls = None):
        self.func = func
        self.ctx = ctx
        self.cls = cls

    def do(self, *args, **kwargs):

        arguments = self.func.func_code.co_varnames
        if self.cls is not None and hasattr(self.cls, "context") and self.cls.context is not None:
            in_context = self.cls.context
        elif "in_context" in kwargs:
            in_context = kwargs["in_context"]
        else:
            in_context = None

        if in_context is None:
            try:
                kwargs["respond"].this_context = self.cls.context
            except:
                pass

        if "in_context" in kwargs:
            del kwargs["in_context"]

        apply_context = False
        if self.ctx is not None and self.cls is not None:
            logging.getLogger('system').debug("Method "+self.func.__name__+" executed in context "+str(in_context)
                                              +", allowed contexts "+str(self.ctx))
            if in_context in self.ctx:
                logging.getLogger('system').debug("Applying context "+in_context+" to method "+self.func.__name__)
                apply_context = True


        if "respond" in kwargs:
            kwargs["respond"].this_context = in_context
        if "signal" not in arguments and "signal" in kwargs: del kwargs["signal"]
        if "sender" not in arguments and "sender" in kwargs: del kwargs["sender"]

        before = []
        around = []
        after = []
        if apply_context and in_context is not None and in_context in aspects:

            for aspect in aspects[in_context]:
                if aspect["pointcut"].match(self.func.__name__):
                    logging.getLogger('system').debug("Method "+self.func.__name__+" matched aspect "+str(aspect))
                    if "before" in aspect["advise"]: before.append(aspect["advise"]["before"])
                    if "around" in aspect["advise"]: around.append(aspect["advise"]["around"])
                    if "after" in aspect["advise"]: after.append(aspect["advise"]["after"])

        # func_args = copy.copy(args)
        func_kwargs = copy.copy(kwargs)

        # if "before" in func_kwargs: del func_kwargs["before"]
        # if "around" in func_kwargs: del func_kwargs["around"]
        # if "after" in func_kwargs: del func_kwargs["after"]

        # if "before" in kwargs:
        #     kwargs["before"](**func_kwargs)

        if len(before) > 0:
            for b in before:

                result = b(self=self.cls, **func_kwargs)

                if result == Call.stop:
                    return result
                elif result == Call.proceed:
                    continue
                elif type(result) == dict:
                    del result["self"]
                    func_kwargs = result


        # if "around" in kwargs:
        #     result = kwargs["around"](*args, **func_kwargs)
        if len(around) > 0:
            for a in around:
                result = a(self=self.cls, *args, **func_kwargs)
                break
        else:

            result = self.func(*args, **func_kwargs)


        if len(after) > 0:
            for a in after:
                result = a(self=self.cls, *args, **func_kwargs)
                if result == Call.stop:
                    return result
                elif result == Call.proceed:
                    continue

        # if "after" in kwargs:
        #     kwargs["after"](**func_kwargs)

        return result

def ctx():
    # registry = {}
    def context(ctx=None):
        def context_inner(func):
            @make_async
            def context_inner_inner(*args, **kwargs):
                try:
                    self = args[0]
                except: self = None
                return Call(func, ctx, self).do(*args, **kwargs)
            context_inner_inner.__name__ = func.__name__
            # registry[func.__name__] = func
            return context_inner_inner

        return context_inner
    # context.all = registry
    return context

in_context = ctx()
aspects = {}

def context(ctx):
    def context_in(original_class):
        orig_init = original_class.__init__
        try:
            context_aspects = original_class.aspects()
        except:
            context_aspects = None
        if context_aspects is not None:
            logging.getLogger('system').debug("Registering to context "+ctx+" aspects "+str(context_aspects))
            for context_aspect in context_aspects:
                context_aspect["pointcut"] = re.compile(context_aspect["pointcut"])
            if ctx not in aspects: aspects[ctx] = []
            aspects[ctx] = aspects[ctx]+context_aspects

        def __init__(self, *args, **kwargs):
            self.context = ctx
            orig_init(self, *args, **kwargs)

        original_class.__init__ = __init__
        return original_class
    return context_in


def asynchronous(func):
    @make_async
    def context_inner_inner(*args, **kwargs):
        try:
            self = args[0]
        except: self = None
        return Call(func, None, self).do(*args, **kwargs)
        # registry[func.__name__] = func
    context_inner_inner.__name__ = func.__name__
    return context_inner_inner


class MetaBase(type):
    def __call__(cls, *args, **kw):
        obj = type.__call__(cls, *args, **kw)
        return obj


class Base(object):

    __metaclass__ = MetaBase

    def __init__(self):
        if issubclass(self.__class__, Thread):
            Thread.__init__(self)

        if not hasattr(self, "context"):
            self.context = None
        else:
            if self.context is not None:
                logging.getLogger('system').debug("Initializing context "+self.context)

        Application().register_object(self)

    # def on_load(self):
    #
    #     print "POKUSAM"
    #
    #     for fn in self.__dict__.values():
    #         # print fn
    #         if hasattr(fn, '__call__'):
    #             try:
    #                 fn.__func__.class_name = self.__class__.__name__
    #             except:
    #                 fn.class_name = self.__class__.__name__
    #
    #             print str(fn)+" nastavujem "+str(self.__class__.__name__)

    # Calling using yield task(self.send...), we are changing worker after every message, calling self.send will block
    # current worker and cannot be unblocked.
    # After unblock, all operations should be blocking, because when first unblock operation is fired, thread will end
    # so callback will be called from Worker and unblock is useless.
    def send(self, message, in_context=None, callback=None, unblock=False):

        signal = message

        if isinstance(signal["signal"], dict):
            signal["signal"] = json.dumps(signal["signal"])

        if not 'sender' in signal:
            signal['sender'] = self

        signal['in_context'] = in_context

        print(unblock, callback)

        if callback is None:
            save_here = {}
            def respond(result, save_here):
                save_here["result"] = result
            dispatcher.send(respond=partial(respond, save_here=save_here), **signal)
            if not "result" in save_here:
                return None
            else:
                return save_here["result"]

        elif not unblock:
            print('245897239485732947239487230942379084')
            logging.getLogger('system').debug(self.id+" blocking and sending message "+str(signal["signal"]))
            signal['respond'] = callback
            PriorityQueue.queue.put(signal)

        else:
            def fn(signal, callback):
                logging.getLogger('system').debug("Received message from "+str(signal["sender"].id)
                                                  +", dispatching "+str(signal["signal"]))
                dispatcher.send(respond=callback, **signal)

            logging.getLogger('system').debug(self.id+" unblocking and sending message "+str(signal["signal"]))
            self.o_settings["executor"].submit(
                fn, signal, callback
            )

    def call(self, fn, callback, in_context=None, unblock=False, *args, **kwargs):

        callback.this_context = in_context

        if not unblock:
            logging.getLogger('system').debug(self.id+" blocking and calling function "+str(fn.__name__))

            fn(respond=callback, in_context=in_context, *args, **kwargs)
        else:
            logging.getLogger('system').debug(self.id+" unblocking and calling function "+str(fn.__name__))
            self.o_settings["executor"].submit(
                fn, respond=callback, in_context=in_context, *args, **kwargs
            )

    def sleep(self, seconds, callback):
        Timer(seconds, callback, ()).start()

    def connect(self, handler, signal, sender=dispatcher.Any, weak=False):
        if isinstance(signal, dict):
            signal = json.dumps(signal)
        logging.getLogger('system').debug(self.id+" connecting signal to handler "+str(signal))
        dispatcher.connect(receiver=handler, signal=signal, sender=sender, weak=weak)

    def add_method(self, func):
        self.__dict__[func.__name__] = types.MethodType(func, self, self.__class__)

    def add_attribute(self, key, value):
        self.__dict__[key] = value

    @property
    def id(self):
        return self.__class__.__name__+"_"+str(id(self))
