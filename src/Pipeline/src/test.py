class M(type):
	def __new__(meta, name, bases, attrs):
		print meta
		attrs["ufo"] = 3
		print attrs
		print("We could alter creation of class object before initialization of class object")
		return type.__new__(meta, name, bases, attrs)
	
	def __init__(cls, name, bases, attrs):
		print("We could alter class object after initialization of class object")
		print attrs
		print cls
		cls.ufao = "2"
		print attrs
		return type.__init__(cls, name, bases, attrs)

	def __call__(cls, *args, **kwargs):
		print("We could alter constructor attributes before initialization of object")
		return type.__call__(cls, *args, **kwargs)

class Book(object):
	__metaclass__ = M
	def __init__(self, content):
		self.content = content
	def read(self):
		print(self.content)

book = Book("content")
print type(book.read)
book = Book("content")
book.read()
print book.ufao
print Book.ufao
