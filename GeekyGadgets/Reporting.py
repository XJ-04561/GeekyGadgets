
from GeekyGadgets.Globals import * 
from GeekyGadgets.Hooks import *
from GeekyGadgets.Hooks import GlobalHooks, Hooks
from GeekyGadgets.Threads.Synch import Lock
from GeekyGadgets.Threads.Dummies import DummyLock
from GeekyGadgets.SQL import ThreadConnection, sqlite3
from GeekyGadgets.Paths import Path

class Reporter:

	category : str
	hooks : Hooks
	name : str

	def __init__(self, *, category : str, name : str=None, hooks : Hooks=GlobalHooks):
		self.category = category
		self.hooks = hooks
		self.name = name
	
	@overload
	def Starting(self): ...
	@overload
	def Starting(self, name : str): ...
	def Starting(self, name : str=None):
		if name or self.name:
			self.hooks.trigger(self.category, {"name" : name or self.name, "type" : "Starting"})
		else:
			raise ValueError(f"Name of progress report is not set and was not provided through report call.")

	def progressHook(self, name : str) -> partial:
		return partial(self.Progress, name=name)

	@overload
	def Progress(self, progress : float): ...
	@overload
	def Progress(self, progress : float, name : str): ...
	def Progress(self, progress : float, name : str=None):
		"""
		None	-	Service crashed
		2		-	Never ran/skipped
		3		-	Completed
		0<->1	-	Running
		<0		-	Not started
		1.0		-	Postprocessing
		"""
		if name or self.name:
			
			if 0 <= progress < 1:
				self.hooks.trigger(self.category, {"name" : name or self.name, "type" : "Progress", "value" : progress})
			elif progress == None:
				self.hooks.trigger(self.category, {"name" : name or self.name, "type" : "Failed"})
			elif progress == 2:
				self.hooks.trigger(self.category, {"name" : name or self.name, "type" : "Skipped"})
			elif progress == 3:
				self.hooks.trigger(self.category, {"name" : name or self.name, "type" : "Finished"})
			elif progress <0:
				self.hooks.trigger(self.category, {"name" : name or self.name, "type" : "Starting"})
			elif progress == 1.0:
				self.hooks.trigger(self.category, {"name" : name or self.name, "type" : "PostProcess"})
			else:
				self.hooks.trigger(self.category, {"name" : name or self.name, "type" : "Failed"})
		else:
			raise ValueError(f"Name of progress report is not set and was not provided through report call.")

	@overload
	def PostProcess(self): ...
	@overload
	def PostProcess(self, name : str): ...
	def PostProcess(self, name : str=None):
		if name or self.name:
			self.hooks.trigger(self.category, {"name" : name or self.name, "type" : "PostProcess"})
		else:
			raise ValueError(f"Name of progress report is not set and was not provided through report call.")

	@overload
	def Failed(self): ...
	@overload
	def Failed(self, name : str): ...
	def Failed(self, name : str=None):
		if name or self.name:
			self.hooks.trigger(self.category, {"name" : name or self.name, "type" : "Failed"})
		else:
			raise ValueError(f"Name of progress report is not set and was not provided through report call.")

	@overload
	def Skipped(self): ...
	@overload
	def Skipped(self, name : str): ...
	def Skipped(self, name : str=None):
		if name or self.name:
			self.hooks.trigger(self.category, {"name" : name or self.name, "type" : "Skipped"})
		else:
			raise ValueError(f"Name of progress report is not set and was not provided through report call.")

	@overload
	def Finished(self): ...
	@overload
	def Finished(self, name : str): ...
	def Finished(self, name : str=None):
		if name or self.name:
			self.hooks.trigger(self.category, {"name" : name or self.name, "type" : "Finished"})
		else:
			raise ValueError(f"Name of progress report is not set and was not provided through report call.")

"""
None	-	Service crashed
2		-	Never ran/skipped
3		-	Completed
0<->1	-	Running
<0		-	Not started
1.0		-	Postprocessing
"""

SCOREBOARD = {
	"Failed" : None,
	"Skipped" : 2,
	"Finished" : 3,
	"Starting" : -1,
	"Progress" : 0,
	"PostProcess" : 1
}

class Advisor(ABC):

	ledger : Any
	lock : Lock
	category : str
	hooks : Hooks
	name : str

	def __init__(self, *, category : str, hooks : Hooks=GlobalHooks):
		self.category = category
		self.hooks = hooks
		self.hooks.addHook(self.category, target=self.progressCallback)

	@abstractmethod
	def progressCallback(self, eventInfo : dict): ...
	def askProgress(self, name : str) -> float|int|None:
		return self.askStatus(name)[0]
	@abstractmethod
	def askStatus(self, name : str) -> tuple[float|int|None, float]: ...
	@abstractmethod
	def request(self, name : str): ...
	@abstractmethod
	def clear(self, name : str): ...
	def isStarting(self, name : str) -> bool:
		with self.lock:
			return (ret := self.askProgress(name)) and ret < 0
	
	def isRunning(self, name : str) -> bool:
		with self.lock:
			return isinstance(ret := self.askProgress(name), (int, float)) and 0 <= ret < 1
	
	def isComplete(self, name : str) -> bool:
		with self.lock:
			return (ret := self.askProgress(name)) and ret > 1
	
	def isPostProcess(self, name : str) -> bool:
		with self.lock:
			return (ret := self.askProgress(name)) and ret == 1
	
	def isDead(self, name : str, tolerance : float=10.0) -> bool:
		with self.lock:
			return (ret := self.askStatus(name))[0] is None or (ret[1] + tolerance) < time.time()

class DictAdvisor(Advisor):

	ledger : dict[str,tuple[float|int|None,float]] = {}
	lock : Lock = Lock()
	
	def progressCallback(self, eventInfo : dict):
		with self.lock:
			if "name" in eventInfo:
				if "value" in eventInfo:
					self.ledger[eventInfo["name"]] = (eventInfo["value"], time.time())
				elif "type" in eventInfo:
					self.ledger[eventInfo["name"]] = (SCOREBOARD[eventInfo["type"]], time.time())
	
	def askStatus(self, name : str) -> tuple[float|int|None, float]:
		with self.lock:
			if name in self.ledger:
				return self.ledger[name]
			else:
				return (NULL, 0)
	
	def request(self, name : str):
		with self.lock:
			if name not in self.ledger:
				self.ledger[name] = (-1, time.time())
				return True
			else:
				return False
	
	def clear(self, name : str):
		with self.lock:
			del self.ledger[name]

class DatabaseAdvisor(Advisor):
	
	ledger : ThreadConnection
	lock : Lock = DummyLock()

	def __init__(self, *, category: str, directory: Path=Path("."), hooks: Hooks = GlobalHooks):
		self.ledger = ThreadConnection(directory / f".{category}.db", identifier=id(self))
		self.ledger.execute("CREATE TABLE IF NOT EXISTS queueTable (name TEXT UNIQUE, progress DECIMAL DEFAULT -1.0, modified INTEGER DEFAULT (UNIXEPOCH()));")
		super().__init__(category=category, hooks=hooks)
	
	def progressCallback(self, eventInfo : dict):
		if "name" in eventInfo:
			if "value" in eventInfo:
				self.ledger.execute("UPDATE queueTable SET progress = ?, modified = UNIXEPOCH() WHERE name = ?;", [eventInfo["value"], eventInfo["name"]])
			elif "type" in eventInfo:
				self.ledger.execute("UPDATE queueTable SET progress = ?, modified = UNIXEPOCH() WHERE name = ?;", [SCOREBOARD[eventInfo["type"]], eventInfo["name"]])
	
	def askStatus(self, name : str):
		if self.ledger.execute("SELECT CASE WHEN EXISTS(SELECT 1 FROM queueTable WHERE name = ?) THEN TRUE ELSE FALSE END;", [name]).fetchone()[0]:
			return self.ledger.execute("SELECT progress, modified FROM queueTable WHERE name = ?;", [name]).fetchone()
		else:
			return (NULL, 0)
	
	def request(self, name : str, tolerance : float = 10.0):
		try:
			self.clear(name, tolerance)
			self.ledger.execute("INSERT OR FAIL INTO queueTable (name) VALUES (?);", [name])
			return True
		except sqlite3.IntegrityError:
			return False
	
	def clear(self, name : str, tolerance : float = 10.0):
		try:
			self.ledger.execute("DELETE FROM queueTable WHERE name = ? AND modified + ? < UNIXEPOCH();", [name, tolerance])
		except:
			pass