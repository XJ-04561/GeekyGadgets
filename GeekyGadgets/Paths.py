
from GeekyGadgets.Globals import *

class Pathy(ABC):
	writable : "Path|None"
	readable : "Path|None"
	executable : "Path|None"
	fullPerms : "Path|None"

	directory : "Path|PathGroup"
	filename : "Path|PathGroup"

	@abstractmethod
	def find(self, name : "Path|str", purpose : str="r") -> "Path|None": ...
	def __rshift__(self, right : "Path") -> bool:
		if not isinstance(right, Pathy):
			right = Path(right)
		if not right.writable:
			return False
		if not self.writable:
			return False

		os.rename(self.writable, out := right.writable)
		return os.path.exists(out)
	
	def __lshift__(self, right : "Path") -> bool:
		if not isinstance(right, Pathy):
			right = Path(right)
		if not right.writable:
			return False
		if not self.writable:
			return False

		os.rename(right.writable, out := self.writable)
		return os.path.exists(out)

try:
	from PseudoPathy import *
	Pathy.register(Path)
	Pathy.register(PathGroup)
	Pathy.register(PathList)
except ModuleNotFoundError:
	# Not meant to be used! Please install PseudoPathy instead.
	# https://www.GitHub.com/XJ-04561/PseudoPathy

	class Path(str, Pathy):
		def __truediv__(self, other):
			if isinstance(other, Path):
				return type(other)(os.path.join(self, other))
			else:
				return type(self)(os.path.join(self, other))
		def __rtruediv__(self, other):
			return type(self)(os.path.join(other, self))
	class DirectoryPath(Path): pass
	class FilePath(Path): pass
	
	class PathList(list, Pathy):
		def __str__(self):
			return " ".join(map(str, self))
	class DirectoryList(PathList): pass
	class FileList(PathList): pass
	
	class PathGroup(Pathy):
		def __init__(self, iterable : Iterable[Path]):
			self._roots = tuple(iterable)
		def __truediv__(self, other):
			if isinstance(other, FilePath):
				return FileGroup(tuple(x / other for x in self._roots))
			elif isinstance(other, DirectoryPath):
				return DirectoryGroup(tuple(x / other for x in self._roots))
			else:
				return type(self)(os.path.join(self, other))
		def __rtruediv__(self, other):
			return type(self)(tuple(other / x for x in self._roots))
	class DirectoryGroup(PathGroup): pass
	class FileGroup(PathGroup): pass

_T = TypeVar("_T")

@overload
def pathize(string : str) -> Path: ...
@overload
def pathize(string : _T) -> _T: ...
def pathize(string : _T) -> _T:
	if isinstance(string, Pathy):
		return string
	else:
		return Path(string)

