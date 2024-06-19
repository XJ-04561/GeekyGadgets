
from types import TracebackType
from GeekyGadgets.Globals import *
from GeekyGadgets.Classy import Default
from GeekyGadgets.Threads import RLock, Thread, DummyThread
from GeekyGadgets.SpecialTypes import LimitedList
from GeekyGadgets.Functions import swapAttr


from io import *

_T = TypeVar("_T")

class RePrinter:

	LOCK : RLock = RLock()

	@Default["out"]
	def supportsColor(self):
		from GeekyGadgets.Colors.ANSI import supportsColor
		try:
			return supportsColor(self.out)
		except:
			return False

	@property
	def terminalWidth(self):
		if ISATTY:
			return os.get_terminal_size()[0]
		else:
			return 80

	@overload
	def __init__(self, out=sys.stdout, exitMessage : str=None): ...
	def __init__(self, out=None, exitMessage=None):
		self.out = out or sys.stdout
		self.last = 0
		self.exitMessage = exitMessage
	
	def __call__(self, msg):
		with self.LOCK:
			self.out.write(msg)
			self.out.flush()
			self.last += len(getattr(msg, "raw", msg))
	
	def __enter__(self):
		return self

	def __exit__(self, exc_type, exc_value, traceback):
		if self.exitMessage:
			self.out.write(self.exitMessage)
		self.out.write("\n")
	
	def reset(self):
		with self.LOCK:
			if self.supportsColor:
				self.out.write("\r"+"\033[A"*(max(self.last-1, 0) // self.terminalWidth))
			else:
				self.out.write("\b"*self.last)
			self.out.flush()
			self.last = 0
	
	def clear(self):
		with self.LOCK:
			last = self.last
			self.reset()
			self(" " * last)
			self.reset()

class SplitIO(IOBase):
	
	mode : str
	closed : bool = Default["files"](lambda self:False)
	name : str = property(lambda self: f"<SplitIO {self.files} at {id(self):#x}>")

	files : tuple[IOBase]

	def __init__(self, files : Iterable[IO]):
		if type(self) is SplitIO:
			raise NotImplementedError(f"Base class is not implemented. Possible subclasses: {', '.join(map(lambda x:x.__name__, self.__class__.__subclasses__()))}")
		self.files = tuple(files)
		if not all(file.mode == self.mode for file in self.files):
			raise TypeError(f"Can not create a splitter with mode {self.mode!r} when target IOs are of modes: {', '.join(map(lambda x:x.mode, self.files))!r}.")

	def __getitem__(self, index : int, /):
		return self.files[index]

	def __enter__(self) -> "SplitIO[AnyStr]":
		return self

	def __exit__(self, type, value, traceback) -> None:
		pass

	def add(self, file):
		self.files += (file)
	
	def remove(self, file):
		pos = self.files.index(file)
		self.files = self.files[:pos] + self.files[pos+1:]
	
	def discard(self, file):
		if file in self.files:
			pos = self.files.index(file)
			self.files = self.files[:pos] + self.files[pos+1:]
		else:
			return None

	def read(self, n: int = -1) -> tuple[AnyStr]:
		return tuple(file.read(n=n) for file in self.files)

	def readline(self, limit: int = -1) -> AnyStr:
		return tuple(file.readline(limit=limit) for file in self.files)

	def readlines(self, hint: int = -1) -> List[AnyStr]:
		return tuple(file.readlines(hint=hint) for file in self.files)

	def seek(self, offset: int, whence: int = 0) -> int:
		return tuple(file.seek(offset=offset, whence=whence) for file in self.files)

	def seekable(self) -> bool:
		return all(hasattr(file, "seekable") and file.seekable() for file in self.files)

	def tell(self) -> int:
		return tuple(file.tell() if hasattr(file, "tell") else None for file in self.files)

	def truncate(self, size: int = None) -> int:
		return tuple(file.truncate(size=size) for file in self.files)

	def write(self, s: AnyStr) -> int:
		return tuple(file.write(s=s) for file in self.files)

	def writelines(self, lines: List[AnyStr]) -> None:
		for file in self.files:
			file.writelines(lines=lines)

	def readable(self) -> bool:
		return all(file.readable() for file in self.files)
	
	def writable(self) -> bool:
		return all(file.writable() for file in self.files)

	def close(self) -> None:
		for file in self.files:
			if file not in [sys.__stdin__, sys.__stderr__, sys.__stdout__]:
				file.close()
		self.closed = True
	
	def closeAll(self) -> None:
		for file in self.files:
			file.close()
		self.closed = True

	def fileno(self) -> int:
		raise NotImplementedError(f"SplitIO has no one single `fileno`")

	def flush(self) -> None:
		for file in self.files:
			file.flush()

	def isatty(self) -> bool:
		return False

class SplitBinaryIO(SplitIO):
	
	def __init__(self, files : Iterable[BinaryIO], mode : str):
		
		if mode in ("r", "w"):
			self.mode = f"{mode}b"
		elif mode in ("rb", "wb"):
			self.mode = mode
		elif isinstance(mode, str):
			raise ValueError(f"{mode!r} is not any of valid modes: \"r\", \"w\", \"rb\", and \"wb\"")
		else:
			raise TypeError(f"Argument `mode` must be of type `str` or a subclass of it, not {mode.__class__.__name__!r}")
		
		super().__init__(files=files)

class SplitTextIO(SplitIO):
	
	def __init__(self, files : Iterable[BinaryIO], mode : str):
		
		if mode in ("r", "w"):
			self.mode = mode
		elif isinstance(mode, str):
			raise ValueError(f"{mode!r} is not any of valid modes: \"r\" and \"w\"")
		else:
			raise TypeError(f"Argument `mode` must be of type `str` or a subclass of it, not {mode.__class__.__name__!r}")
		
		super().__init__(files=files)

class LocalIO(list, IO):
	
	size : int = property(lambda self: sum(map(len, self)))
	closed = False
	coupled : Thread = DummyThread()
	streamLock : RLock = Default(lambda self:RLock())

	def read(self, n: int = -1) -> tuple[AnyStr]:
		with self.streamLock:
			_iter = iter(self)
			for row in _iter:
				out = row
				break
			else:
				return ""
			for row in _iter:
				out = out + row
				if n > 0 and len(out) > n:
					return out[:n]
			return out

	def readlines(self, hint: int = -1) -> List[AnyStr]:
		with self.streamLock:
			return list(self)

	def write(self : "LocalIO[_T]", s : _T):
		with self.streamLock:
			self.append(s)
	
	def writelines(self : "LocalIO[_T]", lines : Iterable[_T]):
		with self.streamLock:
			self.extend(lines)

	def fileno(self):
		return -1

	def flush(self):
		pass

	def _read_loop(localIO : "LocalIO", readableIO : IO):
		while line := readableIO.readline(): localIO.write(line)
		readableIO.close()

	def couple(self, readableIO : IO, /):
		from GeekyGadgets.Threads import Thread
		if "b" in readableIO.mode:
			self.coupled = Thread(target=self._read_loop, args=(TextIOWrapper(readableIO, errors="backslashreplace"), ))
		else:
			self.coupled = Thread(target=self._read_loop, args=(readableIO,))
		self.coupled.start()

class LocalBufferIO(LimitedList, LocalIO):
	
	size : int = property(lambda self: sum(map(len, self)))
	# closed = False

	# def read(self, n: int = -1) -> tuple[AnyStr]:
	# 	_iter = iter(self)
	# 	for row in _iter:
	# 		out = row
	# 		break
	# 	else:
	# 		return ""
	# 	for row in _iter:
	# 		out = out + row
	# 		if n > 0 and len(out) > n:
	# 			return out[:n]
	# 	return out

	# def readlines(self, hint: int = -1) -> List[AnyStr]:
	# 	return list(self)

	# def write(self : "LocalBufferIO[_T]", s : _T):
	# 	self.append(s)
	
	# def writelines(self : "LocalBufferIO[_T]", lines : Iterable[_T]):
	# 	self.extend(lines)

	# def fileno(self):
	# 	return -1

	# def flush(self):
	# 	pass

	# def _read_loop(localBufferIO : "LocalBufferIO", readableIO : IO):
	# 	while line := readableIO.readline():
	# 		localBufferIO.write(line)
	# 	readableIO.close()
	
	# def couple(self, readableIO : IO, /):
	# 	from GeekyGadgets.Threads import Thread
	# 	if "b" in readableIO.mode:
	# 		self.coupled = Thread(target=self._read_loop, args=(TextIOWrapper(readableIO, errors="backslashreplace"), ))
	# 	else:
	# 		self.coupled = Thread(target=self._read_loop, args=(readableIO,))
	# 	self.coupled.start()

class ReplaceIO(IO):
	
	outIO : IO[str|bytes]
	container : IO[str|bytes]
	replacerFunc : Callable

	@overload
	def __init__(self, /): ...
	@overload
	def __init__(self, /, container : IO[str|bytes], replacerFunc : Callable): ...
	def __init__(self, /, container : IO[str|bytes], replacerFunc : Callable):
		self.container = container
		self.replacerFunc = replacerFunc
	
	def __iter__(self):
		return iter(tuple(self.container))

	def __enter__(self):
		"""Start capturing and return `self`."""
		self.start()
		return self
	
	def __exit__(self, type: type[BaseException] | None, value: BaseException | None, traceback: TracebackType | None) -> None:
		"""Stop capturing."""
		self.stop()

	def start(self):
		"""Start capturing."""
		self.outIO = self.replacerFunc(self.container)

	def stop(self):
		"""Stop capturing."""
		self.replacerFunc(self.outIO)

	def read(self, n: int = -1) -> tuple[AnyStr]:
		return self.container.read(n)

	def readlines(self, hint: int = -1) -> List[AnyStr]:
		return self.container.readlines(hint)

	def write(self, s : str|bytes):
		return self.container.write(s)
	
	def writelines(self, lines : Iterable[_T]):
		return self.container.writelines(lines)

class SiphonIO(ReplaceIO):
	
	splitIO : SplitTextIO

	def start(self):
		"""Start capturing."""
		self.splitIO = SplitTextIO()
		self.splitIO.add(self.container)
		self.splitIO.add(old := self.replacerFunc(self.splitIO))
		self.outIO = old

class ReplaceSTDIO(ReplaceIO):

	@overload
	def __init__(self, /, container : IO[str|bytes]=LocalIO): ...
	def __init__(self, /, container : IO[str|bytes]=None):
		self.container = container or LocalIO()


class SiphonSTDIO(ReplaceSTDIO, SiphonIO): pass

@staticmethod
def swapSTDOUT(new):
	"""Swap the current value of `sys.stdout` with that of the `new` argument, and return the old value."""
	return swapAttr(sys, "stdout", new)
@staticmethod
def swapSTDERR(new):
	"""Swap the current value of `sys.stderr` with that of the `new` argument, and return the old value."""
	return swapAttr(sys, "stderr", new)
@staticmethod
def swapSTDIN(new):
	"""Swap the current value of `sys.stdin` with that of the `new` argument, and return the old value."""
	return swapAttr(sys, "stdin", new)

class ReplaceSTDOUT(ReplaceSTDIO):
	replacerFunc = swapSTDOUT
class SiphonSTDOUT(SiphonSTDIO):
	replacerFunc = swapSTDOUT

class ReplaceSTDERR(ReplaceSTDIO):
	replacerFunc = swapSTDERR
class SiphonSTDERR(SiphonSTDIO):
	replacerFunc = swapSTDERR

class ReplaceSTDIN(ReplaceSTDIO):
	replacerFunc = swapSTDIN
class SiphonSTDIN(SiphonSTDIO):
	replacerFunc = swapSTDIN