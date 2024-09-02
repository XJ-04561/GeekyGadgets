
import GeekyGadgets.Globals as _Globals

_E = _Globals.TypeVar("_E")
_NOT_SET = object()

import itertools

if _Globals.PYTHON_VERSION < (3, 12):
	class Batched:
		def __init__(self, iterable, n):
			self._iter = iter(iterable)
			self.n = n
		
		def __iter__(self):
			return self
		
		def __next__(self):
			while (ret := tuple(item for i, item in zip(range(self.n), self._iter))):
				return ret
			raise StopIteration()
else:
	class Batched(itertools.batched, _Globals.Subscriptable): ...

class InheritDoc:
	def __init_subclass__(cls) -> _Globals.NoneType:
		for subCls in cls.__bases__:
			if getattr(subCls, "__doc__", None) is not None and len(subCls.__doc__) > 3:
				cls.__doc__ = subCls.__doc__
		return super().__init_subclass__()

class Chain(InheritDoc, itertools.chain, _Globals.Subscriptable): ...
class Count(InheritDoc, itertools.count, _Globals.Subscriptable): ...
class DropWhile(InheritDoc, itertools.dropwhile, _Globals.Subscriptable): ...
class IterSlice(InheritDoc, itertools.islice, _Globals.Subscriptable): ...
class Product(InheritDoc, itertools.product, _Globals.Subscriptable): ...
class Repeat(InheritDoc, itertools.repeat, _Globals.Subscriptable): ...
class TakeWhile(InheritDoc, itertools.takewhile, _Globals.Subscriptable): ...
class ZipLongest(InheritDoc, itertools.zip_longest, _Globals.Subscriptable): ...