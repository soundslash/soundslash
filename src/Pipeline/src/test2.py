def my_decorator(attr=None):
    def my_decorator_in(func):
        def my_decorator_in_in(*args, **kwargs):
            print("Decorator called with argument "+str(attr))
            print("Before function")
            result = func(*args, **kwargs)
            print("After function")
            return result
        return my_decorator_in_in
    return my_decorator_in
    
class Book(object):
    content = "Something"
    @my_decorator("Hello!")
    def read(self):
        print(self.content)

Book().read()
