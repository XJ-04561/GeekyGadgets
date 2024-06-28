
from collections.abc import Iterable
from typing import Any, SupportsIndex
from GeekyGadgets.Globals import *
from GeekyGadgets.Threads import RLock
from GeekyGadgets.Classy import Default
from GeekyGadgets.Iterators import Chain

__all__ = ("LimitedDict",)

_NOT_SET = object()
_DEFAULT_LIMIT = 10000
_T = TypeVar("_T")
_F = TypeVar("_F")
_S = TypeVar("_S")

def useLock(func : Callable):
	def _func_wrapper(self, *args, **kwargs):
		with self._lock:
			return func(self, *args, **kwargs)
	update_wrapper(_func_wrapper, func)
	_func_wrapper.usesLock = True
	return _func_wrapper

def preShave(func : Callable):
	def _func_wrapper(self, *args, **kwargs):
		# print(_func_wrapper, func, id(_func_wrapper), id(func), self, args, kwargs)
		self.shave()
		return func(self, *args, **kwargs)
	update_wrapper(_func_wrapper, func)
	_func_wrapper.shaves = True
	return _func_wrapper

def postShave(func : Callable):
	def _func_wrapper(self, *args, **kwargs):
		# print(_func_wrapper, func, id(_func_wrapper), id(func), self, args, kwargs)
		ret = func(self, *args, **kwargs)
		self.shave()
		return ret
	update_wrapper(_func_wrapper, func)
	_func_wrapper.shaves = True
	return _func_wrapper

class Pair(tuple):
	def __new__(cls, iterable: Iterable[_F,_S] = ...) -> "Pair[_F,_S]":
		iterable = tuple(iterable)
		if len(iterable) == 2:
			return super().__new__(cls, iterable)
		else:
			raise ValueError(f"`Pair` can only be created from an iterable 2 values in length. Not {len(iterable)} values.")

class Freezer:

	_freezers : dict

	def __init__(self):
		self._freezers = {}

	def __get__(self, instance, owner=None):
		from GeekyGadgets.Threads import current_thread
		return self._freezers.get(current_thread())
	
	def __set__(self, instance, value):
		from GeekyGadgets.Threads import current_thread
		self._freezers[current_thread()] = value
	
	def __delete__(self, instance, owner=None):
		from GeekyGadgets.Threads import current_thread
		del self._freezers[current_thread()]

class Spaces(ABC):

	@abstractmethod
	def __getattribute__(self, name: str) -> Any:
		return super().__getattribute__(name)
	@abstractmethod
	def __setattr__(self, name: str, value: Any) -> None:
		return super().__setattr__(name, value)
	@abstractmethod
	def __getitem__(self, key: str):
		return super().__getitem__(key)
	@abstractmethod
	def __setitem__(self, key: str, value: Any):
		return super().__setitem__(key, value)
	
	def __iter__(self : "_D[_V]") -> "Generator[tuple[str,_V]]":
		for name, value in dict.items(self):
			yield (name, value)

_V = TypeVar("_V")
_D = TypeVar("_D", bound=Spaces)

class LinkedSpace(Spaces):

	def __init__(self, source : object, /):
		SETATTR(self, "__source__", source)
	
	def __getitem__(self, key):
		return getattr(self, key)
	
	def __setitem__(self, key, value) -> None:
		return setattr(self, key, value)
	
	def __contains__(self, name):
		return hasattr(GETATTR(self, "__source__"), name)

	def __getattribute__(self, name: str) -> Any:
		return getattr(GETATTR(self, "__source__"), name)
	
	def __setattr__(self, name: str, value : Any) -> None:
		return setattr(GETATTR(self, "__source__"), name, value)

class NameSpace(dict, Spaces):

	@overload
	def __init__(self, /, **kwargs): ...
	@overload
	def __init__(self, iterable : Iterable[tuple[str,Any]]|dict|None, /, **kwargs): ...
	def __init__(self, iterable : Iterable[tuple[str,Any]]|dict|None=None, /, **kwargs):
		
		if iterable is None:
			super().__init__(**kwargs)
		else:
			super().__init__(iterable, **kwargs)
	
	def __str__(self):
		return " ".join(map("{0[0]}={0[1]!r}".format, self))

	def __getitem__(self, key):
		ret = dict.get(self, key, NULL)
		if ret is NULL:
			raise NameError(f"{self!r} has no entry named {key!r}")
		return ret
	
	def __setitem__(self, key, value) -> None:
		dict.__setitem__(self, key, value)
	
	def __getattribute__(self, name: str) -> Any:
		if name.startswith("_"):
			return object.__getattribute__(self, name)
		else:
			return self[name]
	
	def __setattr__(self, name: str, value : Any) -> None:
		self[name] = value

class NullSpace(Spaces):

	def __getattribute__(self, name: str) -> Any:
		return NULL
	
	def __setattr__(self, name: str, value: Any) -> None:
		pass
	
	def __getitem__(self, key: Any) -> Any:
		return NULL
	
	def __setitem__(self, key: Any, value: Any) -> None:
		pass

class HybridSpace(NameSpace, LinkedSpace):
	
	__link_spaces__ : list[LinkedSpace]

	@overload
	def __init__(self, /, **kwargs): ...
	@overload
	def __init__(self, source : object, /, **kwargs): ...
	@overload
	def __init__(self, source : object, iterable : Iterable, /, **kwargs): ...
	def __init__(self, source : object=None, iterable=None, /, **kwargs):
		SETATTR(self, "__link_spaces__", [LinkedSpace(self, source)] if source is not None else [])
		NameSpace.__init__(self, iterable, **kwargs)

	def __getitem__(self, key):
		ret = dict.get(self, key, NULL)
		if ret is NULL:
			for ls in reversed(GETATTR(self, "__link_spaces__")):
				if key in ls:
					return ls[key]
		return ret
	
	def __getattribute__(self, name: str) -> Any:
		ret = dict.get(self, name, NULL)
		if ret is NULL:
			for ls in reversed(GETATTR(self, "__link_spaces__")):
				if name in ls:
					return ls[name]
		return ret
	
	def __or__(self, iterable : Iterable) -> "HybridSpace":
		if isinstance(iterable, NameSpace):
			for name, value in dict.items(iterable):
				self[name] = value
		elif isinstance(iterable, LinkedSpace):
			GETATTR(self, "__link_spaces__").append(iterable)
		elif isinstance(iterable, dict):
			for name, value in iterable.items():
				self[name] = value
		elif isinstance(iterable, Iterable):
			for name, value in iterable:
				self[name] = value
		else:
			return NotImplemented
		return self
	
	def __ior__(self, iterable : Iterable) -> "HybridSpace":
		return self | iterable


class LimitedIterable(Subscriptable):
	"""An iterable type that imposes a size-limit on its instances, or instances of its subclasses. It and 
	its subclasses uses the method `shave` to correct the iterable. `shave` in turn uses the method `shift` to remove 
	an item, the property `size` to check the size of the iterable instance, and the attribute `LIMIT` 
	as a size-limit (inclusive).
	
	`shave` can't be overrided, but `shift` and `size` can. This is because `size` determines how the size 
	is defined (default is what is returned by `len`), and `shift` chooses which item(s) to remove. All `shave` does 
	is keep calling `shift` until `size` is lower or equal to `LIMIT`.

	It would be wise when subclassing to define your own `shift` method, to ensure proper behavior."""
	
	LIMIT : int
	
	_lock : RLock = cached_property(lambda self: RLock())

	size : int = property(len)
	
	@overload
	def __init__(self, /): ...
	@overload
	def __init__(self, /, *, limit : int=10000): ...
	@overload
	def __init__(self, iterable : Iterable, /): ...
	@overload
	def __init__(self, iterable : Iterable, /, *, limit : int=10000): ...
	@postShave
	def __init__(self, *args, limit : int=10000, **kwargs):
		self.LIMIT = limit
		super().__init__(*args, **kwargs)
	
	def __init_subclass__(cls) -> None:
		super().__init_subclass__()
		if getattr(cls.shift, "usesLock", False) is not True:
			cls.shift = useLock(cls.shift)

	def __repr__(self) -> str:
		return f"<'{self.__class__.__qualname__}' object at {id(self):#x} filled to {self.size}/{self.LIMIT}>"

	def shift(self : "LimitedIterable"):
		with self._lock:
			if hasattr(self, "remove"):
				self.remove(next(iter(self)))
			elif hasattr(self, "pop"):
				if isinstance(self, dict):
					self.pop(next(iter(self.keys())))
				else:
					self.pop(0)
			else:
				raise TypeError(f"Can't remove first element of {self} as it does not implement `remove` or `pop`")

	@final
	def shave(self) -> int:
		"""Checks `self.size` and removes elements until it is within the set `LIMIT`. Returns the difference in 
		`self.size` from before until return.
		
		### Use this after changing the size of the object!"""
		with self._lock:
			start = self.size
			while self.size > self.LIMIT:
				self.shift()
			return self.size - start

class LimitedList(LimitedIterable, list):

	def shift(self : "LimitedList[_T]") -> _T:
		return self.pop(0)

	@postShave
	def append(self, object: Any) -> None:
		return super().append(object)
	
	@postShave
	def extend(self, iterable: Iterable) -> None:
		return super().extend(iterable)
	
	@postShave
	def insert(self, index: SupportsIndex, object: Any) -> None:
		return super().insert(index, object)

class LimitedDict(LimitedIterable, dict):

	def shift(self : "LimitedDict[_T]") -> _T:
		with self._lock:
			try:
				return self.pop(next(iter(self.keys())))
			except StopIteration:
				raise KeyError(f"{self} is empty.")

	@postShave
	def setdefault(self: "LimitedDict", key: Any, default: Any=None, /) -> Any:
		return super().setdefault(key, default)
	
	@overload
	def update(self: dict, m: SupportsKeysAndGetItem, /, **kwargs: Any) -> None: ...
	@overload
	def update(self: dict, m: Iterable[tuple], /, **kwargs: Any) -> None: ...
	@overload
	def update(self: dict, **kwargs: Any) -> None: ...
	@postShave
	def update(self, m, /, **kwargs):
		return super().update(m, **kwargs)

	@postShave
	def __setitem__(self, key: Any, value: Any) -> None:
		return super().__setitem__(key, value)

class LimitedSet(LimitedIterable, set):

	def shift(self : "LimitedSet[_T]") -> _T:
		self.remove(out := next(iter(self)))
		return out

	@postShave
	def add(self, element: Any) -> None:
		return super().add(element)
	
	@postShave	
	def update(self, *s: Iterable) -> None:
		return super().update(*s)
	
	@postShave	
	def difference_update(self, *s: Iterable[Any]) -> None:
		return super().difference_update(*s)

	@postShave
	def intersection_update(self, *s: Iterable[Any]) -> None:
		return super().intersection_update(*s)

	@postShave
	def symmetric_difference_update(self, s: Iterable) -> None:
		return super().symmetric_difference_update(s)