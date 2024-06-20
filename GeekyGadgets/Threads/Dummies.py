
from GeekyGadgets.Threads.Globals import *
from GeekyGadgets.Threads.Thread import *
from GeekyGadgets.Threads.Groups import *

__all__ = ("DummyThread", "DummyLock")

class DummyThread:

	group : ThreadGroup
	future : Future
	pre : Callable
	target : Callable
	post : Callable
	"""An object to access the """

	def __init__(self, *, group: ThreadGroup | None = None, pre: Callable[[Any], object] | None = None, target: Callable[[Any], object] | None = None, post: Callable[[Any], object] | None = None, name: str | None = None, args: Iterable[Any] = [], kwargs: Mapping[str, Any] | None = None, daemon: bool | None = None) -> None:
		self.target=target
		self.name=name
		self.args=args
		self.kwargs=kwargs
		self.daemon=daemon
		self.pre = pre
		self.target = target
		self.post = post
		self.group = group
		if self.group:
			self.group.add(self)
		self.future = Future(self)
	alive = False
	def join(self, *args):
		pass
	def start(self, *args):
		pass

class DummyLock:
	def __enter__(self):
		return self
	def __exit__(self):
		pass
	def acquire(self, blocking: bool = None, timeout: float = None):
		return True
	def release(self):
		pass
	@property
	def locked(self):
		return False