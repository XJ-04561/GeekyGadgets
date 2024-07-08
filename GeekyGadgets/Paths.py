

from PseudoPathy import *
import PseudoPathy.Globals as _Globals
from GeekyGadgets.TypeHinting import *
from PseudoPathy.Globals import Pathy

_T = TypeVar("_T")

@overload
def pathize(string : str) -> Path: ...
@overload
def pathize(string : _T) -> _T: ...
def pathize(string : _T) -> _T:
	if isinstance(string, _Globals.Pathy):
		return string
	elif isinstance(string, str):
		return Path(string)
	elif isinstance(string, Iterable):
		return PathList(string)
	else:
		return Path(string)

