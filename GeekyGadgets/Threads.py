

from GeekyGadgets.Globals import *
from GeekyGadgets.Logging import Logged
from GeekyGadgets.Classy import Default

import sqlite3
from queue import Queue, Empty as EmptyQueueException
from threading import (Timer as DelayedCall, Lock, RLock, Condition, Semaphore, BoundedSemaphore, Event, Barrier,
					   BrokenBarrierError, Thread as _Thread, ThreadError)
from threading import (setprofile as set_profile, setprofile_all_threads as set_profile_all_threads,
					   getprofile as get_profile, settrace as set_trace_function,
					   settrace_all_threads as set_trace_all_threads, gettrace as get_trace_function, current_thread,
					   active_count, enumerate as enumerate_threads, main_thread)

__all__ = (
	"set_profile", "set_profile_all_threads", "get_profile", "set_trace_function", "set_trace_all_threads",
	"get_trace_function", "current_thread", "active_count", "enumerate_threads", "main_thread",
	"DummyLock", "ThreadGroup", "ThreadConnection", "DelayedCall", "Lock", "RLock", "Condition", "Semaphore",
	"BoundedSemaphore", "Event", "Barrier", "BrokenBarrierError", "Thread", "CalledBeforeRealized", "Future"
)

class CalledBeforeRealized(ThreadError):
	def __init__(self, thread : "Thread"):
		self.args = (f"Tried to `call` future of {thread} before it had been realized.", )

class _NOT_REALIZED: pass
class Future:
	
	value : Any
	thread : "Thread"
	awaiter : Condition

	def __init__(self, thread):
		self.value = _NOT_REALIZED
		self.thread = thread
		self.awaiter = Condition()

	def __await__(self):
		

	@property
	def ready(self):
		return self.value is not _NOT_REALIZED

	def realize(self, value):
		assert current_thread() == self.thread, f"Only the thread assigned to this future can realize this future. {current_thread()=} and {self.thread=}"
		self.value = value
	
	def call(self):
		if self.value is _NOT_REALIZED:
			raise CalledBeforeRealized(thread=self.thread)
		else:
			return self.value

class ThreadGroup:
	
	_dict : dict[str,"Thread"]
	_names : list[str]

	writeLock : RLock
	names : list[str]

	def __init__(self, iterable : Iterable["Thread"]|Iterator["Thread"]=[]):
		self.writeLock = RLock()
		with self.writeLock:
			self._dict = {thread.name:thread for thread in iterable}
			self._names = list(self._dict.keys())

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
		return self._dict[self._names[key]] if isinstance(key, int) else self._dict[key]
	
	@Default["_names"]
	def names(self) -> list[str]:
		return [name for name in self._names]

	def add(self, thread : "Thread") -> int:
		with self.writeLock:
			if thread.name not in self._dict:
				self._names.append(thread.name)
				i = len(self._names) - 1
			else:
				i = self._names.index(thread.name)
			self._dict[thread.name] = thread
		return i
	
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
		return tuple(map(Thread.is_alive, self))
	
	@property
	def anyAlive(self):
		return any(t.is_alive for t in self)
	
	@property
	def allAlive(self):
		return all(t.is_alive for t in self)

class Thread(_Thread):
	
	group : ThreadGroup
	future : Future
	"""An object to access the """

	def __init__(self, group: ThreadGroup | None = None, target: Callable[[Any], object] | None = None, name: str | None = None, args: Iterable[Any] = [], kwargs: Mapping[str, Any] | None = None, *, daemon: bool | None = None) -> None:
		super().__init__(target=target, name=name, args=args, kwargs=kwargs, daemon=daemon)
		self.group = group
		self.group.add(self)
		self.future = Future(self)

class DummyLock:
	def acquire(self, blocking: bool = None, timeout: float = None):
		return True
	def release(self):
		pass
	@property
	def locked(self):
		return False


class CursorLike:
	def __init__(self, data : list):
		self.data = data
		self.dataIterator = iter(data)
	def __iter__(self):
		for row in self.data:
			yield row
	def __next__(self):
		return next(self.dataIterator)
	def fetchone(self):
		if self.data:
			return self.data[0]
		else:
			return None
	def fetchall(self):
		return self.data

class ThreadConnection(Logged):

	LOG : logging.Logger
	OPEN_DATABASES : dict[tuple[str, type],list["ThreadConnection",set[int]]]= {}
	REFERENCE : "ThreadConnection"
	CACHE_LOCK = Lock()
	CLOSED : bool

	queue : Queue[list[str,list,Lock, list]]
	queueLock : Lock
	running : bool
	
	filename : str
	_thread : Thread
	@property
	def _connection(self) -> "ThreadConnection":
		return self

	def __init__(self, filename : str, factory=sqlite3.Connection, identifier=0, *, logger : logging.Logger=None):
		if logger:
			self.LOG = logger
		with self.CACHE_LOCK:
			if (filename, factory) in self.OPEN_DATABASES and self.OPEN_DATABASES[filename, factory][0].running:
				ref = self.OPEN_DATABASES[filename, factory][0]
				self.OPEN_DATABASES[filename, factory][1].add(identifier)
				self.REFERENCE = ref
				if ref.running:
					return
				else:
					self.__dict__.pop("REFERENCE", None)
			
			self.OPEN_DATABASES[filename, factory] = [self, {identifier}]
			
			self.running = True
			self.CLOSED = False
			self.queue = Queue()
			self.queueLock = Lock()
			self.filename = filename
			self._factory = factory
			self._thread = Thread(target=self.mainLoop, daemon=True)
			self._thread.start()

	def __getattr__(self, name):
		return getattr(self.REFERENCE, name)

	def mainLoop(self):
		try:
			_connection = sqlite3.connect(self.filename, factory=self._factory)
			while self.running:
				try:
					string, params, lock, results = self.queue.get(timeout=15)
					if string is None and lock is None:
						continue
					try:
						results.extend(_connection.execute(string, params).fetchall())
					except Exception as e:
						self.LOG.exception(e)
						try:
							results.append(e)
						except:
							pass
					try:
						lock.release()
					except:
						pass
					self.queue.task_done()
				except EmptyQueueException:
					pass
				except Exception as e:
					self.LOG.exception(e)
			self.running = False
			_connection.close()
		except Exception as e:
			self.running = False
			_connection.close()
			self.LOG.exception(e)
			try:
				results.append(e)
				lock.release()
			except:
				pass
			for _ in range(self.queue.unfinished_tasks):
				string, params, lock, results = self.queue.get(timeout=15)
				if lock is not None:
					lock.release()

	def execute(self, string : str, params : list=[]):
		lock = Lock()
		lock.acquire()
		results = []
		with self.queueLock:
			self.queue.put([string, params, lock, results])
		
		if not self._thread.is_alive() or not self.running:
			raise sqlite3.ProgrammingError("Cannot operate on a closed database.")
		
		lock.acquire()
		
		if results and isinstance(results[-1], Exception):
			raise results[-1]
		
		return CursorLike(results)
	
	def executemany(self, *statements : tuple[str, list]):
		fakeLock = lambda :None
		fakeLock.release = lambda :None

		with self.queueLock:
			results = [[] for _ in len(statements)]
			for i, statement in enumerate(statements[:-1]):
				self.queue.put([*statement, fakeLock, results[i]])
			lock = Lock()
			lock.acquire()
			self.queue.put([*statements[-1], lock, results[-1]])
		
		if not self._thread.is_alive() or not self.running:
			raise sqlite3.ProgrammingError("Cannot operate on a closed database.")
		lock.acquire()
		
		if any(r and isinstance(r[-1], Exception) for r in results):
			raise next(filter(lambda r:r and isinstance(r[-1], Exception), results))[-1]
		
		return results

	def close(self, identifier=0):
		import inspect
		from pprint import pformat
		self.LOG.info(f"Database thread at 0x{id(self):X} was closed in stack:\n{pformat(inspect.stack())}")
		with self.CACHE_LOCK:
			self.OPEN_DATABASES[self.filename, self._factory][1].discard(identifier)
			if not self.OPEN_DATABASES[self.filename, self._factory][1]:
				if hasattr(self, "REFERENCE"):
					self.REFERENCE.running = False
				else:
					self.running = False
				self.queue.put([None, None, None, None])
				self._thread.join()
	
	def commit(self):
		self.execute("COMMIT;")

	def __del__(self):
		self.close()