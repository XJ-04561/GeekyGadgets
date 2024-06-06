
from GeekyGadgets.Globals import *

_T = TypeVar("_T")
_TA = TypeVar("_TA")

class Subscriptable:
	def __class_getitem__(cls : _T, args : _TA) -> GenericAlias:
		return GenericAlias(cls, args)