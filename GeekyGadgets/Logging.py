
import GeekyGadgets.Globals as _GL
from GeekyGadgets.Globals import ROOT_LOGGER
import GeekyGadgets.Formatting as _Formatting

@_GL.overload
def logTo(*, file : _GL.BinaryIO, level : int|None=None, logger=_GL.ROOT_LOGGER): ...
@_GL.overload
def logTo(*, filename : _GL.Path, level : int|None=None, logger=_GL.ROOT_LOGGER): ...
def logTo(*, file : _GL.BinaryIO|None=None, filename : _GL.FilePath|None=None, logger=_GL.ROOT_LOGGER, level=0, format : _GL.logging.Formatter|dict[str,_GL.Any]|str=_GL.logging.Formatter("[%(name)s.%(funcName)s (%(threadName)s)] %(asctime)s - %(levelname)s: %(message)s")):
	
	if isinstance(format, _GL.logging.Formatter):
		formatter = format
	elif isinstance(format, dict):
		formatter = _GL.logging.Formatter(**format)
	else:
		formatter = _GL.logging.Formatter(format)
	
	if file is not None:
		handler = _GL.logging.StreamHandler(file)
		if level is not None:
			handler.setLevel(level=level)
		handler.setFormatter(formatter)
		logger.addHandler(handler)
	
	if filename is not None:
		if not isinstance(filename, _GL.Pathy):
			filename = _GL.Path(filename)
		handler = _GL.logging.FileHandler(filename.writable / f"{_Formatting.timeStamp()}.log" if _GL.os.path.isdir(filename.writable) else filename.writable)
		if level is not None:
			handler.setLevel(level=level)
		handler.setFormatter(formatter)
		logger.addHandler(handler)
	
	logger.addHandler(handler)

def setLevel(level : int=0, logger=_GL.ROOT_LOGGER):
	# logging.basicConfig(level=level)
	logger.setLevel(level=level)

class Logged:
	
	LOG : _GL.logging.Logger = _GL.ROOT_LOGGER

	def __init_subclass__(cls, *args, **kwargs) -> None:
		super().__init_subclass__(*args, **kwargs)
		cls.LOG = cls.LOG.getChild(cls.__name__)