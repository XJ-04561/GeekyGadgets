
from GeekyGadgets.Threads.Globals import *


__all__ = ("DelayedCall", "Lock", "RLock", "Condition", "Semaphore", "BoundedSemaphore", "Event", "Barrier",
		   "BrokenBarrierError")

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