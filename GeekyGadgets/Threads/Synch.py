
from GeekyGadgets.Threads.Globals import *


__all__ = ("DelayedCall", "Lock", "RLock", "RLockType", "Condition", "Semaphore", "BoundedSemaphore", "Event", "Barrier",
		   "BrokenBarrierError", "LockedDict")

class RLockType: pass
RLockType = type(RLock())

class State:
	
	_locks : dict[int,Lock]

	frozen : bool

	def __init__(self) -> None:
		self._locks = {}

	def __enter__(self):
		self.freeze()
		return self
	
	def __exit__(self, exc_type, exc_value, traceback):
		self.thaw()

	@property
	def frozen(self):
		if current_thread().ident in self._locks:
			if self._locks[current_thread().ident].acquire(False):
				self._locks[current_thread().ident].release()
				return False
			else:
				return True
		else:
			return False

	def freeze(self):
		if current_thread().ident not in self._locks:
			self._locks[current_thread().ident] = Lock()
		return self._locks[current_thread().ident].acquire(False)
	
	def thaw(self):
		if current_thread().ident not in self._locks:
			self._locks[current_thread().ident] = Lock()
		return self._locks[current_thread().ident].release()

_T = TypeVar("_T")
_KT = TypeVar("_KT")
_VT = TypeVar("_VT")
_NOT_SET = object()

class LockedDict(dict):

	LOCK : Lock = cached_property(lambda self:RLock())

	def __init__(self, *args, factory=None, **kwargs):
		self.factory = factory
		assert isinstance(self.LOCK, RLockType)
		super().__init__(self, *args, **kwargs)

	def __getitem__(self, key: Any) -> Any:
		with self.LOCK:
			try:
				return super().__getitem__(key)
			except KeyError as e:
				if self.factory is None:
					raise e
				ret = self[key] = self.factory()
				return ret
	
	def __setitem__(self, key: Any, value: Any) -> None:
		with self.LOCK:
			return super().__setitem__(key, value)

	def __delitem__(self, key: Any) -> None:
		with self.LOCK:
			return super().__delitem__(key)
	
	def keys(self : "LockedDict[_KT,_VT]") -> tuple[_KT]:
		with self.LOCK:
			return tuple(super().keys())
	def values(self : "LockedDict[_KT,_VT]") -> tuple[_VT]:
		with self.LOCK:
			return tuple(super().values())
	def items(self : "LockedDict[_KT,_VT]") -> tuple[_KT,_VT]:
		with self.LOCK:
			return tuple(super().items())
	
	@overload
	def setdefault(self: "LockedDict[_KT, Any | None]", key: _KT, default: None = None, /) -> (Any | None): ...
	@overload
	def setdefault(self: "LockedDict[_KT, _VT]", key: _KT, default: _VT, /) -> _VT: ...
	def setdefault(self, key, default= None, /):
		with self.LOCK:
			return super().setdefault(key, default)

	@overload
	def pop(self: dict, key: Any, /) -> Any: ...
	@overload
	def pop(self: dict, key: Any, default: Any, /) -> Any: ...
	@overload
	def pop(self: dict, key: Any, default: _T, /) -> (Any | _T): ...
	def pop(self, key, default=_NOT_SET, /):
		with self.LOCK:
			if default is _NOT_SET:
				ret = super().pop(key)
			else:
				ret = super().pop(key, default)
			return ret

	def popitem(self) -> tuple:
		with self.LOCK:
			return super().popitem()
		
	def update(self, *args, **kwargs):
		with self.LOCK:
			super().update(*args, **kwargs)