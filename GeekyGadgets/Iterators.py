
from collections.abc import Iterable
from GeekyGadgets.Globals import *

_E = TypeVar("_E")
_NOT_SET = object()

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
from itertools import chain as Chain, takewhile as TakeWhile, dropwhile as DropWhile, zip_longest as ZipLongest, repeat as Repeat

__all__ = ("Batched", "Chain", "Repeat", "TakeWhile", "DropWhile", "ZipLongest", "DropThenTakeWhile", "ChainChain", "Grouper",
		   "Walker", "LeavesWalker", "BranchesWalker", "ConfigWalker", "AlphaRange")

class AlphaRange:

	_range : range

	@overload
	def __init__(self, stop: SupportsIndex, /) -> range: ...
	@overload
	def __init__(self, start: SupportsIndex, stop: SupportsIndex, step: SupportsIndex = ..., /) -> range: ...
	def __init__(self, start, stop=_NOT_SET, step=_NOT_SET, /):
		if stop is _NOT_SET:
			self._range = range(start)
		elif step is _NOT_SET:
			self._range = range(start, stop)
		else:
			self._range = range(start, stop, step)

	def __iter__(self):
		from GeekyGadgets.Formatting import alphabetize
		for i in self._range:
			yield alphabetize(i)

class DropThenTakeWhile:
	@overload
	def __init__(self, iterable : Iterable|Iterator): ...
	@overload
	def __init__(self, iterable : Iterable|Iterator, key : Callable): ...
	@overload
	def __init__(self, iterable : Iterable|Iterator, startKey : Callable, stopKey : Callable): ...
	def __init__(self, iterable : Iterable|Iterator, startKey=None, stopKey=None, key=None):
		if key is not None:
			self.startKey = self.stopKey = key
		else:
			if startKey is None:
				self.startKey = lambda x:bool(x)
			else:
				self.startKey = startKey
			if stopKey is None:
				self.stopKey = lambda x:bool(x)
			else:
				self.stopKey = stopKey

		self.iterator = iterable if isinstance(iterable, Iterator) else iter(iterable)
	
	def __iter__(self):
		return self
	
	def __next__(self):
		next(TakeWhile(self.stopKey, DropWhile(self.startKey, self.iterator)))

class ChainChain(Chain):
	def __init__(self, *iterables: Iterable) -> None:
		super().__init__(*(Chain(iterable) for iterable in iterables))

_T1 = TypeVar("_T1")
_T2 = TypeVar("_T2")

class Grouper(Subscriptable): pass
class Grouper(Subscriptable):
	"""Groups values of an iterable according to their value or the value returned when passed to the function given 
	as `key`. When the set of possible/expected keys are known, they can be specified (order-specific) using 
	the `keys` argument."""

	

	@overload
	def __init__(self, iterable: Iterable[_T1]) -> Grouper[_T1, _T1]: ...
	@overload
	def __init__(self, iterable: Iterable[_T1], key: Callable[[_T1], _T2]) -> Grouper[_T1, _T2]: ...
	@overload
	def __init__(self, iterable: Iterable[_T1], keys: Iterable[_T1]) -> Grouper[_T1, _T1]: ...
	@overload
	def __init__(self, iterable: Iterable[_T1], key: Callable[[_T1], _T2], keys: Iterable[_T2]) -> Grouper[_T1, _T2]: ...
	def __init__(self, iterable, key=None, keys=None):
		"""The `Grouper.keys` are set/determined by iterating the iterable at instantiation, and not when iterated. If 
		an *Iterator* is passed as `iterable`, a `tuple` is created from it and saved instead of the iterator. When `keys` is excluded, the keys created are sorted using `sorted()` """
		
		if isinstance(iterable, Iterator):
			self.iterable = tuple(iterable)
		elif isinstance(iterable, Iterable):
			self.iterable = iterable
		else:
			iter(iterable)
			self.iterable = iterable
		self.key = key or (lambda x:x)
		if keys is None:
			self.keys = sorted(set(map(self.key, iterable)), reverse=True)
		else:
			self.keys = list(reversed(tuple(keys)))
	
	def __next__(self):
		if not self.keys:
			raise StopIteration()
		
		currentKey = self.keys.pop()
		
		return tuple(filter(lambda x:self.key(x) == currentKey, self.iterable))
			
			
		

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
	from GeekyGadgets.Configs import Config, ConfigCategory

class ConfigWalker(Walker):
	"""Iterator that iterates in-order through an iterable and down through all their iterable elements. Going all the
	way down through an element before progressing to the next element.

	Yields name-value pairs, where the name-value pairs are dependent on the iterator method used:

	* `ConfigWalker.__next__` - Iterates through both categories and variables.
	
	* `ConfigWalker.categories` - Iterates only through categories.
	
	* `ConfigWalker.variables` - Iterates only through variables."""
	
	_iterator : Config[str,Any]

	@classmethod
	def recursiveWalk(cls, iterable : Config, root : str=None) -> Generator[tuple[str,str,ConfigCategory|Any],None,None]:
		for name, value in iterable.items():
			yield (root, name, value)
			if isinstance(value, ConfigCategory):
				yield from cls.recursiveWalk(value, root=f"{root}.{name}" if root is not None else name)
	
	@property
	def categories(self) -> Generator[tuple[str,str,ConfigCategory],None,None]:
		for root, name, value in self:
			if isinstance(value, ConfigCategory):
				yield (root, name, value)
	
	@property
	def variables(self) -> Generator[tuple[str,str,Any],None,None]:
		for root, name, value in self:
			if not isinstance(value, ConfigCategory):
				yield (root, name, value)
