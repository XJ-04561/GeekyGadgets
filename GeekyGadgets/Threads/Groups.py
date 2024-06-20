
from GeekyGadgets.Threads.Globals import *
from GeekyGadgets.Threads.Thread import *

__all__ = ("ThreadGroup",)

class ThreadGroup:
	
	_dict : dict[str,"Thread"]

	writeLock : RLock
	names : list[str]

	def __init__(self, iterable : Iterable["Thread"]|Iterator["Thread"]=[]):
		self.writeLock = RLock()
		with self.writeLock:
			self._dict = {thread.name:thread for thread in iterable}
			for thread in self._dict.values():
				thread.group = self

		if not all(isinstance(t, Thread) for t in self):
			offenders = list(repr(t) for t in self if not isinstance(t, Thread))
			if len(offenders) == 1:
				raise TypeError(f"Item {offenders[0]} is not an instance of {Thread}")
			else:
				raise TypeError(f"Items {', '.join(offenders)} are not instances of {Thread}")

	def __iter__(self):
		for thread in self._dict.values():
			yield thread

	def __getitem__(self, key : int|str) -> "Thread":
		return self._dict[self.names[key]] if isinstance(key, int) else self._dict[key]
	
	@property
	def names(self) -> list[str]:
		return list(self._dict.keys())

	def add(self, thread : "Thread") -> int:
		with self.writeLock:
			self._dict[thread.name] = thread
		return len(self.names)
	
	@overload
	def __or__(self, other : "ThreadGroup") -> "ThreadGroup": ...
	@overload
	def __or__(self, other : Iterable["Thread"]) -> "ThreadGroup": ...
	def __or__(self, other):
		from GeekyGadgets.Iterators import Chain
		return ThreadGroup(Chain(self, other))

	def wait(self, timeout : float|None=None) -> bool:
		"""Wait for all started threads in the group to finish. Returns `True` if all threads in the group have been 
		started and finished running. If at least one thread has yet to be started and/or finished, this will return 
		`False`. `timeout` is passed on to Thread.join(timeout=timeout)."""
		allFinished = True
		threads = tuple(self)
		for thread in threads:
			if thread.ident is None:
				allFinished = False
			else:
				thread.join(timeout=timeout)
				if thread.is_alive():
					allFinished = False
		return allFinished
	
	def start(self):
		for thread in self:
			thread.start()
	
	@property
	def alive(self):
		return tuple(t.alive for t in self)
	
	@property
	def anyAlive(self):
		return any(t.alive for t in self)
	
	@property
	def allAlive(self):
		return all(t.alive for t in self)
	
	@property
	def futures(self):
		"""`tuple` of the threads' `Future` objects."""
		return tuple(t.future for t in self)
	
	@property
	def results(self):
		"""`tuple` of the threads' return-values, where the values of threads who have yet to 
		return are replaced with `None`."""
		return tuple(t.future.call() if t.future.ready else None for t in self)
