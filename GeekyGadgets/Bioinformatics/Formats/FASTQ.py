
from GeekyGadgets.Bioinformatics.Globals import *
from GeekyGadgets.Classy import Default
from GeekyGadgets.Formatting.SISize import shortenNumber
from GeekyGadgets.Logging import Logged, ROOT_LOGGER
from GeekyGadgets.Hooks import GlobalHooks, Hooks
from GeekyGadgets.Iterators import Batched, Count
import gunzip

__all__ = ("subSampleFASTQ", "subSampleName", "RandomReads", "createReadsIndex")

LOGGER = ROOT_LOGGER.getChild(__name__)

SUB_SAMPLE_NAMES = {
	"reads" : "Reads",
	"coverage" : "Coverage",
	"dilution" : "Dilution",
	"bases" : "Bases",
	"bytes" : "Bytes"
}

class RandomReads(random.Random):
	
	length : int = Default["reads"](lambda self : len(self.reads))
	
	@overload
	def __init__(self, reads : Iterable[str], x: int | float | str | bytes | bytearray | None = None, *, condition : Callable[[str],bool]) -> None: ...
	@overload
	def __init__(self, reads : Iterable[Iterable[int,int,int]], x: int | float | str | bytes | bytearray | None = None, *, condition : Callable[[list[int,int,int]],bool]) -> None: ...
	def __init__(self, reads : Iterable[str|Iterable[int,int,int]], x: int | float | str | bytes | bytearray | None = None, *, condition : Callable[[str|Iterable[int,int,int]],bool]) -> None:
		super().__init__(x)
		self.reads = reads
	
	def getReads(self, n : int) -> list:
		self.choices(self.reads, k=n)
	
	def superSample(self, factor : float, excl : bool=True) -> list:
		
		factor = max(1, factor)
		whole, rest = factor // 1, factor % 1
		out = [list(self.reads) for i in range(whole)] + self.choices(self.reads, k=int(self.length*rest) + (0 if excl else bool(self.length*rest % 1)))
		self.shuffle(out)
		return out
	
	def subSample(self, factor : float, excl : bool=True) -> list:
		
		factor = min(1, factor)
		return self.choices(self.reads, k=int(self.length*factor) + (0 if excl else bool(self.length*factor % 1)))
	
	def infiniteReads(self) -> Generator[list[int,int,int],None,None]:
		readIndices = list(range(self.reads))
		while True:
			self.shuffle(readIndices)
			for i in readIndices:
				yield self.reads[i]

def subSampleName(name : FilePath|DirectoryPath|str, type : Literal["reads","coverage","dilution","bases","bytes"], *N, index : int=None) -> str:
	
	if index is None:
		bracketedID = f"[{SUB_SAMPLE_NAMES[type]}-{'-'.join(map(shortenNumber, N))}]"
	else:
		bracketedID = f"[{SUB_SAMPLE_NAMES[type]}-{str(index).zfill(len(str(N[0])))}-{'-'.join(map(shortenNumber, N))}]"
	if isinstance(name, FilePath):
		return name.name + bracketedID + "." + name.ext
	elif isinstance(name, DirectoryPath):
		return os.path.basename(name) + bracketedID
	else:
		newName, *ext = os.path.basename(name)[1:].split(".")
		name, ext = os.path.basename(name)[0]+newName, ".".join(ext)
		if ext:
			ext = "." + ext
		
		return name + bracketedID + ext

class ProgressTracker(list):
	def __init__(self, n : int, goal : int|float, factor : int|float=1, **kwargs):
		super().__init__(0 for _ in range(n))
		self.n = n
		self.goal = goal
		self.factor = factor
		for name, value in kwargs.items():
			setattr(self, name, value)
	
	def __iter__(self):
		for p in super().__iter__():
			yield self.factor * p / self.goal

	def update(self, other):
		for i, x in enumerate(other):
			self[i] += 1
	
	def mean(self):
		return self.goal * self.norm()
	
	def norm(self):
		return sum(self) / self.n

class ReadsProgressTracker(ProgressTracker): ...

class CoverageProgressTracker(ProgressTracker): ...

class DilutionProgressTracker(ProgressTracker): ...

class BasesProgressTracker(ProgressTracker):
	def update(self, other):
		for i, x in enumerate(other):
			self[i] += sum(map(lambda y:y[0][0], x))

class BytesProgressTracker(ProgressTracker):
	def update(self, other):
		for i, x in enumerate(other):
			self[i] += sum(map(lambda y:y[0][2] - y[0][1], x))

def getProgressCallback(subSamplingType : str, n : int, *args, **kwargs):
	match subSamplingType:
		case "reads":
			return ReadsProgressTracker(n, goal=args[0])
		case "coverage":
			return CoverageProgressTracker(n, goal=args[0], factor=args[1] / args[2])
		case "dilution":
			return DilutionProgressTracker(n, goal=1/args[0], factor=1/args[1])
		case "bases":
			return BasesProgressTracker(n, goal=args[0])
		case "bytes":
			return BytesProgressTracker(n, goal=args[0])

def createReadsIndex(filepath : FilePath, ioFunc : Callable[[str,str],BinaryIO]):
	
	if os.path.exists(f"{filepath.name}_readsIndex.csv"):
		return [[int(x) for x in row.strip().split(",")] for row in open(f"{filepath.name}_readsIndex.csv", "r")]
	
	pos = -1
	readList = []
	with ioFunc(filepath, "rb") as file:
		while pos != (pos := file.tell()):
			if not file.readline().startswith(b"@"):
				continue
			read = []
			for line in file:
				if not line.strip().isalpha():
					qualHeader = line
					break
				read.append(line)
			
			if qualHeader.startswith(b"+"):
				file.seek(sum(map(len, read)), 1)
			elif qualHeader:
				file.seek(-len(qualHeader), 1)
			readList.append([sum(map(len, map(bytes.strip, read))), pos, file.tell()])
	try:
		with open(f"{filepath.name}_readsIndex.csv", "w") as file:
			for row in readList:
				file.write(f"{row[0]},{row[1]},{row[2]}\n")
	except:
		pass
			
	return readList

@overload
def subSampleFASTQ(files : int, source : FilePath|FileList[FilePath], *, reads : list[int], **kwargs) -> list[tuple[str]]: ...
@overload
def subSampleFASTQ(files : int, source : FilePath|FileList[FilePath], *, coverage : list[int,int], **kwargs) -> list[tuple[str]]: ...
@overload
def subSampleFASTQ(files : int, source : FilePath|FileList[FilePath], *, dilution : list[int], **kwargs) -> list[tuple[str]]: ...
@overload
def subSampleFASTQ(files : int, source : FilePath|FileList[FilePath], *, bytes : list[int], **kwargs) -> list[tuple[str]]: ...
@overload
def subSampleFASTQ(files : int, source : FilePath|FileList[FilePath], *,
			   reads : list[int]=None, dilution : list[int]=None, coverage : list[int,int]=None, bytes : list[int]=None, bases : list[int]=None,
			   outDir : DirectoryPath=None, hooks=GlobalHooks, steps : int=100) -> list[tuple[str]]: ...
def subSampleFASTQ(files : int, source : FilePath|FileList[FilePath], *,
			   outDir : DirectoryPath=None, hooks=GlobalHooks, steps : int=100,
			   **kwargs) -> list[tuple[str]]:
	
	LOGGER.info(f"Sub Sampling: From {source}.")

	if isinstance(source, str):
		source = FileList([FilePath(source)])
	elif isinstance(source, Iterable):
		source = FileList(FilePath(name) for name in source)
	
	if all(filepath.endswith(".gz") for filepath in source):
		LOGGER.info("Sub Sampling: From and to gzip-data.")
		dataOpen = gunzip.gzip.open
	elif not any(filepath.endswith(".gz") for filepath in source):
		LOGGER.info("Sub Sampling: From and to raw-data.")
		dataOpen = open
	else:
		raise ValueError(f"Files are not consistent in their compression file extensions: {source}")
	
	LOGGER.info("Sub Sampling: Creating Read Index.")
	readsIndex = []
	for filepath in source:
		readsIndex.append(createReadsIndex(filepath, dataOpen))
	LOGGER.info(f"Sub Sampling: Found {', '.join(map(str, map(len, readsIndex)))} reads for the source file(s).")

	for name in ["reads", "dilution", "coverage", "bases", "bytes"]:
		if name in kwargs:
			varName, values = name, kwargs[name]
			LOGGER.info(f"Sub Sampling: Using {values[0]} {SUB_SAMPLE_NAMES[name]}.")
			progressTracker = getProgressCallback(name, files, *values, totalReads=len(readsIndex[0]))
			break
	else:
		raise ValueError("No sub sampling information given, check keyword arguments of `splitFastq`.")

	hooks.trigger("SplitFastq", {"type" : "Starting", "name" : source.name, "value" : 0.0})
	outNames = [tuple((outDir or filepath.directory) / subSampleName(filepath, varName, files, *values, index=i+1) for filepath in source) for i in range(files)]

	if all(os.path.exists(filename) for filenames in outNames for filename in filenames):
		hooks.trigger("SplitFastq", {"type" : "Skipped", "name" : source.name, "value" : 2})
		return outNames
	
	dataFiles : list[BinaryIO] = [dataOpen(filepath, "rb") for filepath in source]
	outData : list[list[BinaryIO]] = [[[] for filename in filenames] for filenames in outNames]
	outFiles : list[list[BinaryIO]] = [[dataOpen(filename, "wb") for filename in filenames] for filenames in outNames]
	
	threshold = 0
	# First 1/4 of progress
	LOGGER.info(f"Sub Sampling: Read Selection.")
	for readSet in Batched(RandomReads(readsIndex).infiniteReads(), len(outData)):
		for prog, sampleData, outReads in zip(progressTracker, outData, readSet):
			if prog < 1.0:
				for fileData, read in zip(sampleData, outReads):
					fileData.append(read)
		progressTracker.update(outData)
		if progressTracker.norm() >= 1.0:
			break
		elif steps * (1/4) * progressTracker.norm() >= threshold:
			hooks.trigger("SplitFastq", {"type" : "Progress", "name" : source.name, "value" : min(1.0, (1/4) * progressTracker.norm())})
			threshold += 1
	
	# 2/4 of progress
	LOGGER.info(f"Sub Sampling: Read Aggregation.")
	readsAggregates = [[] for _ in outFiles[0]]
	for i, data, files in zip(Count(), outData, outFiles):
		if steps * ((1/4) + (1/4) * i / len(outFiles)) >= threshold:
			hooks.trigger("SplitFastq", {"type" : "Progress", "name" : source.name, "value" : min(1.0, (1/4) + (1/4) * i / len(outFiles))})
			threshold += 1
		for fileN, file, reads in zip(Count(), files, data):
			readsAggregates[fileN].extend((file, read) for read in reads)

	# 3/4 of progress
	LOGGER.info(f"Sub Sampling: Read Sorting.")
	for i, aggregate in enumerate(readsAggregates):
		if steps * ((2/4) + (1/4) * i / len(readsAggregates)) >= threshold:
			hooks.trigger("SplitFastq", {"type" : "Progress", "name" : source.name, "value" : min(1.0, (2/4) + (1/4) * i / len(readsAggregates))})
			threshold += 1
		aggregate.sort(key=lambda x:x[1][1])

	# 4/4 of progress
	LOGGER.info(f"Sub Sampling: Writing Files.")
	for i, aggregate, dataFile in zip(Count(), readsAggregates, dataFiles):
		if steps * ((3/4) + (1/4) * i / len(readsAggregates)) >= threshold:
			hooks.trigger("SplitFastq", {"type" : "Progress", "name" : source.name, "value" : min(1.0, (3/4) + (1/4) * i / len(readsAggregates))})
			threshold += 1
		for file, read in aggregate:
			dataFile.seek(read[1])
			file.write(dataFile.read(read[2] - read[1]))
	hooks.trigger("SplitFastq", {"type" : "Progress", "name" : source.name, "value" : 1.0})

	for files in outFiles:
		for file in files:
			file.close()
	hooks.trigger("SplitFastq", {"type" : "Finished", "name" : source.name, "value" : 3})

	LOGGER.info(f"Sub Sampling: Finished!")
	
	return outNames
