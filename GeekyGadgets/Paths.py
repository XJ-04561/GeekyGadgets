


try:
	from PseudoPathy import *
except ModuleNotFoundError:
	import os
	from typing import Iterable
	# Not meant to be used! Please install PseudoPathy instead.
	# https://www.GitHub.com/XJ-04561/PseudoPathy

	class Pathy: pass

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