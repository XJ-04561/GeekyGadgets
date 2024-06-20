

from GeekyGadgets.Threads.Globals import *
from GeekyGadgets.Threads.Globals import _Thread

import GeekyGadgets.Threads.Groups as Groups

__all__ = ("Thread", "Future")

_NOT_SET = object()

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
	group : "Groups.ThreadGroup" = property(lambda self:self.thread.group)

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

class Thread(_Thread, Logged):
	
	group : Groups.ThreadGroup
	future : Future
	pre : Callable
	target : Callable
	post : Callable
	"""An object to access the """

	def __init__(self, *, group: Groups.ThreadGroup | None = None, pre: Callable[[Any], object] | None = None, target: Callable[[Any], object] | None = None, post: Callable[[Any], object] | None = None, name: str | None = None, args: Iterable[Any] = [], kwargs: Mapping[str, Any] | None = None, daemon: bool | None = None) -> None:
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

