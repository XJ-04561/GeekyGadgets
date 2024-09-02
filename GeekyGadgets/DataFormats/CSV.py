
from GeekyGadgets.DataFormats.Globals import *
import GeekyGadgets.Classy as _Classy

_T = TypeVar("_T")

class CSV(TextDataInterpreter):
	
	PATTERNS_FORMAT = (
		r"""^(?:(?:[^"{sep}\r\n]*)|""|".*?((?<=[^"])(?:"")*"))?"""
		r"""(?:[{sep}](?:[^"{sep}\r\n]*)|""|".*?((?<=[^"])(?:"")*"))*?$""",
		r"""((?<=[{sep}]|[\r\n])|^)((?:(?:[^"{sep}\r\n]*)|""|".*?(?:(?<=[^"])(?:"")*")))(?=[{sep}]|[\r\n]|$)"""
	)
	FORMATTING : dict[str,dict[int,Callable[[str],Any]]|dict[int,Callable[[Any],str]]] = {
		"parse" : {
			1 : lambda self, s:s.replace('""', '"')[1:-1] if s.startswith('"') else s
		},
		"compile" : {
			0 : lambda self, s: "\n".join(s),
			1 : lambda self, s: self.sep.join(s),
			2 : lambda self, s: '"'+format(s).replace('"', '""')+'"' # if isinstance(s := str(s), str) and (any(c in s for c in "\"\n\r") or self.sep in s) else '"'+format(s)+'"'
		}
	}
	SEPS = ",;\t |"

	sep = ","

	def __init__(self, data: list|None=None, sep : str|None=None, header: list|None=None) -> _Classy.NoneType:

		if sep is not None:
			self.sep = sep
		self.PATTERNS = self.COMPILE_PATTERNS(self.sep)
		super().__init__(data=data, header=header)

	@staticmethod
	@cache
	def COMPILE_PATTERNS(sep):
		return [re.compile(string.format(sep=sep), flags=re.MULTILINE|re.DOTALL) for string in CSV.PATTERNS_FORMAT]

class TSV(CSV):
	sep = "\t"

	def __init__(self, data: tuple|None=None) -> _Classy.NoneType:
		if data is not None:
			self.data = data
		self.PATTERNS = self.COMPILE_PATTERNS(self.sep)

def openCSV(filename : str, sep : str|None=None):
	csv = CSV(sep=sep)
	csv.parse(open(filename, "r").read())
	return csv

def openTSV(filename : str):
	tsv = TSV()
	tsv.parse(open(filename, "r").read())
	return tsv