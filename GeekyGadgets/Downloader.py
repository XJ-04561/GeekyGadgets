
from GeekyGadgets.Globals import *
from GeekyGadgets.URL import URL_TEMPLATE, URL, HTTP, HTTPS, FTP, ping
from GeekyGadgets.Threads import MultiTasker, threadTask
from GeekyGadgets.Hooks import Hooks, GlobalHooks, ProgressHook
from GeekyGadgets.Paths import Path, pathize
from GeekyGadgets.Classy import Default
from urllib.request import urlretrieve, HTTPError
from GeekyGadgets.This import this

class DownloadFailed(Exception):
	@overload
	def __init__(self, name : str, links : Iterable[URL]): ...
	@overload
	def __init__(self, name : str, links : Iterable[tuple[str,URL]]): ...
	def __init__(self, name : str, links : Iterable[URL|tuple[str,URL]]):
		nt = "\n\t"
		f"{name!r} not found.\nSources tried:\n{nt.join(map(lambda x:x if isinstance(x, str) else x[0]+' = '+x[1], links))}"

class Downloader(MultiTasker):

	SOURCES : tuple[tuple[str, URL]] = Default(lambda self: tuple(), lambda self, value: SET__DICT__("SOURCES", tuple((name, URL_TEMPLATE(value)) for name, value in self.SOURCES)))

	postProcessFunc : Callable[[Path],Path]
	directory : Path
	hooks : Hooks


	def __init__(self, *, directory : Path=Path("."), hooks: Hooks=GlobalHooks):
		self.directory = directory
		super().__init__(hooks=hooks)
	
	def __init_subclass__(cls, *args, **kwargs) -> None:
		cls.SOURCES = tuple((name, URL_TEMPLATE(value)) for name, value in cls.SOURCES)
		return super().__init_subclass__(*args, **kwargs)

	def addSources(self, *sources : str):
		self.SOURCES = self.SOURCES + sources
	
	def postProcess(self, name : str, filepath : str, link : URL) -> Path:
		try:
			return self.postProcessFunc(filepath)
		except Exception as e:
			e.add_note(f"This occurred while processing {filepath} downloaded from {link}")
			self.LOG.exception(e)

	@overload
	def download(self, filename : str|Path, query : str|tuple[str]) -> None: ...
	@overload
	def download(self, filename : str|Path, query : str|tuple[str], directory : str|Path) -> None: ...
	@threadTask
	def download(self, filename : str|Path, query : str|tuple[str], directory : str|Path=None) -> None:
		
		filename = pathize(filename)
		directory = pathize(directory or self.directory)
		
		links  = tuple((sourceName, sourceLink.format(query=query)) for sourceName, sourceLink in self.SOURCES)
		for sourceName, link in links:
			if not link.exists:
				continue
				
			outName = link.retrieve(reportHook=self.reporter.progressHook(filename), outPath=directory / filename)

			if outName is None:
				self.reporter.Starting(filename)
				continue
			
			outName = self.postProcess(filename, outName, link)
			if outName and outName.exists:
				return outName
		else:
			exc = DownloadFailed(filename, self.SOURCES)
			self.LOG.exception(exc)
			raise exc
