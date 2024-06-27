
from GeekyGadgets.Globals import *
from GeekyGadgets.SpecialTypes import NameSpace
from GeekyGadgets.Formatting.Case import KebabCase, SnakeCase, PascalCase
from GeekyGadgets.Functions import last
from GeekyGadgets.Classy import Default
from GeekyGadgets.Threads import ThreadsMeta


DEFAULT_CONTEXT = {
	"stringDelimiter" : "\"",
	"indentation" : "\t",
	"compact" : False
}
_CONTEXTS = {}

class Semantics: ...
class SemanticsNameSpace(Semantics, NameSpace):
	
	newline : str
	sep : str
	spacing : str
	pairSep : str
	listSep : str
	delimiters : tuple[str,str]
	indentation : str

	def __str__(self):
		if SyntaxContext.compact:
			return f"{self.delimiters[0]}{self.sep.join(map(lambda x: f'{x[0]}{self.pairSep}{self.listSep.join(map(str, x[1])) if isinstance(x[1], (list,tuple)) else x[1]}', self))}{self.delimiters[1]}"
		else:
			return f"{self.delimiters[0]}{self.newline}{self.indentation}{f'{self.sep}{self.newline}{self.indentation}'.join(map(lambda x: f'{x[0]}{self.spacing}{self.pairSep}{self.spacing}{self.listSep.join(map(str, x[1])) if isinstance(x[1], (list,tuple)) else x[1]}', self))}{self.newline}{self.delimiters[1]}"

	def __format__(self, fs):
		return f"{self.delimiters[0]}{self.sep.join(map(lambda x: f'{x[0]}{self.pairSep}{self.listSep.join(map(str, x[1])) if isinstance(x[1], (list,tuple)) else x[1]}', self))}{self.delimiters[1]}"

class Attributes(SemanticsNameSpace):
	
	newline : str = ""
	sep : str = " "
	spacing : str = ""
	pairSep : str = "="
	listSep : str = ","
	delimiters : tuple[str,str] = ("", "")
	indentation : str = ""

	def __str__(self):
		return " ".join(f"{name}={value}" if not isinstance(value, str) else f"{name}={SyntaxContext.repString(value)}" for name, value in self)

class SyntaxContextMeta(type):
	
	CONTEXTS : dict[int,dict[str,Any]] = _CONTEXTS

	stringDelimiter : str
	indentation : str
	attributeSep : str
	pairSep : str
	compact : bool

	def __getattr__(cls, name) -> str:
		return cls.CONTEXTS.get(ThreadsMeta.currentThread.ident, DEFAULT_CONTEXT)[name]
	
	def repString(cls, string : str) -> str:
		return f"{cls.stringDelimiter}{string.replace(cls.stringDelimiter, "\\"+cls.stringDelimiter)}{cls.stringDelimiter}"
	
class SyntaxContext(metaclass=SyntaxContextMeta):
	
	CONTEXTS : dict[int,dict[str,Any]] = _CONTEXTS

	stringDelimiter : str
	indentation : str
	attributeSep : str
	pairSep : str
	compact : bool

	def __init__(self, **kwargs):
		self.context = DEFAULT_CONTEXT | kwargs

	def __getattr__(self, name) -> str:
		return self.CONTEXTS.get(ThreadsMeta.currentThread.ident, DEFAULT_CONTEXT)[name]

	def __enter__(self):
		self.CONTEXTS[ThreadsMeta.currentThread.ident] = self.context
		return self
	
	def __exit__(self, *args, **kwargs):
		self.CONTEXTS.pop(ThreadsMeta.currentThread.ident, None)
	
	def repString(self, string : str) -> str:
		return f"{self.stringDelimiter}{string.replace(self.stringDelimiter, "\\"+self.stringDelimiter)}{self.stringDelimiter}"
