
from GeekyGadgets.Globals import *
from GeekyGadgets.Threads import RLock

_NOT_SET = object()

__all__ = ("LimitedDict",)

class LimitedDict(dict):
	
	
	LIMIT : int = 10000
	_lock : RLock

	@overload
	def __init__(self, /): ...
	@overload
	def __init__(self, *, limit : int): ...
	@overload
	def __init__(self, iterable : Iterable|dict, /): ...
	@overload
	def __init__(self, iterable : Iterable|dict, /, *, limit : int): ...
	def __init__(self, iterable=None, /, *, limit=None):
		self._lock = RLock()
		self.N = 0
		if limit is not None:
			self.LIMIT = limit
		if iterable is None:
			pass
		elif isinstance(iterable, Iterable):
			if isinstance(iterable, dict):
				iterable = iterable.items()
			for key, value in iterable:
				self[key] = value
	
	def __setitem__(self, key, value):
		with self._lock:
			if key not in self:
				while self.N >= self.LIMIT:
					self.pop(next(iter(self)))
				self.N += 1
			super().__setitem__(key, value)

	def setdefault(self, key, value):
		with self._lock:
			if key not in self:
				while self.N >= self.LIMIT:
					self.pop(next(iter(self)))
				self.N += 1
				super().setdefault(key, value)
	
	def __delitem__(self, key):
		with self._lock:
			if key in self:
				self.N -= 1
			super().__delitem__(key)

	def update(self, other : dict|Iterable[tuple[Any,Any]]):
		if isinstance(other, dict):
			other = other.items()
		for key, value in other:
			self[key] = value
	
	def clear(self):
		for key in tuple(self.keys()):
			self.pop(key)

	def pop(self, key, default=_NOT_SET):
		with self._lock:
			if key in self:
				self.N -= 1
			
			if default is _NOT_SET:
				return super().pop(key)
			else:
				return super().pop(key, default)
			
	def popitem(self) -> tuple:
		with self._lock:
			self.N -= 1
			return super().popitem()