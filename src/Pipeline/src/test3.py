class my_function(object):
    def __call__(self, value):
        print value

mfunc = my_function()
mfunc("This should be printed")
