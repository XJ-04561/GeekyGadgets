
from GeekyGadgets.Globals import *

_E = TypeVar("_E")

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
	
	_iterator : Iterator[_E]

	def __init__(self, iterable : Iterable):
		self._iterator = self.recursiveWalk(iterable)
	
	def __next__(self) -> _E:
		return next(self._iterator)
	
	@classmethod
	def recursiveWalk(cls, iterable) -> Generator[_E, None, None]:
		for item in iterable:
			yield item
			if isinstance(item, Iterable):
				yield from cls.recursiveWalk(item)

class LeavesWalker(Walker):
	"""Iterator that iterates in-order through an iterable and down through all their iterable elements. Going all the
	way down through an element before progressing to the next element.
	
	But, only yields the elements which are not 
	themselves iterable."""
	
	_iterator : Iterator[Iterable|_E]

	def __next__(self) -> _E:
		for item in self._iterator:
			if not isinstance(item, Iterable):
				return item
		else:
			raise StopIteration(f"{self} came to a stop.")

class BranchesWalker(Walker):
	"""Iterator that iterates in-order through an iterable and down through all their iterable elements. Going all the 
	way down through an element before progressing to the next element.
	
	But, only yields the elements which are themselves iterable, and not their non-iterable elements.
	"""
	
	_iterator : Iterator[_E]

	def __next__(self) -> _E:
		for item in self._iterator:
			if not isinstance(item, Iterable):
				return item
		else:
			raise StopIteration(f"{self} came to a stop.")

#
#	Relevant to Configs.py
#

if "Config" not in globals():
	from GeekyGadgets.Configs import Config, Category

class ConfigWalker(Walker):
	"""Iterator that iterates in-order through an iterable and down through all their iterable elements. Going all the
	way down through an element before progressing to the next element.

	Yields name-value pairs, where the name-value pairs are dependent on the iterator method used:

	* `ConfigWalker.__next__` - Iterates through both categories and variables.
	
	* `ConfigWalker.categories` - Iterates only through categories.
	
	* `ConfigWalker.variables` - Iterates only through variables."""
	
	_iterator : Config[str,Any]

	@classmethod
	def recursiveWalk(cls, iterable : Config, root : str=None) -> Generator[tuple[str,str,Category|Any],None,None]:
		for name, value in iterable.items():
			yield (root, name, value)
			if isinstance(value, Category):
				yield from cls.recursiveWalk(value, root=f"{root}.{name}" if root is not None else name)
	
	@property
	def categories(self) -> Generator[tuple[str,str,Category],None,None]:
		for root, name, value in self:
			if isinstance(value, Category):
				yield (root, name, value)
	
	@property
	def variables(self) -> Generator[tuple[str,str,Any],None,None]:
		for root, name, value in self:
			if not isinstance(value, Category):
				yield (root, name, value)
