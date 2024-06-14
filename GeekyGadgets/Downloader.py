
from GeekyGadgets.Globals import *
from GeekyGadgets.Logging import Logged
from GeekyGadgets.URL import URL
from GeekyGadgets.Threads import ThreadConnection, Thread, sqlite3
from GeekyGadgets.Hooks import Hooks, GlobalHooks
from GeekyGadgets.Classy import threaded
from GeekyGadgets.Paths import Path
from urllib.request import urlretrieve, HTTPError
from GeekyGadgets.This import this



class ReportHook:

	totalBlocks : int = None
	def __init__(self, reportHook):
		self.reportHook = reportHook
	
	def __call__(self, block, blockSize, totalSize):
		if self.totalBlocks is None:
			self.totalBlocks = (totalSize // blockSize) + 1
		
		self.reportHook(block / self.totalBlocks)

class Job(Logged):

	_queueConnection : ThreadConnection

	query : Any|Iterable
	filename : str
	out : Path = Path(".")
	reportHook : Callable = None

	def __init__(self, query, filename, conn, reportHook=None, out=None, *, logger=None):
		
		if logger is not None:
			self.LOG = logger.getChild(type(self).__name__.split(".")[-1])
		self._queueConnection = conn

		self.query = query
		self.filename = filename
		if reportHook:
			self.reportHook = reportHook
		if out:
			self.out = out
	
	def reserveQueue(self):
		try:
			self._queueConnection.execute("INSERT OR FAIL INTO queueTable (name) VALUES (?);", [self.filename])
		except sqlite3.IntegrityError:
			return False
		else:
			return True
	
	def clearFromQueue(self):
		try:
			self._queueConnection.execute("DELETE FROM queueTable WHERE name = ?;", [self.filename])
		except:
			pass

	def isListed(self):
		return self._queueConnection.execute("SELECT CASE WHEN EXISTS(SELECT 1 FROM queueTable WHERE name = ?) THEN TRUE ELSE FALSE END;", [self.filename]).fetchone()[0]
	def isQueued(self):
		return self._queueConnection.execute("SELECT CASE WHEN EXISTS(SELECT 1 FROM queueTable WHERE name = ? AND progress < 0.0) THEN TRUE ELSE FALSE END;", [self.filename]).fetchone()[0]
	def isDownloading(self):
		return self._queueConnection.execute("SELECT CASE WHEN EXISTS(SELECT 1 FROM queueTable WHERE name = ? AND progress >= 0.0 AND progress < 1.0) THEN TRUE ELSE FALSE END;", [self.filename]).fetchone()[0]
	def isDone(self):
		if self.filename in self.out:
			return self._queueConnection.execute("SELECT CASE WHEN EXISTS(SELECT 1 FROM queueTable WHERE name = ? AND progress > 1.0) THEN TRUE ELSE FALSE END;", [self.filename]).fetchone()[0]
		else:
			return False
	def isPostProcess(self):
		return self._queueConnection.execute("SELECT CASE WHEN EXISTS(SELECT 1 FROM queueTable WHERE name = ? AND progress == 1.0) THEN TRUE ELSE FALSE END;", [self.filename]).fetchone()[0]
	def isDead(self):
		return self._queueConnection.execute("SELECT CASE WHEN EXISTS(SELECT 1 FROM queueTable WHERE name = ? AND modified + 10.0 < UNIXEPOCH()) THEN TRUE ELSE FALSE END;", [self.filename]).fetchone()[0]
	
	def updateProgress(self, prog : float):
		self._queueConnection.execute("UPDATE queueTable SET progress = ?, modified = UNIXEPOCH() WHERE name = ?;", [prog, self.filename])
		self.reportHook(prog)

	def getProgress(self):
		ret = self._queueConnection.execute("SELECT progress FROM queueTable WHERE name = ?;", [self.filename]).fetchone()
		if not ret:
			return None
		else:
			return ret[0]
	
	def updateLoop(self, timeStep : float=0.25):
		
		while not self.isDone():
			if self.isDead():
				self.reportHook(None)
				break
			self.reportHook(self.getProgress())
			sleep(timeStep)
		else:
			self.reportHook(3.0)
	
	def run(self, sources : list[tuple[str, type[URL]]], postProcess : Callable=None):

		try:
			reportHook = ReportHook(self.updateProgress)
			outFile = "N/A"
			for sourceName, sourceLink in sources:
				try:
					link = sourceLink.format(query=self.query)
					filename = link.rsplit("/")[-1]
					(outFile, msg) = urlretrieve(link, filename=self.out / filename, reporthook=reportHook) # Throws error if 404

					if postProcess is not None:
						self.updateProgress(1.0)
						try:
							postProcess(self.out / filename, self.out / self.filename)
						except Exception as e:
							e.add_note(f"This occurred while processing {outFile} downloaded from {sourceLink.format(query=self.query)}")
							self.LOG.exception(e)
							raise e
					elif self.out / filename != (self.out / self.filename):
						os.rename(self.out / filename, self.out / self.filename)
					self.updateProgress(3.0)
					return self.out / filename, sourceName
				except HTTPError as e:
					self.LOG.info(f"Couldn't download from source={sourceName}, url: {sourceLink.format(query=self.query)}, due to {e.args}")
				except Exception as e:
					self.LOG.exception(e)
					raise e
			self.LOG.error(f"No database named {self.filename!r} found online. Sources tried: {', '.join(map(*this[0] + ': ' + this[1], sources))}")
			raise e
		except Exception as e:
			self.updateProgress(None)
			raise e

class Downloader(Logged):

	SOURCES : tuple[tuple[str]] = ()

	directory : Path = Path(".")
	reportHook : Callable=None
	postProcess : Callable=None
	"""Function that takes arguments: block, blockSize, totalSize"""
	timeStep : float = 0.25
	database : Path = f"{__module__}_QUEUE.db"
	jobs : list
	hooks : Hooks = GlobalHooks

	_queueConnection : ThreadConnection
	_threads : list[Thread]= []

	def __init__(self, directory=directory, *, reportHook=None, logger=None, hooks=None, threads=None):

		if os.access(directory, mode=os.R_OK+os.W_OK):
			self.directory = directory
		elif not os.path.exists(directory) and os.makedirs(directory, "rw"):
			self.directory = directory
		else:
			raise PermissionError(f"Missing read and/or write permissions in directory: {directory}")
		self.jobs = []
		
		self._queueConnection = ThreadConnection(self.directory / self.database, identifier=id(self))
		self._queueConnection.execute("CREATE TABLE IF NOT EXISTS queueTable (name TEXT UNIQUE, progress DECIMAL DEFAULT -1.0, modified INTEGER DEFAULT (UNIXEPOCH()));")
		if logger is not None:
			self.LOG = logger.getChild(type(self).__name__.split(".")[-1])
		if reportHook:
			self.reportHook = reportHook
		if hooks:
			self.hooks = hooks
		self._threads = threads if threads is not None else []
		self.LOG.info(f"Created {type(self)} object at 0x{id(self):0>16X}")

	def __del__(self):
		del self._queueConnection

	def addSources(self, *sources : str):
		self.SOURCES = self.SOURCES + sources

	def wait(self):
		threads = self._threads.copy()
		for t in threads:
			try:
				t.join()
				self._threads.remove(t)
			except:
				pass
			if hasattr(t, "exception"):
				raise t.exception
	
	@threaded
	def download(self, query, filename : str, reportHook : "DownloaderReportHook"=None) -> None:
		
		if reportHook:
			pass
		elif self.reportHook:
			reportHook = self.reportHook
		else:
			reportHook = DownloaderReportHook(getattr(self, "__name__", getattr(self.__class__, "__name__")), self.hooks, filename)
		
		job = Job(query, filename, conn=self._queueConnection, reportHook=reportHook, out=self.directory, logger=self.LOG)
		self.jobs.append(job)

		while not job.reserveQueue():
			if job.isDone():
				break
			elif job.isDead():
				job.clearFromQueue()
			else:
				job.updateLoop(timeStep=self.timeStep)
		else:
			job.run(self.SOURCES, postProcess=self.postProcess)


# Implementations

class DownloaderReportHook:

	category : str
	hooks : Hooks
	name : str
	def __init__(self, category : str, hooks : Hooks, name : str):
		self.category = category
		self.hooks = hooks
		self.name = name

	def __call__(self, prog):
		"""
		None	-	Service crashed
		2		-	Never ran/skipped
		3		-	Completed
		0<->1	-	Running
		<0		-	Not started
		1.0		-	Postprocessing
		"""
		if prog == None:
			self.hooks.trigger(self.category+"Failed", {"value" : prog, "name" : self.name})
		elif prog == 2:
			self.hooks.trigger(self.category+"Skipped", {"value" : prog, "name" : self.name})
		elif prog == 3:
			self.hooks.trigger(self.category+"Finished", {"value" : prog, "name" : self.name})
		elif 0 <= prog < 1:
			self.hooks.trigger(self.category+"Progress", {"value" : prog, "name" : self.name})
		elif prog <0:
			self.hooks.trigger(self.category+"Starting", {"value" : prog, "name" : self.name})
		elif prog == 1.0:
			self.hooks.trigger(self.category+"PostProcess", {"value" : prog, "name" : self.name})
		else:
			self.hooks.trigger(self.category+"Failed", {"value" : prog, "name" : self.name})