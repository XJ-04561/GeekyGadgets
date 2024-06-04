
from GeekyGadgets.Globals import *

if PYTHON_VERSION < (3, 12):
	class Batched(Iterator):
		def __init__(self, iterable, n):
			self.iterable = iter(iterable) if hasattr(iterable, "__iter__") else iterable
			self.n = n
		
		def __iter__(self):
			_iter = iter(self.iterable) if hasattr(self.iterable, "__iter__") else self.iterable
			
			while (ret := tuple(item for i, item in zip(range(self.n), _iter))):
				yield ret
else:
	from itertools import batched as Batched

class Walker(Iterator):
	"""Iterator that iterates in-order through an iterable and down through all their iterable elements. Going all the
	way down through an element before progressing to the next element."""
		
	def __init__(self, iterable : Iterable):
		self._iterator = self.recursiveWalk(iterable)
	
	def __next__(self):
		return next(self._iterator)
	
	@classmethod
	def recursiveWalk(cls, iterable):
		for item in iterable:
			yield item
			if isinstance(item, Iterable):
				yield from cls.recursiveWalk(item)

class LeavesWalker(Walker):
	"""Iterator that iterates in-order through an iterable and down through all their iterable elements. Going all the
	way down through an element before progressing to the next element.
	
	But, only yields the elements which are not 
	themselves iterable."""
	
	def __next__(self):
		for item in self._iterator:
			if not isinstance(item, Iterable):
				return item
		else:
			raise StopIteration(f"{self} came to a stop.")

class ConfigWalker(Walker):
	"""Iterator that iterates in-order through an iterable and down through all their iterable elements. Going all the
	way down through an element before progressing to the next element.

	Yields name-value pairs, where the name-value pairs are dependent on the iterator method used:

	 * `ConfigWalker.__next__` - Iterates through both categories and variables.
	
	 * `ConfigWalker.categories` - Iterates only through categories.
	 
	 * `ConfigWalker.variables` - Iterates only through variables."""
	
	@classmethod
	def recursiveWalk(cls, iterable : "Config"):
		for name, value in iterable.items():
			yield (name, value)
			if isinstance(value, Category):
				yield from cls.recursiveWalk(value)
	
	@property
	def categories(self):
		for name, value in self:
			if isinstance(value, Category):
				yield (name, value)
	
	@property
	def variables(self):
		for name, value in self:
			if not isinstance(value, Category):
				yield (name, value)


try:
	from GeekyGadgets.Configs import Config, Category
except ImportError:
	pass