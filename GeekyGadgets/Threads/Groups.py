
from GeekyGadgets.Threads.Globals import *
import GeekyGadgets.Classy as Classy

__all__ = ("ThreadGroup",)

class ThreadGroup:

	GROUPS : "LockedDict"

	name : Hashable
	threads : "LockedDict[Hashable,Thread]" = cached_property(lambda self: LockedDict())
	names : tuple[Hashable]

	def __new__(cls, threads : Iterable["Thread"]=(), name : Hashable=None):
		with cls.GROUPS.LOCK:
			if name is None:
				i = 1
				while (name := f"UNNAMED GROUP {i}") in cls.GROUPS:
					i += 1
			if name in cls.GROUPS:
				return cls.GROUPS[name]
			else:
				cls.GROUPS[name] = ret = super().__new__(cls)
				return ret

	def __init__(self, threads : Iterable["Thread"]=(), name : Hashable=None):
		
		if name is not None:
			self.name = name

		for thread in threads:
			self.add(thread)
	
	def __init_subclass__(cls, *args, **kwargs):
		cls.GROUPS = LockedDict()
		return super().__init_subclass__(*args, **kwargs)

	def __iter__(self) -> "Generator[Thread,None,None]":
		for thread in self.threads.values():
			yield thread

	def __getitem__(self, key : int|str) -> "Thread":
		return self.threads[self.names[key]] if isinstance(key, int) else self.threads[key]
	
	@Classy.Default
	def name(self):
		for name, value in self.GROUPS.items():
			if self is value:
				return name
		else:
			raise ValueError(f"Group {self} is unnamed, it should be given a name when created.")

	@property
	def names(self) -> tuple[str]:
		return self.threads.keys()

	def add(self, thread : "Thread") -> int:
		if thread.group is not self:
			thread.group = self
		self.threads[thread.name] = thread
		return len(self.names)
	
	def prune(self):
		for thread in self:
			if not thread.alive:
				self.threads.pop(thread.name, None)

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

try:
	
	from GeekyGadgets.Threads.Synch import LockedDict, RLock
	from GeekyGadgets.Threads.Thread import *
	ThreadGroup.GROUPS = LockedDict()
except ImportError:
	pass