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
    
    func = x[0]
    args = list(x[1:])

    # define callback and append it to args
    # (assuming that callback is always the last argument)

    callback = lambda new_value: async_call(it, new_value)
    args.append(callback)

    func(*args)

#def task(func, *args, **kwargs):
#    return async_call(func(*args, **kwargs))
    

@make_async
def ab(arg, callback):
    print arg
    callback("fu")

@make_async
def read(callback):
    a = yield ab, "a"
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
