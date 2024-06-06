

from collections.abc import Callable, Iterable, Mapping
from typing import Any
from GeekyGadgets.Globals import *
from threading import Thread as _Thread, current_thread, main_thread

class ThreadGroup: pass

class Thread(_Thread):
	
	group : ThreadGroup

	def __init__(self, group: ThreadGroup | None = None, target: Callable[..., object] | None = None, name: str | None = None, args: Iterable[Any] = ..., kwargs: Mapping[str, Any] | None = None, *, daemon: bool | None = None) -> None:
		super().__init__(None, target, name, args, kwargs, daemon=daemon)
		self.group = group

class DummyLock:
	def acquire(self, blocking: bool = ..., timeout: float = ...):
		return True
	def release(self):
		pass
	@property
	def locked(self):
		return False