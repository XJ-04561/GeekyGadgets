
from GeekyGadgets.Globals import *

_NOT_SET = object()

__all__ = ("LimitedDict")

class LimitedDict(dict):
	
	
	LIMIT : int = 10000
	_lock : threading.Lock

	def __init__(self, *args, **kwargs):
		self._lock = threading.Lock()
		self.N = 0
		if args and isinstance(args[0], int):
			self.LIMIT = args[0]
		elif "limit" in kwargs:
			self.LIMIT = kwargs["limit"]
	
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