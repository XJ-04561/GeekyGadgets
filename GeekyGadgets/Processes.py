
from GeekyGadgets.Globals import *
from GeekyGadgets.Hooks import Hooks, GlobalHooks
from GeekyGadgets.Paths import Path
from GeekyGadgets.Classy import Default
from GeekyGadgets.This import this
from GeekyGadgets.Threads import Thread
from GeekyGadgets.Functions import first

from subprocess import Popen, PIPE
import subprocess
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

	def wait(self): pass
	def __bool__(self): return False

class Commands:
	
	commands : list["Command"]

	def __init__(self, commands : tuple[str], category : str="Command", names : str=None, hooks : Hooks=GlobalHooks, dirs : Path=None):
		self.commands = []
		self.category = category
		self.names = names or [f"Command[{i+1}]" for i in range(len(commands))]
		self.dirs = dirs or [Path(".") for _ in range(len(commands))]
		self.hooks = hooks
		for command, name, dir in zip(commands, self.names, self.dirs):
			self.commands.append(Command(command, category=category, name=name, hooks=hooks, dir=dir))
	
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

	_thread : Thread = None

	@overload
	def __init__(self, args : str, category : str="Command", name : str="Process", hooks : Hooks=GlobalHooks, dir : Path=Path(".")): ...
	@overload
	def __init__(self, args : list[str], category : str="Command", name : str="Process", hooks : Hooks=GlobalHooks, dir : Path=Path(".")): ...
	def __init__(self, args, category="Command", name="Process", hooks=GlobalHooks, dir=Path(".")):
		
		self.hooks = hooks
		self.category = category
		self.name = name
		if isinstance(args, Iterator):
			args = list(args)
		
		if isinstance(args, str):
			self.args = ARGS_PATTERN.findall(args)
		elif isinstance(args, Iterable) and all(isinstance(arg, str) for arg in args):
			self.args = args
		else:
			raise TypeError(f"`args` must be an iterable of strings or itself a `str`")
		
		self.processes = evalCommand(self.args, dir=dir, hooks=hooks)
		for i, p in enumerate(self.processes):
			p.category = self.category
			p.name = f"{self.name}-{i}"
	
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
	
	def checkReadiness(self):
		if self.notOnPath:
			raise MissingDependency(f"Could not find dependencies: {', '.join(self.notOnPath)}")
		elif not all(os.path.exists(os.path.dirname(path)) for p in self.processes for path in [p.logname, p.filename]):
			offenders = []
			for p in self.processes:
				for path in [p.logname, p.filename]:
					if not os.path.exists(os.path.dirname(path)):
						offenders.append(os.path.dirname(path))
			raise NotADirectoryError(f"Can not store subprocess outputs in directories: {', '.join(offenders)}")
		elif not all((not os.path.exists(path) and os.access(os.path.dirname(path), mode=os.W_OK)) or os.access(path, mode=os.W_OK) for p in self.processes for path in [p.logname, p.filename]):
			offenders = []
			for p in self.processes:
				for path in [p.logname, p.filename]:
					if os.path.exists(path) and os.access(path, mode=os.W_OK):
						continue
					elif os.path.exists(path) and not os.access(path, mode=os.W_OK):
						offenders.append(path)
					elif not os.access(os.path.dirname(path), mode=os.W_OK):
						offenders.append(os.path.dirname(path))
			raise PermissionError(f"Can not store subprocess outputs in directories: {', '.join(offenders)}")

class Process:

	OUT : BufferedWriter = Default(lambda self: self.ERR if self.filename == self.logname else open(self.filename, "wb"))
	ERR : BufferedWriter = Default(lambda self: open(self.logname, "wb"))
	IN : BufferedReader = Default(lambda self: self.parent.OUT if self.parent and self.parent.OUT and not self.parent.OUT.closed and self.parent.OUT.readable() else None)
	RUNNING : bool
	EXITCODES : int | list[int] = property(lambda self: [self.popen.returncode] + self.child.EXITCODES if self.child else [self.popen.returncode])
	SUCCESS : bool = property(lambda self: self.popen.returncode == 0 and (self.child.SUCCESS if self.child else True))
	ON_PATH = property(lambda self: shutil.which(self.args[0]) is not None)
	END_SYMBOL : str= None

	parent : "Process"
	args : Iterable[str]
	child : "Process"
	category : str
	name : str
	dir : Path
	logname : Path = Default["name"](lambda self: self.dir / f"{self.name}.log")
	filename : Path = Default["name"](lambda self: self.logname)
	hooks : Hooks

	popen : Popen

	def __init__(self, *, parent : "Process"=None, args : Iterable[str], child : "Process"=None, 
				name : str|Any=None, category : str|Any="Command", filename : str=None, logname : str=None,
				hooks : Hooks=GlobalHooks, dir : Path="."):
		self.parent = parent
		self.args = args
		self.popen = FakePopen()
		self.category = category
		self.name = name or '_'.join(filter(WORD_PATTERN.fullmatch, self.args[:2]))
		self.dir = Path(dir)
		if logname: self.logname = self.dir / logname
		if filename: self.filename = self.dir / filename
		self.child = child
		self.hooks = hooks

		if self.parent:
			self.parent.child = self
		if self.child:
			self.child.parent = self

	def __str__(self):
		return " ".join(self.args) + (" "+self.END_SYMBOL if self.END_SYMBOL else "")

	def run(self):
		
		self.popen = Popen(args=self.args, stdin=self.IN, stderr=self.ERR, stdout=self.OUT)
		self.OUT, self.ERR, self.IN = self.popen.stdout, self.popen.stderr, self.popen.stdin
		
		try:
			if not self.OUT.readable():
				self.OUT.close()
		except:
			pass
		
		try:
			if not self.ERR.readable():
				self.ERR.close()
		except:
			pass
		
		try:
			self.IN.close()
		except:
			pass
		
		self.hooks.trigger(self.category, {"name" : self.name, "type" : "Started"})
	
	def wait(self):
		if self.popen.returncode is None:
			if self.popen.wait() == 0:
				self.hooks.trigger(self.category, {"name" : self.name, "type" : "Finished"})
			else:
				self.hooks.trigger(self.category, {"name" : self.name, "type" : "Failed"})
	
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
	
	OUT = Default["popen"](*this.__dict__.get("OUT", PIPE))

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

	parent : Process
	args : Iterable[str] = []
	child : Process

	def __init__(self, parent=None, child=None, **kwargs):
		self.parent = parent
		self.child = child
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
				filename : str=None, logname : str=None, hooks : Hooks=GlobalHooks, dir : Path=".") -> "Process": ...
def evalCommand(argv, **kwargs):
	args = []
	filename = None
	breaker = None
	if isinstance(argv, Iterable):
		argv = iter(argv)
	for arg in argv:
		if arg in SYNTAX_SYMBOLS:
			breaker = arg
			break
		elif arg == ">":
			try:
				filename = next(argv)
				breaker = next(argv)
			except StopIteration:
				pass
			break
		else:
			args.append(arg)
	
	if not args:
		return None
	elif breaker is None:
		return Process(args=args, **(kwargs | {"filename" : filename}))
	else:
		processClass = SYNTAX_SYMBOLS_LOOKUP[breaker]
		
		ret = processClass(args=args, child=evalCommand(argv, **kwargs), **kwargs)
		if ret.child is not None:
			ret.child.parent = ret
		return ret