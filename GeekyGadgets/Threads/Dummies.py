
import GeekyGadgets.Threads.Globals as _GL
import GeekyGadgets.Threads.Thread as _Thread
import GeekyGadgets.Threads.Groups as _Groups
import GeekyGadgets.Threads.Groups as _Groups

class DummyThread:

	group : "_Groups.ThreadGroup"
	future : "_Groups.Future"
	pre : _GL.Callable
	target : _GL.Callable
	post : _GL.Callable

	def __init__(self, *, group: "_Groups.ThreadGroup | None" = None, pre: _GL.Callable[[_GL.Any], object] | None = None, target: _GL.Callable[[_GL.Any], object] | None = None, post: _GL.Callable[[_GL.Any], object] | None = None, name: str | None = None, args: _GL.Iterable[_GL.Any] = [], kwargs: _GL.Mapping[str, _GL.Any] | None = None, daemon: bool | None = None) -> None:
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
		self.future = _Groups.Future(self)
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
