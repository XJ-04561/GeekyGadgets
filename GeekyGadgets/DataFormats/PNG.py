
import GeekyGadgets.DataFormats.Globals as _GL

import GeekyGadgets.Iterators as _Iterators
import GeekyGadgets.Functions as _Functions

class PngChunk(_GL.Chunk):
	
	CHUNK_TYPE : _GL.Bytes[4]

	length : int
	chunkType : _GL.Bytes[4] = property(lambda self: self.raw[self.start-4:self.start])
	CRC : _GL.Bytes[4] = property(lambda self: self.raw[self.end:self.end+4])
	
	def __init__(self, raw: bytes, start: int) -> None:
		if self.CHUNK_TYPE != raw[start+4:start+8]:
			raise ValueError(f"Tried to create chunk instance of type {self.CHUNK_TYPE}, but raw data has {raw[start+4:start+8]}")
		self.raw = raw
		self.length = int.from_bytes(raw[start:start+4], "big")
		self.start = start + 8
		self.end = start + 8 + self.length
	
	def __init_subclass__(cls) -> None:
		cls.CHUNK_TYPE = cls.__name__.encode("ascii")
		return super().__init_subclass__()
	
	def __len__(self):
		return 12 + self.end - self.start
	
	def cut(self) -> None:
		self.raw = self.raw[self.start-8:self.end+4]
		self.start = 8
		self.end = 12 + self.length

class GenericChunk(PngChunk):
	def __init__(self, raw: bytes, start: int) -> None:
		self.raw = raw
		self.length = int.from_bytes(raw[start:start+4], "big")
		self.start = start + 8
		self.end = start + 8 + self.length

class IHDR(PngChunk):
	
	PALETTE_USED = 1
	COLOR_USED = 2
	ALPHA_USED = 4

	width : int = property(lambda self: self.getInteger(0, 4))
	height : int = property(lambda self: self.getInteger(4, 4))
	bitDepth : int = property(lambda self: self.getInteger(8, 1))
	colorType : int = property(lambda self: self.getInteger(9, 1))
	compressionMethod : int = property(lambda self: self.getInteger(10, 1))
	filterMethod : int = property(lambda self: self.getInteger(11, 1))
	interlaceMethod : int = property(lambda self: self.getInteger(12, 1))

class PLTE(PngChunk):
	
	colors : list[tuple[int,int,int]] = property(lambda self: list(_Iterators.Batched(self.raw[self.start:self.end], 3)))

	def __init__(self, raw: bytes, start: int) -> None:
		super().__init__(raw, start)
		if self.length % 3:
			raise ValueError(f"PLTE chunk data length must be divisible by three, as each color is represented by 3 bytes.")

class tRNS(PngChunk):
	opacities : list[int] = property(lambda self: list(self.raw[self.start:self.end]))
class IDAT(PngChunk): ...
class IEND(PngChunk): ...

class PNG(_GL.BinaryDataStructure):
	
	signature : bytes = bytes([137, 80, 78, 71, 13, 10, 26, 10])
	chunks : list[PngChunk]
	raw : bytes

	header : IHDR = property(lambda self: _Functions.first(filter(lambda x:isinstance(x, IHDR), self.chunks)))

	resolution : tuple[int,int] = property(lambda self: (self.width, self.height))
	width : int = property(lambda self: self.header.width)
	height : int = property(lambda self: self.header.height)
	bitDepth : int = property(lambda self: self.header.bitDepth)
	colorType : int = property(lambda self: self.header.colorType)
	compressionMethod : int = property(lambda self: self.header.compressionMethod)
	filterMethod : int = property(lambda self: self.header.filterMethod)
	interlaceMethod : int = property(lambda self: self.header.interlaceMethod)

	def __init__(self, chunks : "PNG|_GL.Iterable[_GL.Chunk]") -> None:
		if isinstance(chunks, PNG):
			self.chunks = chunks.chunks.copy()
		else:
			self.chunks = list(chunks)
	
	@classmethod
	def parse(cls, raw : bytes) -> None:
		if raw[:8] != cls.signature:
			raise ValueError(f"PNG: Raw bytes does not have the correct PNG signature.\nExpected: {_GL.alignBytes(cls.signature)}\nObserved: {_GL.alignBytes(raw[:8])}")
		
		chunks = []
		i = len(cls.signature)
		N = len(raw)
		while i < N-4:
			chunks.append(createChunk(raw, i))
			i += len(chunks[-1])
		obj = cls(chunks)
		obj.raw = raw
		
		return obj
	
	def __bytes__(self) -> bytes:
		return self.raw
	
	def __repr__(self) -> str:
		return f"<PNG object w/ {len(self.chunks)}>"
	
	def compile(self: "PNG") -> bytes:
		return bytes(self)


def createChunk(raw : bytes, index : int):
	typeName = raw[index+4:index+8]
	for cls in PngChunk.__subclasses__():
		if cls.__name__.encode("ascii") == typeName:
			return cls(raw, index)
	else:
		return GenericChunk(raw, index)