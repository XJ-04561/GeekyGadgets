
from GeekyGadgets.Globals import *
from GeekyGadgets.URL import URL
from GeekyGadgets.Threads import MultiTasker, taskMethod
from GeekyGadgets.Hooks import Hooks, GlobalHooks, ProgressHook
from GeekyGadgets.Paths import Path
from urllib.request import urlretrieve, HTTPError
from GeekyGadgets.This import this

class ReportHook:

	totalBlocks : int = None
	reportFunction : Callable
	name : str

	def __init__(self, reportFunction : Callable, name : str):
		self.reportFunction = reportFunction
		self.name = name
	
	def __call__(self, block, blockSize, totalSize):
		if self.totalBlocks is None:
			self.totalBlocks = (totalSize // blockSize) + 1
		
		self.reportFunction(block / self.totalBlocks, self.name)

class Downloader(MultiTasker):

	SOURCES : tuple[tuple[str, URL]] = ()

	directory : Path
	postProcess : Callable=None
	hooks : Hooks


	def __init__(self, *, directory : Path=Path("."), hooks: Hooks=GlobalHooks):
		self.directory = directory
		super().__init__(hooks=hooks)

	def addSources(self, *sources : str):
		self.SOURCES = self.SOURCES + sources

	@taskMethod
	def download(self, name : str, query : str|tuple[str], filename : str=None) -> None:
		
		reportHook = ReportHook(self.reporter.Progress)
		outFile = "N/A"
		for sourceName, sourceLink in self.SOURCES:
			try:
				link = sourceLink.format(query=query)
				tempFilename = link.rsplit("/")[-1]
				(outFile, msg) = urlretrieve(link, filename=self.directory / tempFilename, reporthook=reportHook) # Throws error if 404

				if filename is None:
					filename = tempFilename

				if self.postProcess is not None:
					self.reporter.PostProcess(name)
					try:
						self.postProcess(self.directory / tempFilename, self.directory / filename)
					except Exception as e:
						e.add_note(f"This occurred while processing {outFile} downloaded from {sourceLink.format(query=query)}")
						self.LOG.exception(e)
						raise e
				elif self.directory / tempFilename != (self.directory / filename):
					os.rename(self.directory / tempFilename, self.directory / filename)
				self.reporter.Finished(name)
				return self.directory / filename, sourceName
			except HTTPError as e:
				self.LOG.info(f"Couldn't download from source={sourceName}, url: {sourceLink.format(query=query)}, due to {e.args}")
			except Exception as e:
				self.LOG.exception(e)
				raise e
		self.LOG.error(f"No database named {filename!r} found online. Sources tried: {', '.join(map(*this[0] + ': ' + this[1], self.SOURCES))}")
		raise e
