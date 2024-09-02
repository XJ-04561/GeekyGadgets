
from GeekyGadgets.Globals import *

import GeekyGadgets.Iterators.Itertools as _Itertools
import GeekyGadgets.Classy as _Classy
import GeekyGadgets.Math.Stats.Binning as Binning
import GeekyGadgets.Math.Stats.Functions as _MathFuncs


__all__ = ("Alternate", "AlphaRange", "ChainChain", "DropThenTakeWhile", "Echo", "EveryNth", "Grouper", "Join", "River", "SlidingWindow", "Spaced", "Zip", "Wrap")

_NOT_SET = object()
_END = object()
_T1 = TypeVar("_T1")
_T2 = TypeVar("_T2")
_E = TypeVar("_E")

class Row(tuple):
	def __new__(cls, iterable: Iterable = ()) -> "Row":
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
		from GeekyGadgets.Formatting import numerateAlpha
		
		if not isinstance(start, str):
			pass
		elif isinstance(stop, str):
			start = numerateAlpha(start)
			stop = numerateAlpha(stop)
		elif isinstance(stop, int):
			start = numerateAlpha(start)
			stop = start+stop
		else:
			start = numerateAlpha(start)+1
		
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
	"""
	```python
	DropThenTakeWhile(iterable : Iterable[_E], key : Callable[[_E],bool])
	```
		Drops first items for which `key(item)` evaluates to `False` and only starts yielding items after it first returns `True`.
		Stops yielding items when the iterable is exhausted or `key(item)` evaluates to `False`.
		Default key is the boolean evaluation of the items themselves.
	
	Ex:
	```python
	DropThenTakeWhile(range(10), lambda x: 3 < x < 7) -> 4,5,6
	```
	///
	---

	```python
	DropThenTakeWhile(iterable : Iterable[_E], startKey : Callable[[_E],bool], stopKey : Callable[[_E],bool])
	```
		Drops first items for which `startKey(item)` evaluates to `True` and only starts yielding items after it first returns `False`.
		Stops yielding items when the iterable is exhausted or `stopKey(item)` evaluates to `False`.
	
	Ex:
	```python
	DropThenTakeWhile(range(10), lambda x: 3 < x, lambda x: x < 7) -> 0,1,2,3,4,5,6
	```
	"""
	@overload
	def __init__(self, iterable : Iterable|Iterator, /): ...
	@overload
	def __init__(self, iterable : Iterable|Iterator, key : Callable, /): ...
	@overload
	def __init__(self, iterable : Iterable|Iterator, startKey : Callable, stopKey : Callable, /): ...
	def __init__(self, iterable : Iterable|Iterator, startKey=None, stopKey=None, /):
		if startKey is None:
			self.startKey = lambda x:not bool(x)
			self.stopKey = bool
		elif stopKey is None:
			self.stopKey = startKey
			self.startKey = lambda x: not startKey(x)
		else:
			self.startKey = startKey
			self.stopKey = stopKey

		self.iterator = _Itertools.TakeWhile(self.stopKey, _Itertools.DropWhile(self.startKey, iterable))
	
	def __iter__(self):
		return self
	
	def __next__(self):
		return next(self.iterator)

class ChainChain:
	def __init__(self, *iterables: Iterable) -> None:
		self.iterator = _Itertools.Chain(*(_Itertools.Chain(*iterable) for iterable in iterables))
	
	def __iter__(self):
		return self
	
	def __next__(self):
		return next(self.iterator)

class Echo(Subscriptable):
	def __init__(self, iterable : Iterable[_T1], n : int=2) -> None:
		self.iterator = iter(iterable)
		self.prev = []
		self.n = n
	
	def __iter__(self):
		return self
	
	def __next__(self : "Echo[_T1]") -> tuple[_T1]:
		while len(self.prev) < self.n:
			self.prev.append(next(self.iterator))
		ret = (*self.prev, )
		self.prev.pop(0)
		return ret

class EveryNth(Subscriptable):
	def __init__(self, iterable : Iterable, n : int, start : int=0) -> None:
		self.iterator = iter(iterable)
		for _ in zip(range(start), self.iterator): pass
		self.n = n
	
	def __iter__(self):
		return self
	
	def __next__(self):
		for i in range(self.n-1):
			next(self.iterator)
		return next(self.iterator)

class Grouper(Subscriptable):
	"""Groups values of an iterable according to their value or the value returned when passed to the function given 
	as `key`. When the set of possible/expected keys are known, they can be specified (order-specific) using 
	the `keys` argument."""

	@overload
	def __init__(self, iterable: Iterable[_T1]) -> "Grouper[_T1, _T1]": ...
	@overload
	def __init__(self, iterable: Iterable[_T1], key: Callable[[_T1], _T2]) -> "Grouper[_T1, _T2]": ...
	@overload
	def __init__(self, iterable: Iterable[_T1], keys: Iterable[_T1]) -> "Grouper[_T1, _T1]": ...
	@overload
	def __init__(self, iterable: Iterable[_T1], key: Callable[[_T1], _T2], keys: Iterable[_T2]) -> "Grouper[_T1, _T2]": ...
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

class Join:
	def __init__(self, sep, iterable : Iterable) -> None:
		self.iterator = iter(iterable)
		self.sep = sep
		self.switch = False

	def __iter__(self):
		return self
	
	def __next__(self):
		return self.sep if self.switch else next(self.iterator)

class River(_Itertools.Chain):
	@staticmethod
	def _floaty(item): yield item
	def __init__(self, *iterables: _Classy.Iterable) -> _Classy.NoneType:
		super().__init__(*(item if isinstance(item, Iterable) else River._floaty(item) for item in iterables))

class SlidingWindow(Subscriptable):
	
	front : int
	tail : int

	def __init__(self : "SlidingWindow[tuple[_Itertools.IterSlice[_E], float]]", data : Iterable[_E], width : Number|Callable[[list[_E]],Number]=Binning.sturges, strict : bool=True) -> None:
		self.data = sorted(data)
		self.strict = bool(strict)
		if len(self.data) == 0:
			self.width = float("nan")
		elif isinstance(width, Number):
			self.width = width
		elif isinstance(width, Callable):
			from GeekyGadgets.Math.Stats.Functions import span
			self.width = span(self.data) / width(data)
		else:
			raise TypeError(f"`width` must either be a number or a callable that takes the given data as its first argument and returns a suitable width as a number")
		self.r = self.width / 2
		self.n = len(self.data)
		self.front = 0
		self.tail = 0

		if self.strict:
			while self.front < self.n and self.data[self.tail]+self.width > self.data[self.front]:
				self.front += 1
	
	def __iter__(self : "SlidingWindow[_Itertools.IterSlice[_E]]") -> "SlidingWindow[tuple[_Itertools.IterSlice[_E], float]]":
		return self

	def __next__(self : "SlidingWindow[_Itertools.IterSlice[_E]]") -> tuple[_Itertools.IterSlice[_E], float]:
		
		if self.tail >= self.n-1:
			raise StopIteration()
		elif self.front >= self.n:
			if self.strict:
				raise StopIteration()
			else:
				self.tail += 1
		elif self.data[self.tail]+self.width > self.data[self.front]:
			self.front += 1
		elif self.data[self.tail+1]-self.data[self.tail] < self.data[self.front]-self.data[self.front-1]:
			self.tail += 1
		elif self.data[self.tail+1]-self.data[self.tail] > self.data[self.front]-self.data[self.front-1]:
			self.front += 1
		else:
			self.front += 1
		
		if self.tail == self.front == 0:
			pos = next(iter(self.data)) - self.width
		elif self.tail == self.front:
			pos = (self.data[self.front] + self.data[self.tail-1]) / 2
		elif self.tail == self.front-1:
			pos = self.data[self.tail]
		else:
			pos = (self.data[self.front-1] + self.data[self.tail]) / 2
			+ min( # Margin front
				self.width/2 - (self.data[self.front-1] - pos),
				(self.data[self.tail+1] - self.data[self.tail])
			)
			- min( # Margin tail
				self.width/2 - (pos - self.data[self.tail]),
				(self.data[self.front-1] - self.data[self.front-2])
			)
		return (_Itertools.IterSlice(self.data, self.tail, self.front), pos)

class SortedChain(Subscriptable):
	
	def __init__(self, *iterables, order=min):
		self.iterators = list(map(iter, iterables))
		self.foyer = [next(iterable, _END) for iterable in self.iterators]
		self.order = order
	
	def __iter__(self):
		return self
	
	def __next__(self):
		try:
			ret = self.order(item for item in self.foyer if item is not _END)
		except TypeError:
			raise StopIteration()
		else:
			self.foyer[self.foyer.index(ret)] = next(self.iterators[self.foyer.index(ret)], _END)
			return ret

class Spaced(Subscriptable):
	def __init__(self, start : Number, stop : Number, n : int, *, mode : str="lin") -> None:
		self.iterator = iter(range(n))
		match mode[:3]:
			case "lin":
				self.transform = lambda x: x
				self.inverse = lambda x: x
			case "log":
				from math import log, exp
				if not mode[3:]:
					self.transform = log
					self.inverse = exp
				else:
					base = int(mode[3:])
					self.transform = partial(log, base=base)
					self.inverse = lambda x: base**x
		self.start = start
		self.stop = stop
		self.step = (self.transform(stop) - self.transform(start)) / (n-1)
	
	def __iter__(self):
		return self
	
	def __next__(self : "Spaced[_T1]") -> _T1:
		return self.inverse(self.transform(self.start)+self.step*next(self.iterator))

class Wrap(Subscriptable):
	def __init__(self, iterable : Iterable, n : int) -> None:
		self.iterator = iter(iterable)
		self.n = n
	
	def __iter__(self):
		return self
	
	def __next__(self):
		ret = tuple(nxt for i in range(self.n) if (nxt := next(self.iterator, NULL)) is not NULL )
		if len(ret) == 0:
			raise StopIteration()
		return ret
