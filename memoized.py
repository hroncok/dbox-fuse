import collections
import functools
from datetime import datetime, timedelta
from time import sleep

class memoized(object):
   '''Decorator. Caches a function's return value each time it is called.
   If called later with the same arguments, the cached value is returned
   (not reevaluated), unless more than 10 seconds passed.
   '''
   def __init__(self, func):
      self.func = func
      self.cache = {}
   def __call__(self, *args):
      if not isinstance(args, collections.Hashable):
         # uncacheable. a list, for instance.
         # better to not cache than blow up.
         return self.func(*args)
      if args in self.cache and self.cache[args][0] >= datetime.now()-timedelta(seconds=10):
         return self.cache[args][1]
      else:
         value = self.func(*args)
         self.cache[args] = datetime.now(), value
         return value
   def __repr__(self):
      '''Return the function's docstring.'''
      return self.func.__doc__
   def __get__(self, obj, objtype):
      '''Support instance methods.'''
      return functools.partial(self.__call__, obj)
      
class memoyield(memoized):
   '''Decorator. Caches a function's return value each time it is called.
   If called later with the same arguments, the cached value is returned
   (not reevaluated), unless more than 5 seconds passed. Designed for yielding
   functions. This does the conversion from a generator to a list and back to
   a generator, so might not be the fastest solution ever.
   '''
   def __call__(self, *args):
      if args in self.cache and self.cache[args][0] >= datetime.now()-timedelta(seconds=5):
         for i in self.cache[args][1]:
            yield i
      else:
         gen = self.func(*args)
         value = list(gen)
         self.cache[args] = datetime.now(), value
         for i in value:
            yield i
