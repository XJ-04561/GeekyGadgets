
from GeekyGadgets.Globals import *
from GeekyGadgets.Threads import RLock
from GeekyGadgets.Classy import Default

_NOT_SET = object()

__all__ = ("LimitedDict",)

_DEFAULT_LIMIT = 10000

def shift(self : "LimitedIterable"):
	with self._lock:
		if hasattr(self, "remove"):
			self.remove[next(iter(self.keys()))]
		elif hasattr(self, "pop"):
			self.pop[next(iter(self.keys()))]
		else:
			raise TypeError(f"Can't remove first element of {self} as it does not implement `remove` or `pop`")

class LimitedIterable:
	"""Subclasses will act as wrappers for their data model parent, so whichever function in the subclass that 
	exists in the data model parent will get proper wrappings from them using `functools.update_wrapper`."""
	
	LIMIT : int
	
	_lock : RLock

	size : int = property(len)
	
	@overload
	def __init__(self, /): ...
	@overload
	def __init__(self, /, *, limit : int=10000): ...
	@overload
	def __init__(self, iterable : Iterable, /): ...
	@overload
	def __init__(self, iterable : Iterable, /, *, limit : int=10000): ...
	def __init__(self, *args, limit : int=10000, **kwargs):
		self.LIMIT = limit
		self._lock = RLock()
		super().__init__(*args, **kwargs)
	
	def __init_subclass__(cls) -> None:
		"""Subclasses will act as wrappers for their data model parent, so whichever function in the subclass that 
		exists in the data model parent will get proper wrappings from them using `functools.update_wrapper`."""
		for base in cls.__bases__:
			if not base is LimitedIterable and getattr(base, "__doc__", ""):
				cls.__doc__ = base.__doc__
				break
		for name, func in vars(cls).items():
			for base in cls.__bases__:
				if base is LimitedIterable or not hasattr(base, name):
					continue
				elif isinstance(func, FunctionType):
					update_wrapper(func, getattr(base, name))
				# elif hasattr(func, "__doc__") and hasattr(getattr(base, name), "__doc__"):
				# 	func.__doc__ = getattr(base, name).__doc__
				break
		
		for base in cls.__bases__:
			if base is LimitedIterable:
				continue
			for name in getattr(base, "__dict__", getattr(base, "__slots__", ())):
				if name in getattr(cls, "__dict__", getattr(cls, "__slots__", ())):
					continue
				elif isinstance(func := getattr(base, name), FunctionType):
					def _func_wrapper(self, *args, **kwargs) -> None:
						ret = func(self, *args, **kwargs)
						self.shave()
						return ret
					update_wrapper(_func_wrapper, func)
					setattr(cls, name, _func_wrapper)
		if not hasattr(cls, "shift"):
			cls.shift = shift

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

class LimitedList(LimitedIterable, list): pass
class LimitedDict(LimitedIterable, dict): pass

	# @overload
	# def __init__(self, /): ...
	# @overload
	# def __init__(self, *, limit : int): ...
	# @overload
	# def __init__(self, iterable : Iterable|dict, /): ...
	# @overload
	# def __init__(self, iterable : Iterable|dict, /, *, limit : int): ...
	# def __init__(self, iterable=None, /, *, limit=None):
	# 	if super().__init__(iterable, limit=limit)
	
	# def __setitem__(self, key, value):
	# 	with self._lock:
	# 		if key not in self:
	# 			while self.N >= self.LIMIT:
	# 				self.pop(next(iter(self)))
	# 			self.N += 1
	# 		super().__setitem__(key, value)

	# def setdefault(self, key, value):
	# 	with self._lock:
	# 		if key not in self:
	# 			while self.N >= self.LIMIT:
	# 				self.pop(next(iter(self)))
	# 			self.N += 1
	# 			super().setdefault(key, value)
	
	# def __delitem__(self, key):
	# 	with self._lock:
	# 		if key in self:
	# 			self.N -= 1
	# 		super().__delitem__(key)

	# def update(self, other : dict|Iterable[tuple[Any,Any]]):
	# 	if isinstance(other, dict):
	# 		other = other.items()
	# 	for key, value in other:
	# 		self[key] = value
	
	# def clear(self):
	# 	for key in tuple(self.keys()):
	# 		self.pop(key)

	# def pop(self, key, default=_NOT_SET):
	# 	with self._lock:
	# 		if key in self:
	# 			self.N -= 1
			
	# 		if default is _NOT_SET:
	# 			return super().pop(key)
	# 		else:
	# 			return super().pop(key, default)
			
	# def popitem(self) -> tuple:
	# 	with self._lock:
	# 		self.N -= 1
	# 		return super().popitem()