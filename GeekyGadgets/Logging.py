
from GeekyGadgets.Globals import *

__all__ = ("Logged", "logging")

class Logged:
	
	LOG : logging.Logger = ROOT_LOGGER

	def __init_subclass__(cls, *args, **kwargs) -> None:
		super().__init_subclass__(*args, **kwargs)
		cls.LOG = cls.LOG.getChild(cls.__name__)