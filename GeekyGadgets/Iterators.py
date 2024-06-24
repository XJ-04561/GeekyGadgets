
from collections.abc import Iterable
from GeekyGadgets.Globals import *
from GeekyGadgets.Globals import Callable

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

from itertools import (
	chain as Chain, takewhile as TakeWhile, dropwhile as DropWhile, zip_longest as ZipLongest,
	repeat as Repeat)

__all__ = ("Alternate", "AlphaRange", "Batched", "BranchesWalker", "Chain", "ChainChain", "ConfigWalker",
		   "DropThenTakeWhile", "DropWhile", "Grouper", "LeavesWalker", "Repeat", "TakeWhile", "Walker", "ZipLongest")

_E = TypeVar("_E")
_E1 = TypeVar("_E1")
_E2 = TypeVar("_E2")
_E3 = TypeVar("_E3")
_E4 = TypeVar("_E4")
_E5 = TypeVar("_E5")
_E6 = TypeVar("_E6")

class Row(tuple):
	def __new__(cls, iterable: Iterable = ()) -> Self:
		obj = super().__new__(cls, iterable)
		obj._iterator = tuple.__iter__(obj)
		return obj
	def __iter__(self):
		return self
	def __next__(self):
		return next(self._iterator)

class Zip(zip, Subscriptable):
	rowFactory : type = tuple
	def __next__(self) -> Any:
		return self.rowFactory(super().__next__())

class Alternate(Subscriptable):
	"""Iterate through multiple iterables but iterate only through one position at a time from each iterable. Stops 
	when the first iterable reaches its end. If `strict` is set to `True`, then a `ValueError` is raised.
	
	`Alternate("ABCDEFG", range(7)) -> "A", 0, "B", 1, "C", 2, "D", 3, ...`
	"""

	row : Row
	iterator : Zip[Row]

	def __init__(self, *iterables : Iterable, strict : bool=False):
		self.iterator = Zip(*iterables, strict=strict)
		self.iterator.rowFactory = Row
		self.row = Row()
	
	def __iter__(self):
		return self
	
	def __next__(self):
		for item in self.row:
			return item
		for row in self.iterator:
			self.row = Row(row)
			for item in self.row:
				return item
		raise StopIteration()

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

		self.iterator = TakeWhile(self.stopKey, DropWhile(self.startKey, iterable))
	
	def __iter__(self):
		return self
	
	def __next__(self):
		return next(self.iterator)

class ChainChain:
	def __init__(self, *iterables: Iterable) -> None:
		self.iterator = Chain(*(Chain(*iterable) for iterable in iterables))
	
	def __iter__(self):
		return self
	
	def __next__(self):
		return next(self.iterator)

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
	
	def __iter__(self):
		return self

	def __next__(self):
		if not self.keys:
			raise StopIteration()
		
		currentKey = self.keys.pop()
		
		return tuple(filter(lambda x:self.key(x) == currentKey, self.iterable))


class Walker(Iterator):
	"""Iterator that iterates in-order through an iterable and down through all their iterable elements. Going all the
	way down through an element before progressing to the next element."""
	
	_iterator : Iterator[_E]

	def __init__(self, iterable : Iterable, key : Callable=iter):
		self._iterator = self.recursiveWalk(iterable, key=key)
	
	def __next__(self) -> _E:
		return next(self._iterator)
	
	@classmethod
	def recursiveWalk(cls, iterable, key : Callable=iter) -> Generator[_E, None, None]:
		for item in iterable:
			yield item
			if isinstance(item, Iterable):
				yield from cls.recursiveWalk(key(item))

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
			if isinstance(item, Iterable):
				return item
		else:
			raise StopIteration(f"{self} came to a stop.")

class GraphWalker(Walker):
	@classmethod
	def recursiveWalk(cls, iterable, key : Callable=None, history : set=None) -> Generator[Any,None,None]:
		from GeekyGadgets.Illustrative.NodesAndGraphs import Node, Edge, Graph
		if history is None:
			history = set()
		if isinstance(iterable, Graph):
			yield from cls.recursiveWalk(iterable.root, history=history)
		else:
			for obj in iterable.connections:
				history.add(obj)
				yield obj
				yield from cls.recursiveWalk(obj, history=history)

class NodeWalker(Walker):
	"""Iterator that iterates in-order through an iterable and down through all their iterable elements. Going all the 
	way down through an element before progressing to the next element.
	
	But, only yields the elements which are themselves iterable, and not their non-iterable elements.
	"""
	
	_iterator : Iterator[_E]

	def __next__(self) -> _E:
		from GeekyGadgets.Illustrative.NodesAndGraphs import Node
		for item in self._iterator:
			if isinstance(item, Node):
				return item
		else:
			raise StopIteration(f"{self} came to a stop.")

class EdgeWalker(Walker):
	"""Iterator that iterates in-order through an iterable and down through all their iterable elements. Going all the 
	way down through an element before progressing to the next element.
	
	But, only yields the elements which are themselves iterable, and not their non-iterable elements.
	"""
	
	_iterator : Iterator[_E]

	def __next__(self) -> _E:
		from GeekyGadgets.Illustrative.NodesAndGraphs import Edge
		for item in self._iterator:
			if isinstance(item, Edge):
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
	def recursiveWalk(cls, iterable : Config, root : str=None, key : Callable=iter) -> Generator[tuple[str,str,ConfigCategory|Any],None,None]:
		for name, value in iterable.items():
			yield (root, name, value)
			if isinstance(value, ConfigCategory):
				yield from cls.recursiveWalk(value, root=f"{root}.{name}" if root is not None else name, key=key)
	
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
