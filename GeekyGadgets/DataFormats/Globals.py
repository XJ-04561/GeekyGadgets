
from GeekyGadgets.Globals import *
from GeekyGadgets.Formatting import alignBytes
import GeekyGadgets.Classy as _Classy
import GeekyGadgets.Functions as _Functions
from ast import literal_eval as parseObjects

_T = TypeVar("_T")

_NONE_PATTERN = re.compile(r"^(none|null|nil|nan|na|n/a|-)$", flags=re.IGNORECASE)

def isNone(string : str):
	return _NONE_PATTERN.fullmatch(string)


class DataStructure(Subscriptable, ABC):
	
	MODE : type[str]|type[bytes]
	IO_TYPE : TextIO|BinaryIO = _Classy.Default(lambda self: (TextIO, _IO.TextIOWrapper) if self.MODE is str else (BinaryIO, _IO.BytesIO))
	raw = None

	@classmethod
	@abstractmethod
	def parse(cls, raw : bytes|str) -> None: ...

	@overload
	def save(self : "DataStructure[str|bytes]", file : TextIO|BinaryIO, /): ...
	@overload
	def save(self : "DataStructure[str|bytes]", filename : str, /): ...
	def save(self, file : TextIO|BinaryIO|str, /):
		if isinstance(file, str):
			file = open(file, "w" if self.MODE is str else "wb")
		
		if not isinstance(file, self.IO_TYPE):
			raise TypeError(f"{_Functions.getTypeName(self)!r} object needs a writeable {_Functions.getName(self.IO_TYPE)} object to output to.")
		
		ret = file.write(self.compile())
		file.flush()

		return ret
	
	@abstractmethod
	def compile(self : "DataStructure[bytes|str]") -> bytes|str: ...

class TextDataInterpreter(DataStructure):
	
	MODE : type[str] = str
	PATTERNS : list[re.Pattern]
	FORMATTING : dict[str,dict[int,Callable[[str],Any]]|dict[int,Callable[[Any],str]]] = {
		"parse" : {},
		"compile" : {}
	}
	N = _Classy.CachedDefault(lambda self: len(self.PATTERNS))

	raw : str|TextIO
	header : list
	data : list
	
	def __init__(self, data: list|None=None, header: list|None=None) -> _Classy.NoneType:
		if data is None:
			self.data = []
		else:
			self.data = data
		if header is None:
			self.header = []
		else:
			self.header = header

	def parse(self : _T, raw: str|TextIO) -> None:
		self.data = self.iterateMatches(raw)
		self.raw = raw
	
	def compile(self) -> str:
		return self.iterateData(self.header+self.data)

	def iterateMatches(self, string, i=0):
		return list(
			self.iterateMatches(m.group(), i+1)
			if i < len(self.PATTERNS)-1
			else self.FORMATTING["parse"][i](self, m.group())
			if i in self.FORMATTING["parse"]
			else m.group()
			for m in self.PATTERNS[i].finditer(string)
		)

	def iterateData(self, data, i=0):
		if i in self.FORMATTING["compile"]:
			return self.FORMATTING["compile"][i](
				self,
				(
					self.iterateData(item, i+1)
					for item in data
				)
				if i < self.N
				else data
			)
		else:
			return format(
				( self.iterateData(item, i+1) for item in data )
				if i < self.N
				else data
			)
		
	
	def add(self, entry : Any):
		self.data.append(entry)
	def addHeader(self, entry : Any):
		self.header.append(entry)

class BinaryDataStructure(DataStructure):
	
	MODE : type[bytes] = bytes

class Chunk(Subscriptable):

	raw : bytes

	start : int
	end : int

	def __init__(self, raw : bytes, start : int, end : int) -> None:
		self.raw = raw
		self.start = start
		self.end = end
		super().__init__()

	def __getitem__(self, relativeIndex : int|slice):
		if isinstance(relativeIndex, int):
			return self.raw[self.start+relativeIndex if relativeIndex >= 0 else self.end + relativeIndex]
		elif isinstance(relativeIndex, slice):
			start = relativeIndex.start
			stop = relativeIndex.stop
			step = relativeIndex.step
			return self.raw[self.start+start if start is not None else self.start:(self.start+stop if stop >= 0 else self.end+stop) if stop is not None else self.end:step if step is not None else 1]
		else:
			TypeError(f"key-argument `relativeIndex` must only be an integer or a slice.")
	
	def __len__(self):
		return self.end - self.start
	
	def getInteger(self, relativeIndex, size, byteOrder="big"):
		return int.from_bytes(self.raw[self.start+relativeIndex:self.start+relativeIndex+size], byteOrder)

try:
	import GeekyGadgets.IO as _IO
except ImportError:
	pass