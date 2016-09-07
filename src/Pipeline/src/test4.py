class Price(object):
      def __get__(self, obj, objtype=None):
          return obj._price * obj._amount

      def __set__(self, obj, value):
          obj._price = value

class Book(object):
     price = Price()

     def __init__(self, amount):
          self._price = 42
          self._amount = amount

book = Book(1)
print(book.price)
book2 = Book(3)
print(book2.price)
print(book.price)
book.price = 1
print(book.price)
print(book2.price)
