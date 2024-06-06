
from GeekyGadgets.Globals import *
from GeekyGadgets.Hooks import Hooks, GlobalHooks
from subprocess import Popen, PIPE
import subprocess

_NOT_SET = object()

parallelPattern = re.compile(r"\s*[&]\s*")
sequentialPattern = re.compile(r"\s*([;])\s*|\s*([&][&])\s*|\s*([|][|])\s*")
pipePattern = re.compile(r"\s*[|]\s*")
dumpPattern = re.compile(r"\s*[>]\s*")
whitePattern = re.compile(r"\s*")
argsPattern = re.compile(r"(['][^']*?['])|([\"][^\"]*?[\"])|(\S+)", flags=re.MULTILINE+re.DOTALL)
ARGS_PATTERN = re.compile(r"((?:['][^']*?['])|(?:[\"][^\"]*?[\"])|(?:\S+))", flags=re.MULTILINE+re.DOTALL)
quotePattern = re.compile(r"['\" ]*")
illegalPattern = re.compile(r"[^\w_ \-\.]")

SYNTAX_SYMBOLS = ["|", ">", ";", "&", "&&", "||"]
SYNTAX_SYMBOLS_LOOKUP = {
	"|" :   "PipeProcess",
	">" :   "DumpProcess",
	";" :   "SequentialProcess",
	"&" :   "ParallelProcess",
	"&&" :  "SequentialProcess", # ConditionalProcess on success
	"||" :  "SequentialProcess", # ConditionalProcess on failure
}

class MissingDependency(Exception): pass

class Command:
	
	hooks : Hooks

	@overload
	def __init__(self, args : str, hooks : Hooks=GlobalHooks): ...
	@overload
	def __init__(self, args : list[str], hooks : Hooks=GlobalHooks): ...
	def __init__(self, args, hooks=GlobalHooks):
		
		self.hooks = hooks
		if not isinstance(args, str):
			self.args = args 
		else:
			self.args = ARGS_PATTERN.findall(args)
		
		self.processes = [FakeProcess()]
		currentArgs = []
		_iter = self.args
		# RETHINK THIS
		for arg in _iter:
			if arg in SYNTAX_SYMBOLS:
				processClass = globals[SYNTAX_SYMBOLS_LOOKUP[arg]]
				if arg == ">": 
					self.processes.append(processClass(parent=self.processes[-1], args=currentArgs, filename=next(_iter)))
				else:
					self.processes.append(processClass(parent=self.processes[-1], args=currentArgs))
				currentArgs = []
				if arg in ["&&", "||"]:
					first = arg
					for arg in _iter:
						if arg in SYNTAX_SYMBOLS:
							break
						else:
							currentArgs.append(arg)
					else:
						break
					first = (first, currentArgs)
					currentArgs = []
					second = arg
					for arg in _iter:
						if arg in SYNTAX_SYMBOLS:
							break
						else:
							currentArgs.append(arg)
					else:
						SequentialProcess(parent=self.processes[-1], args=args)
						break
					match first:
						case "&&":
							success = []

						case "||":
							failure = []
					self.processes.append(ConditionalProcess(parent=self.processes[-1], success=))
					

class Process:

	OUT : BinaryIO
	ERR : BinaryIO
	IN : BinaryIO
	EXITCODE : int | list[int]

	hooks : Hooks

	args : Iterable[str]
	popen : Popen = None

	parent : "Process"
	child : "Process"

	# These two properties will give infinite recursion if two connected processes don't override their respective 
	# attributes/properties
	@property
	def OUT(self):
		return self.child.IN
	@property
	def ERR(self):
		return self.parent.ERR
	@property
	def IN(self):
		return self.parent.OUT
	@property
	def EXITCODE(self):
		if self.popen.returncode == 0:
			return [0]
		else:
			return [self.popen.returncode] + self.parent.EXITCODE
	
	@overload
	def __init__(self, *, parent : "Process", args : Iterable[str], child : "Process", hooks : Hooks=GlobalHooks): ...
	def __init__(self, *, parent=_NOT_SET, args, child=_NOT_SET, hooks : Hooks=GlobalHooks):
		if parent is _NOT_SET:
			self.parent = FakeProcess()
		else:
			self.parent = parent
			self.parent.child = self
		self.args = args
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

class SequentialProcess(Process):
	
	def run(self, name=_NOT_SET):
		if self.popen:
			self.popen.wait()
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
		return self.__dict__.get("OUT", open(self.filename, "rb"))

	@overload
	def run(self): ...
	@overload
	def run(self, name : str): ...
	def run(self, name=_NOT_SET):
		if self.popen:
			self.OUT.close()
			self.popen.wait()
			self.child.run(name=name)
		else:
			super().run(name=name)

class ConditionalProcess(Process):
	
	success : Process
	failure : Process

	@overload
	def __init__(self, *, parent : "Process", success : "Process", failure : "Process", hooks : Hooks=GlobalHooks): ...
	def __init__(self, *, parent, success=None, failure=None, hooks : Hooks=GlobalHooks):
		self.parent = parent
		self.success = success
		self.failure = failure
		self.hooks = hooks
	
	@overload
	def run(self): ...
	@overload
	def run(self, name : str): ...
	def run(self, name=_NOT_SET):
		self.parent.wait()
		if self.parent.popen.returncode == 0:
			self.success.run(name=name)
		else:
			self.failure.run(name=name)

class FakeProcess(Process):
	
	@property
	def OUT(self):
		return None
	@OUT.setter
	def OUT(self, value): pass
	@property
	def ERR(self):
		return None
	@ERR.setter
	def ERR(self, value): pass
	@property
	def IN(self):
		return None
	@IN.setter
	def IN(self, value): pass

	args : Iterable[str] = []

	def __init__(self): pass
	def run(self): pass
	def wait(self):
		pass