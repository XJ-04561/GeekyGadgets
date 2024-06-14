

from GeekyGadgets.Globals import *
from GeekyGadgets.Logging import Logged

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

_NOT_SET = object()

class CalledBeforeRealized(ThreadError):
	def __init__(self, thread : "Thread"):
		self.args = (f"Tried to `call` future of {thread} before it had been realized.", )

class Future:
	"""Starting a `Thread` object returns a `Future` object, which is the object through which the return value of the 
	thread's target function can be acquired. The `Future.thread` attribute is the `Thread` object which created this 
	future, and only that thread can resolve this future (assigning the returned value to its attribute 
	`Future.value`). If the target function of the thread raises and exception, that exception is caught by the 
	thread's function wrapper and is assigned to this future's `Future.exception` attribute, thus resolving the future 
	without setting the value of `Future.value`.
	
	The safe way to use a future is to call the `Future.call` method, as it waits for the future to resolve, and if 
	the target function returned successfully, the value set to `Future.value` is returned. But, if the target 
	function raised an exception, the `Future.call` method will instead raise the same exception that was raised by 
	the target function."""
	
	value : Any
	exception : Exception
	thread : "Thread"
	resolveEvent : Event
	group : "ThreadGroup" = property(lambda self:self.thread.group)

	def __init__(self, thread):
		self.thread = thread
		self.resolveEvent = Event()

	def hold(self, timeout : float=None) -> bool:
		"""Hold until the `Future` object resolves or for as long specified with `timeout`. If `timeout` is `None` or 
		not specified, the function will not return until the Future is resolved. Returns `True` if the `Future` 
		object was resolved, and returns `False` if the timeout was exceeded before it was resolved.
		
		Synonymous with `Future.wait`"""
		return self.resolveEvent.wait(timeout=timeout)
	
	def wait(self, timeout : float=None) -> bool:
		"""Wait until the `Future` object resolves or for as long specified with `timeout`. If `timeout` is `None` or 
		not specified, the function will not return until the Future is resolved. Returns `True` if the `Future` 
		object was resolved, and returns `False` if the timeout was exceeded before it was resolved.
		
		Synonymous with `Future.hold`"""
		return self.resolveEvent.wait(timeout=timeout)
	
	@property
	def ready(self) -> bool:
		"""Returns `True` if the `Future` object has resolved, and returns `False` if it has not."""
		return self.resolveEvent.is_set()
	
	@property
	def dropped(self) -> bool:
		"""Returns `True` if the `Future` object was resolved by the wrapped `Thread` target function stopping 
		prematurely. The Exception is then stored in the `Future.exception` attribute."""
		return hasattr(self, "exception")

	@overload
	def resolve(self, *, value : Any): ...
	@overload
	def resolve(self, *, exception : Exception): ...
	def resolve(self, *, value=_NOT_SET, exception=_NOT_SET):
		"""Called by the `Thread` object which created this `Future` object once the `pre`, `target`, & `post` 
		functions have returned or stopped.
		
		If functions returned successfully, the return value is set through the 
		`value` keyword.
		
		If any of the functions raise an exception, that exception is provided instead of `value`, but through the 
		`exception` keyword.
		
		If none of the keywords are provided, a `ValueError` exception is raised."""
		assert current_thread() == self.thread, f"Only the thread assigned to this future can resolve this future. {current_thread()=} and {self.thread=}"
		if value is not _NOT_SET:
			self.value = value
		elif exception is not _NOT_SET:
			self.exception = exception
		else:
			raise ValueError(f"`Future.resolve` can only be called with either `value` or `exception` specified.")
		
		self.resolveEvent.set()
		
	def call(self, timeout : float=None):
		"""Wait for the `Future` object to resolve, and return the value """
		self.hold(timeout=timeout)
		if self.dropped:
			raise self.exception
		else:
			return self.value

class ThreadGroup:
	
	_dict : dict[str,"Thread"]

	writeLock : RLock
	names : list[str]

	def __init__(self, iterable : Iterable["Thread"]|Iterator["Thread"]=[]):
		self.writeLock = RLock()
		with self.writeLock:
			self._dict = {thread.name:thread for thread in iterable}

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

class Thread(_Thread, Logged):
	
	group : ThreadGroup
	future : Future
	pre : Callable
	target : Callable
	post : Callable
	"""An object to access the """

	def __init__(self, *, group: ThreadGroup | None = None, pre: Callable[[Any], object] | None = None, target: Callable[[Any], object] | None = None, post: Callable[[Any], object] | None = None, name: str | None = None, args: Iterable[Any] = [], kwargs: Mapping[str, Any] | None = None, daemon: bool | None = None) -> None:
		super().__init__(target=self.wrapper, name=name, args=args, kwargs=kwargs, daemon=daemon)
		self.pre = pre
		self.target = target
		self.post = post
		self.group = group
		if self.group:
			self.group.add(self)
		self.future = Future(self)
	
	@property
	def alive(self):
		return self.is_alive()

	def wrapper(self, *args, **kwargs):
		try:
			if self.pre: self.pre(*args, **kwargs)
			ret = self.target(*args, **kwargs)
			if self.post: self.post(*args, **kwargs)
			self.future.resolve(value=ret)
		except Exception as e:
			logCopy = type(e)(*e.args)
			logCopy.add_note(f"This exception occured in thread: {current_thread()}")
			self.LOG.exception(type(e)(*e.args))
			self.future.resolve(exception=e)

	
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

from GeekyGadgets.Classy import Default
ThreadGroup = Default["_dict"](ThreadGroup.names.fget)
