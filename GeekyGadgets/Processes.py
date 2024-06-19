
from GeekyGadgets.Globals import *
from GeekyGadgets.Hooks import Hooks, GlobalHooks
from GeekyGadgets.Paths import Path
from GeekyGadgets.Classy import Default
from GeekyGadgets.This import this
from GeekyGadgets.Threads import Thread
from GeekyGadgets.Functions import first
from GeekyGadgets.IO import LocalIO
from GeekyGadgets.SpecialTypes import NullSpace

from subprocess import Popen, PIPE
import shutil

_NOT_SET = object()
ARGS_PATTERN = re.compile(r"""((?:['][^']*?['])|(?:["][^"]*?["])|(?:\S+))""", flags=re.MULTILINE)
WORD_PATTERN = re.compile(r"^[\w_]+$")
ILLEGAL_PATH_CHARACTERS = re.compile(r"[^\w_ \-\.]")
SYNTAX_SYMBOLS = ["|", ";", "&", "&&", "||"]
DUMP_SYMBOL = ">"
SYNTAX_SYMBOLS_LOOKUP : dict[str,type["Process"]]

__all__ = (
	"MissingDependency", "Command", "Process", "ParallelProcess", "SequentialProcess", "PipeProcess",
	"ConditionalProcess", "OnSuccessProcess", "OnFailureProcess", "FakeProcess", "evalCommand"
)

class MissingDependency(Exception): pass

class FakePopen:
	
	returncode = None
	stdin = None
	stderr = None
	stdout = None

	def wait(self): pass
	def __bool__(self): return False


class Commands:
	
	commands : list["Command"]

	def __init__(self, commands : tuple[str], category : str="Command", names : str=None, hooks : Hooks=GlobalHooks, directories : Path=None):
		self.commands = []
		self.category = category
		self.names = names or [f"Command[{i+1}]" for i in range(len(commands))]
		self.directories = directories or [Path(".") for _ in range(len(commands))]
		self.hooks = hooks
		for command, name, directory in zip(commands, self.names, self.directories):
			self.commands.append(Command(command, category=category, name=name, hooks=hooks, directory=directory))
	
	def start(self):
		for command in self.commands:
			command.start()
	
	def wait(self):
		for command in self.commands:
			command.wait()
	
	@property
	def returncodes(self):
		return {command.name:first(filter(lambda x:x is not None and x != 0, reversed(command.exitcodes))) for command in self.commands}
	
	@Default["returncodes"]
	def failed(self):
		return {command.name:first(map(lambda x:'_'.join(filter(WORD_PATTERN.fullmatch, x.args[:2])), filter(lambda x:x.EXITCODES[0] not in [None, 0], reversed(command)))) for command in self.commands}

class Command:
	
	running : bool = property(lambda self: any(map(*this.RUNNING, self.processes)))
	exitcodes = property(lambda self: self.processes.EXITCODES)
	success : bool = property(lambda self: self.processes.SUCCESS)
	hooks : Hooks
	processes : "Process"
	notOnPath = cached_property(lambda self: set(map(lambda x:x.args[0], filter(lambda x:not x.ON_PATH, self.processes))))
	directory : Path = Default(lambda self:Path("."), lambda self, value: self.__dict__.__setitem__("directory", Path(self.directory)))

	_thread : Thread = None

	@overload
	def __init__(self, args : str, category : str="Command", name : str=None, hooks : Hooks=GlobalHooks, directory : Path=Path(".")): ...
	@overload
	def __init__(self, args : list[str], category : str="Command", name : str=None, hooks : Hooks=GlobalHooks, directory : Path=Path(".")): ...
	def __init__(self, args, category="Command", name=None, hooks=GlobalHooks, directory=Path(".")):
		
		self.hooks = hooks
		self.category = category
		self.directory = Path(directory)
		if isinstance(args, Iterator):
			args = list(args)
		
		if isinstance(args, str):
			self.args = ARGS_PATTERN.findall(args)
		elif isinstance(args, Iterable) and all(isinstance(arg, str) for arg in args):
			self.args = args
		else:
			raise TypeError(f"`args` must be an iterable of strings or itself a `str`")
		
		self.processes = evalCommand(self.args, directory=self.directory, hooks=hooks)
		for i, p in enumerate(self.processes):
			p.category = self.category
		self.name = name or self.processes.name
	
	def __str__(self):
		return "".join(map(str, self.processes))
	
	def run(self):
		self.hooks.trigger(self.category, {"name" : self.name, "type" : "Started"})
		self.processes.run()
		for p in self.processes:
			p.wait()
		if self.success:
			self.hooks.trigger(self.category, {"name" : self.name, "type" : "Finished"})
		else:
			self.hooks.trigger(self.category, {"name" : self.name, "type" : "Failed"})

	def start(self):
		
		self.checkReadiness()
		self._thread = Thread(target=self.run)
		self._thread.start()

	def wait(self):
		if self._thread:
			self._thread.join()
		else:
			for p in self.processes:
				p.wait()
		return self.exitcodes
	
	@overload
	def dumpLogs(self, /): ...
	@overload
	def dumpLogs(self, directory : Path, /): ...
	@overload
	def dumpLogs(self, directory : Path, stderr : str, stdout : str, /): ...
	@overload
	def dumpLogs(self, directory : Path=None, stderr : str=None, stdout : str=None, /, *, index : int=1): ...
	def dumpLogs(self, directory : Path=None, stderr : str=None, stdout : str=None, /, *, index : int=1):
		self.processes.dumpLogs(directory or self.directory, stderr, stdout, index=index)
	
	def checkReadiness(self):
		if self.notOnPath:
			raise MissingDependency(f"Could not find dependencies: {', '.join(self.notOnPath)}")
		elif not all(os.path.exists(p.directory) for p in self.processes):
			offenders = []
			for p in self.processes:
				if not os.path.exists(p.directory):
					offenders.append(p.directory)
			raise NotADirectoryError(f"Can not store subprocess outputs in directories: {', '.join(offenders)}")
		elif not all((not os.path.exists(p.directory / name) and os.access(p.directory, mode=os.W_OK)) or os.access(p.directory / name, mode=os.W_OK) for p in self.processes for name in [p.filenameERR, p.filenameOUT]):
			offenders = []
			for p in self.processes:
				for name in [p.filenameERR, p.filenameOUT]:
					if os.path.exists(p.directory / name) and os.access(p.directory / name, mode=os.W_OK):
						continue
					elif os.path.exists(p.directory / name) and not os.access(p.directory / name, mode=os.W_OK):
						offenders.append(p.directory / name)
					elif not os.access(p.directory, mode=os.W_OK):
						offenders.append(p.directory)
			raise PermissionError(f"Can not store subprocess outputs in directories: {', '.join(offenders)}")

class Process:

	OUT : LocalIO = Default(lambda self:LocalIO() if self.filenameDUMP is None else None)
	ERR : LocalIO = Default(lambda self:LocalIO())
	IN : BufferedReader = Default(lambda self: self.popen.stdin if not isinstance(self.parent, PipeProcess) else self.parent.OUT)
	RUNNING : bool
	EXITCODES : int | list[int] = property(lambda self: [self.popen.returncode] + self.child.EXITCODES if self.child else [self.popen.returncode])
	SUCCESS : bool = property(lambda self: self.popen.returncode == 0 and (self.child.SUCCESS if self.child else True))
	ON_PATH = property(lambda self: shutil.which(self.args[0]) is not None)
	END_SYMBOL : str= None

	parent : "Process" = Default(lambda self:FakeProcess(), lambda self, value:SETATTR(self.parent, "child", self) if getattr(self.parent, "child") is not self else None)
	args : Iterable[str]
	child : "Process" = Default(lambda self:FakeProcess(), lambda self, value:SETATTR(self.child, "parent", self) if getattr(self.child, "parent") is not self else None)
	category : str
	name : str = Default["args"](lambda self: "_".join(filter(WORD_PATTERN.fullmatch, map(lambda x:os.path.basename(os.path.splitext(x)[0]), self.args[:2]))))
	directory : Path = Default(lambda self:Path("."), lambda self, value: self.__dict__.__setitem__("directory", Path(self.directory)))
	filenameERR : str = Default["name"](lambda self: f"{self.name}.err.log")
	filenameOUT : str = Default["name"](lambda self: f"{self.name}.out.log")
	filenameDUMP : str = None
	hooks : Hooks

	popen : Popen = FakePopen()

	@overload
	def __init__(self, *, parent : "Process"=None, args : Iterable[str], child : "Process"=None, 
				name : str|Any=None, category : str|Any="Command", filenameOUT : str, filenameERR : str,
				filenameDUMP : str=None, hooks : Hooks=GlobalHooks, directory : Path="."): ...
	def __init__(self, **kwargs):
		for name, value in kwargs.items():
			setattr(self, name, value)

	def __str__(self):
		return " ".join(self.args) + (" "+self.END_SYMBOL if self.END_SYMBOL else "")

	def run(self):
		
		self.popen = Popen(args=self.args, stdin=self.IN, stderr=PIPE, stdout=PIPE if self.filenameDUMP is None else open(self.directory / self.filenameDUMP, "wb"))
		
		if hasattr(self.ERR, "couple"):
			self.ERR.couple(self.popen.stderr)
		
		if hasattr(self.OUT, "couple"):
			self.OUT.couple(self.popen.stdout)
		
		if self.IN: self.IN.close()
		
		self.hooks.trigger(self.category, {"name" : self.name, "type" : "Started"})
	
	def wait(self):
		if self.popen.returncode is None:
			if self.popen.wait() == 0:
				self.hooks.trigger(self.category, {"name" : self.name, "type" : "Finished"})
			else:
				self.hooks.trigger(self.category, {"name" : self.name, "type" : "Failed"})

	@overload
	def dumpLogs(self, /): ...
	@overload
	def dumpLogs(self, directory : Path, /): ...
	@overload
	def dumpLogs(self, directory : Path, stderr : str, stdout : str, /): ...
	@overload
	def dumpLogs(self, directory : Path=None, stderr : str=None, stdout : str=None, /, *, index : int=1): ...
	def dumpLogs(self, directory : Path=None, stderr : str=None, stdout : str=None, /, *, index : int=1):

		if isinstance(self.ERR, LocalIO) and self.popen:
			self.ERR.coupled.join()
			directory = directory or self.directory
			name = stderr or self.filenameERR
			name = name[0] + f"_{index}.".join(name[1:].split(".", 1))
			
			open(directory / name, "w").write(self.ERR.read())
		if isinstance(self.OUT, LocalIO) and self.popen:
			self.OUT.coupled.join()
			directory = directory or self.directory
			name = stdout or self.filenameOUT
			name = name[0] + f"_{index}.".join(name[1:].split(".", 1))

			open(directory / name, "w").write(self.OUT.read())
		if self.child:
			self.child.dumpLogs(directory, stderr, stdout, index=index+1)

	@property
	def RUNNING(self):
		try:
			self.popen.wait(0.01)
			return True
		except:
			return False
	
	def __len__(self):
		swap = self
		i = 1
		while swap.child:
			swap = swap.child
			i += 1
		return i
	
	def __iter__(self):
		swap = self
		yield swap
		while swap.child:
			swap = swap.child
			yield swap

	def __getitem__(self, key):
		if isinstance(key, int):
			realKey = key if key >= 0 else len(self)+key
			for i, p in zip(range(realKey+1), self):
				if i == realKey:
					return p
			else:
				raise IndexError(f"Index {key} out of range for {type(key).__qualname__} object of length {len(self)}")
		elif isinstance(key, slice):
			return list(self)[key]
		else:
			return TypeError(f"Process indices must be integers or slices, not {type(key).__qualname__}")

class ParallelProcess(Process):
	
	END_SYMBOL : str= "&"

	def run(self):
		super().run()
		if self.child:
			self.child.run()

class SequentialProcess(Process):
	
	END_SYMBOL : str= ";"
	
	def run(self):
		super().run()
		self.wait()
		if self.child:
			self.child.run()

class PipeProcess(Process):
	
	END_SYMBOL : str= "|"
	
	OUT = property(lambda self: self.popen.stdout or PIPE)

	def run(self):
		super().run()
		if self.child:
			self.child.run()

class ConditionalProcess(Process):
	
	END_SYMBOL : str= ""

	condition : bool = property(lambda self: True)

	def run(self):
		super().run()
		self.wait()
		if self.condition:
			self.child.run()

class OnSuccessProcess(ConditionalProcess):

	END_SYMBOL : str= "&&"
	@property
	def SUCCESS(self) -> bool:
		if not (self.popen.returncode is not None and (self.popen.returncode == 0) == (self.child.popen.returncode == 0)):
			return False
		elif self.child.child:
			return self.child.child.SUCCESS
		else:
			return True

	@property
	def condition(self):
		return self.popen.returncode == 0

class OnFailureProcess(ConditionalProcess):

	END_SYMBOL : str= "||"
	@property
	def SUCCESS(self) -> bool:
		if not (self.popen.returncode == 0 or self.child.popen.returncode == 0):
			return False
		elif self.child.child:
			return self.child.child.SUCCESS
		else:
			return True

	@property
	def condition(self):
		return self.popen.returncode != 0

class FakeProcess(Process):
	
	OUT : BinaryIO = None
	ERR : BinaryIO = None
	IN : BinaryIO = None
	RUNNING : False
	EXITCODES : list[int] = []
	SUCCESS : bool = True
	END_SYMBOL : str= ""

	parent : Process = None
	args : Iterable[str] = []
	child : Process = None

	def __init__(self, **kwargs): pass
	def __bool__(self): return False
	def run(self): pass
	def wait(self): pass


SYNTAX_SYMBOLS_LOOKUP = {
	"|" :   PipeProcess,
	";" :   SequentialProcess,
	"&" :   ParallelProcess,
	"&&" :  OnSuccessProcess, # ConditionalProcess on success
	"||" :  OnFailureProcess, # ConditionalProcess on failure
}

@overload
def evalCommand(argv : Iterator[str]|Iterable[str], *, name : str|Any="Process", category : str|Any="Command",
				filenameOUT : str, filenameERR : str, filenameDUMP : str=None, hooks : Hooks=GlobalHooks, directory : Path=".") -> "Process": ...
def evalCommand(argv, **kwargs):
	args = []
	filenameDUMP = None
	breaker = None
	if isinstance(argv, Iterable):
		argv = iter(argv)
	for arg in argv:
		if arg in SYNTAX_SYMBOLS:
			breaker = arg
			break
		elif arg == ">":
			try:
				filenameDUMP = next(argv)
				breaker = next(argv)
			except StopIteration:
				pass
			break
		else:
			args.append(arg)
	
	if not args:
		return None
	elif filenameDUMP is not None:
		return Process(args=args, **(kwargs | {"filenameDUMP" : filenameDUMP}))
	elif breaker is None:
		return Process(args=args, **kwargs)
	else:
		processClass = SYNTAX_SYMBOLS_LOOKUP[breaker]
		
		ret = processClass(args=args, child=evalCommand(argv, **kwargs), **kwargs)
		if ret.child is not None:
			ret.child.parent = ret
		return ret