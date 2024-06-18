
from GeekyGadgets.Globals import *
from GeekyGadgets.Hooks import Hooks, GlobalHooks, HookedDict
from GeekyGadgets.Threads import *
from GeekyGadgets.Iterators import Batched, Alternate, Repeat
from GeekyGadgets.This import this
from GeekyGadgets.Logging import Logged
from GeekyGadgets.Classy import Default
from GeekyGadgets.Formatting import timeFormat
from GeekyGadgets.Colors.ANSI import *
from GeekyGadgets.IO import RePrinter

__all__ = ("LoadingBar", "Spinner", "TextProgress", "TerminalUpdater")

_NOT_FOUND = object()

class Indicator(Logged):
	
	FINISHED : bool = property(lambda self: all(value in self.FINISHED_CODES for value in self.threads.values()))
	RUN_LOCK : Lock = Default(lambda self: Lock())
	STOP : bool = False
	FINISHED_CODES = (2, 3, None)
	FAST_UPDATE = True
	FAILED : bool = property(lambda self: None in self.threads.values())
	SUCCEEDED : bool = property(lambda self: all(v is not None and v>1 for v in self.threads.values()))
	SKIPPED : bool = property(lambda self: all(v==2 for v in self.threads.values()))
	
	out : TextIO = Default(lambda self: sys.stdout)
	rowLock : RLock = Default(lambda self: RLock())
	refresh : Event = Default(lambda self: Event())
	threads : HookedDict[str,float]
	running : bool = property(lambda self: not self.RUN_LOCK.acquire(False))
	startTime : float

	category : str
	prompt : str
	status : str # property
	color : AnsiTheme = DefaultTheme
	sep : str = " "
	symbols : tuple[str]
	borders : tuple[str,str] = ("[", "]")
	finishSymbol : str = "="
	crashSymbol : str = "X"
	header : str # property
	spacer : str = property(lambda self: " " * self.width)
	body : str # property
	
	length : int = Default["width"](lambda self: min(max(map(len, self.names)), self.width-2*self.sepLength))
	sepLength : int	= property(lambda self:len(self.sep))
	borderLength : int = property(lambda self:sum(len(self.borders[0]), len(self.borders[1])))
	innerLength : int = property(lambda self:self.length - self.borderLength)
	
	width : int = property(
		lambda self: getattr(self, "DEFAULT_WIDTH", None) or (os.get_terminal_size()[0] if ISATTY else 80),
		lambda self, value: setattr(self, "DEFAULT_WIDTH", value),
		lambda self: delattr(self, "DEFAULT_WIDTH"))
	
	names : tuple[str] = Default["threads"](lambda self: tuple(sorted(self.threads.keys())))
	shortKeys : tuple[str] = Default["threads"](lambda self: [name if len(name) < self.length else name[:self.length-3]+"..." for name in self.names])
	N : int = Default["threads"](lambda self: len(self.names))

	@overload
	def __init__(self, /, category : str, threads : HookedDict): ...
	@overload
	def __init__(self, /, category : str, threads : HookedDict, length : int): ...
	@overload
	def __init__(self, /, category : str, threads : HookedDict, length : int, *, message : str="{status} {category}", out : TextIO, color : AnsiTheme, width : int, refresh : Event, rowLock : RLock): ...
	def __init__(self, /, category : str, threads : HookedDict, length : int=None, message : str="{status} {category}", **kwargs):
		
		self.category = category
		self.message = message
		self.threads = threads
		self.length = length or self.length
		for name, value in kwargs.items():
			setattr(self, name, value)

	@property
	def status(self):
		if all(v < 0 for v in self.threads.values()):
			return self.color.pre("Prepare")
		elif sum(v < 0 for v in self.threads.values()) < sum(0 <= v < 1.0 for v in self.threads.values()):
			return self.color.progress("Running")
		elif any(v == 1.0 for v in self.threads.values()):
			return self.color.post("Finishing")
		elif self.FAILED:
			return self.color.bad("Stopped")
		elif self.SKIPPED:
			return self.color.good("Skipped")
		elif self.SUCCEEDED:
			return self.color.good("Finished")
		else:
			return self.color.warning("Interrupted")
	
	@property
	def header(self):
		message = self.message.format(category=self.category, status=self.status)
		if self.width-2-len(self.message) < 12:
			
			return f"{message}:".ljust(self.width) + timeFormat(timer() - self.startTime).rjust(self.width)
		else:
			return f"{message}: {timeFormat(timer() - self.startTime)}".ljust(self.width)

	@Default["width", "N"]
	def body(self) -> str:
		
		maxCols = (self.width+self.sepLength-2) // (self.length+self.sepLength)
		
		namesIter = Batched(map(lambda i: f"{{names[{i}]:^{self.length}}}", range(self.N)), maxCols)
		barsIter = Batched(map(lambda i: f"{{bars[{i}]:^{self.length}}}", range(self.N)), maxCols)
		
		createRow = lambda cols: " "+self.sep.join(cols) + " "*(self.width-1-len(cols)*(self.length+self.sepLength)+self.sepLength)
		return "".join( map(createRow, Alternate(Repeat(self.spacer), namesIter, barsIter)))

	@property
	def rowGenerator(self) -> Generator[tuple[int,str],None,None]:
		"""Progress special cases:
		None	-	Service crashed
		2		-	Never ran/skipped
		3		-	Completed
		0<->1	-	Running
		<0		-	Not started
		1.0		-	Postprocessing
		"""
		raise NotImplementedError("rowGenerator not implemented in the base class")

	def run(self):
		
		self.startTime = timer()

		with RePrinter(self.out) as printer, self.RUN_LOCK:
			while not self.FINISHED and not self.STOP:
				with self.rowLock:
					printer.clear()
					printer(self.header)
					printer(self.spacer)
					printer(self.body.format(names=self.shortKeys, bars=tuple(self.rowGenerator)))
				
				if self.FINISHED or self.STOP: break

				sleep(0.1)
				self.refresh.wait(timeout=0.40)
			
			with self.rowLock:
				printer.clear()
				printer(self.header)
				if not self.SUCCEEDED:
					printer(self.spacer)
					printer(self.body.format(names=self.shortKeys, bars=tuple(self.rowGenerator)))

	def update(self):
		if self.FAST_UPDATE:
			self.refresh.set()

	def wait(self, timeout : float=None) -> bool:
		ret = self.RUN_LOCK.acquire(timeout=timeout)
		self.RUN_LOCK.release()
		return ret

	def kill(self):
		self.STOP = True
		self.refresh.set()
	
	def stop(self):
		self.STOP = True
		self.refresh.set()
		with self.RUN_LOCK:
			pass

class Timer(Indicator):

	FAST_UPDATE = False

	spacer : str = ""
	body : str = ""

	@property
	def rowGenerator(self) -> Generator[str,None,None]:
		for name in self.names:
			yield None

class LoadingBar(Indicator):
	
	symbols = Default["fill", "halfFill", "background"](lambda self: (self.fill, self.halfFill, self.background))

	fill : str = "="
	halfFill : str = ":"
	background : str = " "

	n = 0
	
	@property
	def rowGenerator(self) -> Generator[str,None,None]:
		"""Progress special cases:
		None	-	Service crashed
		2		-	Never ran/skipped
		3		-	Completed
		0<->1	-	Running
		<0		-	Not started
		1.0		-	Postprocessing
		"""
		crashString = self.borders[0]+self.color.bad(self.crashSymbol * self.innerLength)+self.borders[1]
		finishString = self.borders[0]+self.color.good(self.finishSymbol * self.innerLength)+self.borders[1]
		skippedString = self.borders[0]+self.color.good(self.fill * self.innerLength)+self.borders[1]
		
		for name, prog in zip(self.names, map(self.threads.get, self.names)):
			if prog is None:
				yield crashString
			elif prog == 2:
				yield skippedString
			elif self.threads[name] in self.FINISHED_CODES:
				yield finishString
			elif 0 <= prog < 1.0:
				fillLength = int(self.innerLength*2*prog)
				fillLength, halfBlock = fillLength//2, fillLength%2
				
				yield self.borders[0]+self.color.progress(f"{self.fill*fillLength}{self.halfFill*halfBlock}")+self.color.primary(f"{self.background*(self.innerLength - fillLength - halfBlock)}")+self.borders[1]
			elif prog < 0:
				yield self.borders[0]+self.color.pre(self.background*self.n + self.fill + self.background*(self.innerLength - self.n - 1))+self.borders[1]
			elif prog == 1:
				yield self.borders[0]+self.color.post(self.fill*self.n + self.background + self.fill*(self.innerLength - self.n - 1))+self.borders[1]
			else:
				yield crashString
		self.n = (self.n+1) % self.innerLength

class Spinner(Indicator):

	FAST_UPDATE = False

	symbols : list[str] = ["|", "/", "-", "\\"]

	@property
	def rowGenerator(self) -> Generator[tuple[int,str],None,None]:
		"""Progress special cases:
		None	-	Service crashed
		2		-	Never ran/skipped
		3		-	Completed
		0<->1	-	Running
		<0		-	Not started
		1.0		-	Postprocessing
		"""
		NSymbols = len(self.symbols)
		crashString = self.borders[0]+self.color.bad(self.crashSymbol)+self.borders[1]
		finishString = self.borders[0]+self.color.good(self.finishSymbol)+self.borders[1]
		skippedString = self.borders[0]+self.color.good(self.finishSymbol)+self.borders[1]
		
		for name, prog in zip(self.names, map(self.threads.get, self.names)):
			if prog is None:
				yield crashString
			elif prog == 2:
				yield skippedString
			elif self.threads[name] in self.FINISHED_CODES:
				yield finishString
			elif 0 <= prog < 1:
				yield self.borders[0]+self.color.progress(self.symbols[self.n])+self.borders[1]
			elif prog < 0:
				yield self.borders[0]+self.color.pre("." if self.n%2 else ":")+self.borders[1]
			elif prog == 1:
				yield self.borders[0]+self.color.post("." if self.n%2 else ":")+self.borders[1]
			else:
				yield crashString
		self.n = (self.n+1) % NSymbols

class TextProgress(Indicator):
	
	symbols : tuple[str]=[".", ",", ":", "|", "I", "H", "#"]

	@property
	def rowGenerator(self) -> Generator[tuple[int,str],None,None]:
		"""Progress special cases:
		None	-	Service crashed
		2		-	Never ran/skipped
		3		-	Completed
		0<->1	-	Running
		<0		-	Not started
		1.0		-	Postprocessing
		"""
		NSymbols = len(self.symbols)
		crashString = self.borders[0]+self.color.bad(self.crashSymbol)+self.borders[1]
		finishString = self.borders[0]+self.color.good(self.finishSymbol)+self.borders[1]
		skippedString = self.borders[0]+self.color.good(self.finishSymbol)+self.borders[1]
		
		for name, prog in zip(self.names, map(self.threads.get, self.names)):
			if prog is None:
				yield crashString
			elif prog == 2:
				yield skippedString
			elif self.threads[name] in self.FINISHED_CODES:
				yield finishString
			elif 0 <= prog < 1:
				yield self.borders[0]+self.color.progress(self.symbols[int(NSymbols*prog)])+self.borders[1]
			elif prog < 0:
				yield self.borders[0]+self.color.pre("."*self.n + ":"*(self.n<self.innerLength) + "."*(self.innerLength-self.n))+self.borders[1]
			elif prog == 1:
				yield self.borders[0]+self.color.post("o"*self.n + "O"*(self.n<self.innerLength) + "o"*(self.innerLength-self.n))+self.borders[1]
			else:
				yield crashString
		self.n = (self.n+1) % (self.innerLength + 1)

class TerminalUpdater(Logged):
	
	threads : HookedDict
	thread : Thread
	hooks : Hooks
	out : TextIO = None
	indicator : Indicator

	running = property(lambda self: self.indicator.running)

	@overload
	def __init__(self, category, names : Iterable[Hashable], /): ...
	@overload
	def __init__(self, category, N : int, /): ...
	@overload
	def __init__(self, category, names : Iterable[Hashable], /, *, message : str="{status} {category}", hooks : Hooks=GlobalHooks, out : TextIO=sys.stdout, indicatorType : Indicator=Timer, **indicatorArgs): ...
	@overload
	def __init__(self, category, N : int, /, *, message : str="{status} {category}", hooks : Hooks=GlobalHooks, out : TextIO=sys.stdout, indicatorType : Indicator=Timer, **indicatorArgs): ...
	def __init__(self, category, names, /, *, message : str="{status} {category}", hooks : Hooks=GlobalHooks, out=None, indicatorType : Indicator=Timer, **indicatorArgs):
		
		self.message = message
		self.category = category
		self.hooks = hooks
		self.out = out or sys.stdout
		if isinstance(names, Iterable) and (names := list(names)) and all(isinstance(name, Hashable) for name in names):
			pass
		elif isinstance(names, int):
			Nlength = len(str(names))
			names = [f"#{str(i).zfill(Nlength)}" for i in range(names)]
		else:
			raise TypeError(f"The third positional argument must be either an `int` or an iterable of names (hashable elements), which it was not {names=}.")
		self.threads = HookedDict(map(lambda name : (name,-1.0), names), hooks=self.hooks)
		
		self.hooks.addHook("HookedDict", self.updateIndicator)
		self.hooks.addHook(self.category, self.progressCallback)

		self.indicator = indicatorType(self.category, threads=self.threads, message=self.message, hooks=self.hooks, out=self.out, **indicatorArgs)

	def __enter__(self):
		self.start()
		return self

	def __exit__(self, *args):
		self.stop()

	def progressCallback(self, eventInfo : dict[str,Any]):
		
		if eventInfo["name"] not in self.threads:
			return
		match eventInfo["type"]:
			case "Skipped":
				self.threads[eventInfo["name"]] = 2
			case "Starting":
				self.threads[eventInfo["name"]] = 0.0
			case "Progress":
				self.threads[eventInfo["name"]] = eventInfo["value"]
			case "PostProcess":
				self.threads[eventInfo["name"]] = 1.0
			case "Finished":
				self.threads[eventInfo["name"]] = 3
			case "Failed":
				self.threads[eventInfo["name"]] = None
	
	@property
	def indicator(self) -> Indicator:
		return self.__dict__["indicator"]
	
	@indicator.setter
	def indicator(self, value : Indicator):
		if "indicator" in self.__dict__:
			self.__dict__["indicator"].stop()
		self.__dict__["indicator"] = value
	
	@indicator.deleter
	def indicator(self):
		if "indicator" in self.__dict__:
			self.__dict__["indicator"].stop()
			self.__dict__.pop("indicator")
		else:
			raise AttributeError(f"Indicator has not been set yet, so it can not be deleted.")

	def start(self, *args, **kwargs):
		self.thread = Thread(target=self.indicator.run, args=args, kwargs=kwargs, daemon=True)
		self.thread.start()
	
	def wait(self, timeout=None):
		self.indicator.wait(timeout=timeout)
	
	def kill(self):
		"""Tells updater to stop running, but does not wait for thread to stop."""
		self.indicator.kill()

	def stop(self):
		"""Tells updater to stop running and Waits for updater to stop before returning."""
		self.indicator.stop()

	def updateIndicator(self, eventInfo : dict[str,Any]):
		if eventInfo.get("name") == id(self):
			self.indicator.update()