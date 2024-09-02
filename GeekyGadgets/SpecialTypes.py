
import GeekyGadgets.Globals as _GL
from dataclasses import dataclass

import GeekyGadgets.Threads as _Threads
import GeekyGadgets.Functions as _Funcs

__all__ = (
	"Percent", "Pair", "Freezer",
	"Spaces", "LinkedSpace", "NameSpace", "NullSpace", "HybridSpace",
	"LimitedIterable", "LimitedList", "LimitedDict", "LimitedSet"
)

_T = _GL.TypeVar("_T")
_F = _GL.TypeVar("_F")
_S = _GL.TypeVar("_S")

def useLock(func : _GL.Callable):
	def _func_wrapper(self, *args, **kwargs):
		with self._lock:
			return func(self, *args, **kwargs)
	_GL.update_wrapper(_func_wrapper, func)
	_func_wrapper.usesLock = True
	return _func_wrapper

def preShave(func : _GL.Callable):
	def _func_wrapper(self, *args, **kwargs):
		# print(_func_wrapper, func, id(_func_wrapper), id(func), self, args, kwargs)
		self.shave()
		return func(self, *args, **kwargs)
	_GL.update_wrapper(_func_wrapper, func)
	_func_wrapper.shaves = True
	return _func_wrapper

def postShave(func : _GL.Callable):
	def _func_wrapper(self, *args, **kwargs):
		# print(_func_wrapper, func, id(_func_wrapper), id(func), self, args, kwargs)
		ret = func(self, *args, **kwargs)
		self.shave()
		return ret
	_GL.update_wrapper(_func_wrapper, func)
	_func_wrapper.shaves = True
	return _func_wrapper

class HashedSet(set):
	
	_lock : _Threads.RLock
	_hash : int

	def __new__(cls, *args, **kwargs):
		obj = super().__new__(cls, *args, **kwargs)
		obj._lock = _Threads.RLock()
		return obj
	
	def __hash__(self):
		return self._hash

	def add(self, element: _GL.Any) -> _GL.NoneType:
		with self._lock:
			super().add(element)
			self._hash = _Funcs.forceHash(self)

	def discard(self, element: _GL.Any) -> _GL.NoneType:
		with self._lock:
			super().discard(element)
			self._hash = _Funcs.forceHash(self)
	
	def remove(self, element: _GL.Any) -> _GL.NoneType:
		with self._lock:
			super().remove(element)
			self._hash = _Funcs.forceHash(self)
	
	def clear(self) -> _GL.NoneType:
		with self._lock:
			super().clear()
			self._hash = _Funcs.forceHash(self)
	
	def update(self, *s: _GL.Iterable) -> _GL.NoneType:
		with self._lock:
			super().update(*s)
			self._hash = _Funcs.forceHash(self)
	
	def difference_update(self, *s: _GL.Iterable[_GL.Any]) -> _GL.NoneType:
		with self._lock:
			super().difference_update(*s)
			self._hash = _Funcs.forceHash(self)
	
	def intersection_update(self, *s: _GL.Iterable[_GL.Any]) -> _GL.NoneType:
		with self._lock:
			super().intersection_update(*s)
			self._hash = _Funcs.forceHash(self)
	
	def symmetric_difference_update(self, s: _GL.Iterable) -> _GL.NoneType:
		with self._lock:
			super().symmetric_difference_update(s)
			self._hash = _Funcs.forceHash(self)

HashedSet._hash = hash(HashedSet)

class Percent:
	
	def __new__(cls, value : _GL.Number) -> None:
		if isinstance(value, cls):
			return super().__new__(cls, value.value)
		else:
			return super().__new__(cls, value)

	def __str__(self):
		return str(100 * float(self)) + "%"
	
	def __format__(self, format_spec: str) -> str:
		return format(100 * float(self), format_spec) + "%"
	
	def __add__(self, value: float) -> "Percent":
		return type(self)(self.value + value)
	def __radd__(self, value: float) -> "Percent":
		return type(self)(value + self.value)
	def __mul__(self, value: float) -> "Percent":
		return type(self)(self.value * value)
	def __rmul__(self, value: float) -> "Percent":
		return type(self)(value * self.value)
	def __truediv__(self, value: float) -> "Percent":
		return type(self)(self.value / value)
	def __rtruediv__(self, value: float) -> "Percent":
		return type(self)(value / self.value)
	def __floordiv__(self, value: float) -> "Percent":
		return type(self)(((100 * self.value) // value) / 100)
	def __rfloordiv__(self, value: float) -> "Percent":
		return type(self)((value // (100 * self.value)) / 100)
	def __mod__(self, value: float) -> "Percent":
		return type(self)(self.value % value)
	def __rmod__(self, value: float) -> "Percent":
		return type(self)(value % self.value)
	def __pow__(self, value: float) -> "Percent":
		return type(self)(self.value ** value)
	def __rpow__(self, value: float) -> "Percent":
		return type(self)(value ** self.value)
	
	def __abs__(self) -> "Percent":
		return type(self)(abs(self.value))
_GL.Number.register(Percent)

class Pair(tuple):
	def __new__(cls, iterable: _GL.Iterable[_F,_S] = ...) -> "Pair[_F,_S]":
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

class Spaces(_GL.ABC):

	@_GL.abstractmethod
	def __getattribute__(self, name: str) -> _GL.Any:
		return super().__getattribute__(name)
	@_GL.abstractmethod
	def __setattr__(self, name: str, value: _GL.Any) -> None:
		return super().__setattr__(name, value)
	@_GL.abstractmethod
	def __getitem__(self, key: str):
		return super().__getitem__(key)
	@_GL.abstractmethod
	def __setitem__(self, key: str, value: _GL.Any):
		return super().__setitem__(key, value)
	
	def __iter__(self : "_D[_V]") -> "_GL.Generator[tuple[str,_V]]":
		for name, value in dict.items(self):
			yield (name, value)

_V = _GL.TypeVar("_V")
_D = _GL.TypeVar("_D", bound=Spaces)

class LinkedSpace(Spaces):

	def __init__(self, source : object, /):
		_GL.SETATTR(self, "__source__", source)
	
	def __getitem__(self, key):
		return getattr(self, key)
	
	def __setitem__(self, key, value) -> None:
		return setattr(self, key, value)
	
	def __contains__(self, name):
		return hasattr(_GL.GETATTR(self, "__source__"), name)

	def __getattribute__(self, name: str) -> _GL.Any:
		return getattr(_GL.GETATTR(self, "__source__"), name)
	
	def __setattr__(self, name: str, value : _GL.Any) -> None:
		return setattr(_GL.GETATTR(self, "__source__"), name, value)

class NameSpace(dict, Spaces):

	@_GL.overload
	def __init__(self, /, **kwargs): ...
	@_GL.overload
	def __init__(self, iterable : _GL.Iterable[tuple[str,_GL.Any]]|dict|None, /, **kwargs): ...
	def __init__(self, iterable : _GL.Iterable[tuple[str,_GL.Any]]|dict|None=None, /, **kwargs):
		
		if iterable is None:
			super().__init__(**kwargs)
		else:
			super().__init__(iterable, **kwargs)
	
	def __str__(self):
		return " ".join(map("{0[0]}={0[1]!r}".format, self))

	def __getitem__(self, key):
		ret = dict.get(self, key, _GL.NULL)
		if ret is _GL.NULL:
			raise KeyError(f"{self!r} has no entry named {key!r}")
		return ret
	
	def __setitem__(self, key, value) -> None:
		dict.__setitem__(self, key, value)
	
	def __getattribute__(self, name: str) -> _GL.Any:
		if name.startswith("_"):
			return super().__getattribute__(name)
		try:
			return self[name]
		except KeyError as e:
			try:
				return super().__getattribute__(name)
			except AttributeError:
				raise e
	
	def __setattr__(self, name: str, value : _GL.Any) -> None:
		self[name] = value

@dataclass(init=False, frozen=True)
class ImmutableNameSpace(NameSpace): ...

class NullSpace(Spaces):

	def __getattribute__(self, name: str) -> _GL.Any:
		return _GL.NULL
	
	def __setattr__(self, name: str, value: _GL.Any) -> None:
		pass
	
	def __getitem__(self, key: _GL.Any) -> _GL.Any:
		return _GL.NULL
	
	def __setitem__(self, key: _GL.Any, value: _GL.Any) -> None:
		pass

class HybridSpace(NameSpace, LinkedSpace):
	
	__link_spaces__ : list[LinkedSpace]

	@_GL.overload
	def __init__(self, /, **kwargs): ...
	@_GL.overload
	def __init__(self, source : object, /, **kwargs): ...
	@_GL.overload
	def __init__(self, source : object, iterable : _GL.Iterable, /, **kwargs): ...
	def __init__(self, source : object=None, iterable=None, /, **kwargs):
		_GL.SETATTR(self, "__link_spaces__", [LinkedSpace(self, source)] if source is not None else [])
		NameSpace.__init__(self, iterable, **kwargs)

	def __getitem__(self, key):
		ret = dict.get(self, key, _GL.NULL)
		if ret is _GL.NULL:
			for ls in reversed(_GL.GETATTR(self, "__link_spaces__")):
				if key in ls:
					return ls[key]
		return ret
	
	def __getattribute__(self, name: str) -> _GL.Any:
		ret = dict.get(self, name, _GL.NULL)
		if ret is _GL.NULL:
			for ls in reversed(_GL.GETATTR(self, "__link_spaces__")):
				if name in ls:
					return ls[name]
		return ret
	
	def __or__(self, iterable : _GL.Iterable) -> "HybridSpace":
		if isinstance(iterable, NameSpace):
			for name, value in dict.items(iterable):
				self[name] = value
		elif isinstance(iterable, LinkedSpace):
			_GL.GETATTR(self, "__link_spaces__").append(iterable)
		elif isinstance(iterable, dict):
			for name, value in iterable.items():
				self[name] = value
		elif isinstance(iterable, _GL.Iterable):
			for name, value in iterable:
				self[name] = value
		else:
			return NotImplemented
		return self
	
	def __ior__(self, iterable : _GL.Iterable) -> "HybridSpace":
		return self | iterable


class LimitedIterable(_GL.Subscriptable):
	"""An iterable type that imposes a size-limit on its instances, or instances of its subclasses. It and 
	its subclasses uses the method `shave` to correct the iterable. `shave` in turn uses the method `shift` to remove 
	an item, the property `size` to check the size of the iterable instance, and the attribute `LIMIT` 
	as a size-limit (inclusive).
	
	`shave` can't be overrided, but `shift` and `size` can. This is because `size` determines how the size 
	is defined (default is what is returned by `len`), and `shift` chooses which item(s) to remove. All `shave` does 
	is keep calling `shift` until `size` is lower or equal to `LIMIT`.

	It would be wise when subclassing to define your own `shift` method, to ensure proper behavior."""
	
	LIMIT : int
	
	_lock : _Threads.RLock = _GL.cached_property(lambda self: _Threads.RLock())

	size : int = property(len)
	
	@_GL.overload
	def __init__(self, /): ...
	@_GL.overload
	def __init__(self, /, *, limit : int=10000): ...
	@_GL.overload
	def __init__(self, iterable : _GL.Iterable, /): ...
	@_GL.overload
	def __init__(self, iterable : _GL.Iterable, /, *, limit : int=10000): ...
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

	@_GL.final
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
	def append(self, object: _GL.Any) -> None:
		return super().append(object)
	
	@postShave
	def extend(self, iterable: _GL.Iterable) -> None:
		return super().extend(iterable)
	
	@postShave
	def insert(self, index: _GL.SupportsIndex, object: _GL.Any) -> None:
		return super().insert(index, object)

class LimitedDict(LimitedIterable, dict):

	def shift(self : "LimitedDict[_T]") -> _T:
		with self._lock:
			try:
				return self.pop(next(iter(self.keys())))
			except StopIteration:
				raise KeyError(f"{self} is empty.")

	@postShave
	def setdefault(self: "LimitedDict", key: _GL.Any, default: _GL.Any=None, /) -> _GL.Any:
		return super().setdefault(key, default)
	
	@_GL.overload
	def update(self: dict, m: _GL.Mapping, /, **kwargs: _GL.Any) -> None: ...
	@_GL.overload
	def update(self: dict, m: _GL.Iterable[tuple], /, **kwargs: _GL.Any) -> None: ...
	@_GL.overload
	def update(self: dict, **kwargs: _GL.Any) -> None: ...
	@postShave
	def update(self, m, /, **kwargs):
		return super().update(m, **kwargs)

	@postShave
	def __setitem__(self, key: _GL.Any, value: _GL.Any) -> None:
		return super().__setitem__(key, value)

class LimitedSet(LimitedIterable, set):

	def shift(self : "LimitedSet[_T]") -> _T:
		self.remove(out := next(iter(self)))
		return out

	@postShave
	def add(self, element: _GL.Any) -> None:
		return super().add(element)
	
	@postShave	
	def update(self, *s: _GL.Iterable) -> None:
		return super().update(*s)
	
	@postShave	
	def difference_update(self, *s: _GL.Iterable[_GL.Any]) -> None:
		return super().difference_update(*s)

	@postShave
	def intersection_update(self, *s: _GL.Iterable[_GL.Any]) -> None:
		return super().intersection_update(*s)

	@postShave
	def symmetric_difference_update(self, s: _GL.Iterable) -> None:
		return super().symmetric_difference_update(s)