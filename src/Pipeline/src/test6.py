def asynchronous(func):
    @make_async
    def context_inner_inner(*args, **kwargs):
        return func(*args, **kwargs)
    context_inner_inner.__name__ = func.__name__
    return context_inner_inner

def make_async(f):
    def g(*a, **kw):
        async_call(f(*a, **kw))
    return g

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
    return [args, kwargs]
    

@asynchronous
def ab(arg, callback):
    print arg
    callback("fu")

@asynchronous
def read(callback):
    a = yield task(ab, "a")
    print a
    #yield "Second sentence"
    #for i in range(3):
    #    yield str(i)+" sentence"
    callback("a")

#for i in read():
#    print(i)

def a(res):
    print res

print read(a)
