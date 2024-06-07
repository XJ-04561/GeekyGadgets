
from GeekyGadgets.Globals import *
from GeekyGadgets.Hooks import Hooks, GlobalHooks
from GeekyGadgets.Paths import Path
from GeekyGadgets.Classy import Default
from GeekyGadgets.This import this
from GeekyGadgets.Threads import Thread

from subprocess import Popen, PIPE
import subprocess
import shutil

_NOT_SET = object()
ARGS_PATTERN = re.compile(r"((?:['][^']*?['])|(?:[\"][^\"]*?[\"])|(?:\S+))", flags=re.MULTILINE+re.DOTALL)
WORD_PATTERN = re.compile(r"^\w+$")
ILLEGAL_PATH_CHARACTERS = re.compile(r"[^\w_ \-\.]")
SYNTAX_SYMBOLS = ["|", ">", ";", "&", "&&", "||"]
SYNTAX_SYMBOLS_LOOKUP : dict[str,type["Process"]]

__all__ = (
	"MissingDependency", "Command", "Process", "ParallelProcess", "SequentialProcess", "PipeProcess", "DumpProcess",
	"ConditionalProcess", "OnSuccessProcess", "OnFailureProcess", "FakeProcess", "evalCommand"
)

class MissingDependency(Exception): pass

class FakePopen:
	
	returncode = None

	def wait(self): pass
	def __bool__(self): return False

class Command:
	
	running : bool = property(lambda self: any(map(*this.RUNNING, self.processes)))
	exitcodes = property(lambda self: self.processes[-1].EXITCODES)
	success : bool = property(lambda self: self.processes[-1].SUCCESS)
	hooks : Hooks
	processes : list["Process"]
	notOnPath = cached_property(lambda self: set(map(lambda x:x.args[0], filter(lambda x:x.ON_PATH, self.processes))))


	@overload
	def __init__(self, args : str, hooks : Hooks=GlobalHooks, dir : Path=Path(".")): ...
	@overload
	def __init__(self, args : list[str], hooks : Hooks=GlobalHooks, dir : Path=Path(".")): ...
	def __init__(self, args, hooks=GlobalHooks, dir=Path(".")):
		
		self.hooks = hooks
		if not isinstance(args, str):
			self.args = args 
		else:
			self.args = ARGS_PATTERN.findall(args)
		
		self.processes = evalCommand(self.args, dir=dir)
	
	def run(self):
		self.processes[0].run()

	def start(self):
		if self.notOnPath:
			raise MissingDependency(f"Could not find dependencies: {', '.join(self.notOnPath)}")
		else:
			self._thread = Thread(target=self.run)
			self._thread.start()

	def wait(self):
		for p in self.processes:
			p.wait()
		return p.EXITCODES

class Process:

	OUT : BufferedWriter = Default(lambda self: self.ERR if self.filename == self.logname else open(self.filename, "wb"))
	ERR : BufferedWriter = Default(lambda self: open(self.logname, "wb"))
	IN : BufferedWriter = property(*this.parent.OUT)
	RUNNING : bool
	EXITCODES : int | list[int] = property(lambda self: [self.popen.returncode] + self.parent.EXITCODES)
	SUCCESS : bool = property(*this.popen.returncode == 0)
	ON_PATH = property(lambda self: shutil.which(self.args[0]) is not None)

	parent : "Process"
	args : Iterable[str]
	logname : Path
	filename : Path
	child : "Process"
	hooks : Hooks

	popen : Popen = FakePopen()

	@overload
	def __init__(self, *, args : Iterable[str], filename : str=None, logname : str=None, hooks : Hooks=GlobalHooks, dir : Path="."): ...
	@overload
	def __init__(self, *, args : Iterable[str], child : "Process", filename : str=None, logname : str=None, hooks : Hooks=GlobalHooks, dir : Path="."): ...
	@overload
	def __init__(self, *, parent : "Process", args : Iterable[str], child : "Process", filename : str=None, logname : str=None, hooks : Hooks=GlobalHooks, dir : Path="."): ...
	def __init__(self, *, parent=_NOT_SET, args, filename=None, logname=None, child=_NOT_SET, hooks=GlobalHooks, dir="."):
		if parent is _NOT_SET:
			self.parent = FakeProcess()
		else:
			self.parent = parent
			self.parent.child = self
		self.args = args
		self.logname = Path(dir) / (logname or f"{'_'.join(filter(WORD_PATTERN.fullmatch, self.args[:2]))}.log")
		self.filename = filename or self.logname

		self.child = child if child is not _NOT_SET else FakeProcess()
		self.hooks = hooks

	@overload
	def run(self): ...
	@overload
	def run(self, name : str): ...
	def run(self, name=_NOT_SET):
		if self.popen:
			self.child.run(name=name)
		else:
			self.popen = Popen(args=self.args, stdin=self.IN, stderr=self.ERR, stdout=self.OUT)
			self.hooks.trigger("ProcessStarted", {"name" : name if name is not _NOT_SET else " ".join(self.args)})
			if hasattr(self.IN, "close"):
				self.IN.close()
			self.run(name=name)
	
	def wait(self):
		self.popen.wait()
	
	@property
	def RUNNING(self):
		try:
			self.popen.wait(0.01)
			return True
		except:
			return False

class ParallelProcess(Process): pass

class SequentialProcess(Process):
	
	def run(self, name=_NOT_SET):
		if self.RUNNING:
			self.wait()
			self.child.run(name=name)
		else:
			super().run(name=name)

class PipeProcess(Process):
	
	@property
	def OUT(self):
		return self.__dict__.get("OUT", PIPE)

	@overload
	def run(self): ...
	@overload
	def run(self, name : str): ...
	def run(self, name=_NOT_SET):
		if self.popen:
			self.child.run(name=name)
		else:
			super().run(name=name)

class DumpProcess(Process):
	
	filename : str

	@overload
	def __init__(self, *, parent : "Process", args : Iterable[str], filename : str, child : "Process", hooks : Hooks=GlobalHooks): ...
	def __init__(self, *, parent=_NOT_SET, args, filename, child=_NOT_SET, hooks : Hooks=GlobalHooks):
		super().__init__(parent=parent, args=args, child=child, hooks=hooks)
		self.filename = filename

	@property
	def OUT(self):
		return self.__dict__.get("OUT", open(self.filename, "wb"))
	@OUT.setter
	def OUT(self, value):
		self.__dict__["OUT"] = value

	@overload
	def run(self): ...
	@overload
	def run(self, name : str): ...
	def run(self, name=_NOT_SET):
		if self.popen:
			self.OUT.close()
			self.OUT = None
			self.popen.wait()

			self.child.run(name=name)
		else:
			super().run(name=name)

class ConditionalProcess(Process):
	
	condition : bool

	@overload
	def run(self): ...
	@overload
	def run(self, name : str): ...
	def run(self, name=_NOT_SET):
		self.parent.wait()
		if self.condition:
			super().run(name=name)

class OnSuccessProcess(ConditionalProcess):

	@property
	def condition(self):
		return self.parent.popen.returncode == 0

class OnFailureProcess(ConditionalProcess):

	@property
	def condition(self):
		return self.parent.popen.returncode != 0

class FakeProcess(Process):
	
	OUT : BinaryIO = None
	ERR : BinaryIO = None
	IN : BinaryIO = None
	RUNNING : False
	EXITCODES : list[int] = []
	SUCCESS : bool = True

	args : Iterable[str] = []

	def __init__(self, *args, **kwargs): pass
	def run(self): pass
	def wait(self): pass

SYNTAX_SYMBOLS_LOOKUP = {
	"|" :   PipeProcess,
	">" :   DumpProcess,
	";" :   SequentialProcess,
	"&" :   ParallelProcess,
	"&&" :  OnSuccessProcess, # ConditionalProcess on success
	"||" :  OnFailureProcess, # ConditionalProcess on failure
}

def evalCommand(argv : Iterable[str], dir=None) -> "Process":
	args = []
	filename = None
	_iter = iter(argv)
	for arg in _iter:
		if arg in SYNTAX_SYMBOLS:
			breaker = arg
			if breaker == ">":
				for arg in _iter:
					filename = arg
					break
			break
		args.append(arg)
	else:
		return [Process(args=args)]
	
	processClass = SYNTAX_SYMBOLS_LOOKUP[breaker]
	
	ret = processClass(args=args, filename=filename, child=evalCommand(list(_iter), dir=dir), dir=dir)
	ret.child.parent = ret
	return ret