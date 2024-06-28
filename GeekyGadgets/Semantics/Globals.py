
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
		cls = GETATTR(self, "__class__")
		if SyntaxContext.compact:
			return f"{cls.delimiters[0]}{cls.sep.join(map(lambda x: f'{KebabCase(x[0])}{cls.pairSep}{cls.listSep.join(map(str, x[1])) if isinstance(x[1], (list,tuple)) else SyntaxContext.repString(x[1]) if isinstance(x[1], str) else x[1]}', dict.items(self)))}{cls.delimiters[1]}"
		else:
			return f"{cls.delimiters[0]}{cls.newline}{cls.indentation}{f'{cls.sep}{cls.newline}{cls.indentation}'.join(map(lambda x: f'{KebabCase(x[0])}{cls.spacing}{cls.pairSep}{cls.spacing}{cls.listSep.join(map(str, x[1])) if isinstance(x[1], (list,tuple)) else SyntaxContext.repString(x[1]) if isinstance(x[1], str) else x[1]}', dict.items(self)))}{cls.newline}{cls.delimiters[1]}"

	def __format__(self, fs):
		cls = GETATTR(self, "__class__")
		return f"{cls.delimiters[0]}{cls.sep.join(map(lambda x: f'{KebabCase(x[0])}{cls.pairSep}{cls.listSep.join(map(str, x[1])) if isinstance(x[1], (list,tuple)) else SyntaxContext.repString(x[1]) if isinstance(x[1], str) else x[1]}', dict.items(self)))}{cls.delimiters[1]}"

class Attributes(SemanticsNameSpace):
	
	newline : str = ""
	sep : str = " "
	spacing : str = ""
	pairSep : str = "="
	listSep : str = ","
	delimiters : tuple[str,str] = ("", "")
	indentation : str = ""

	def __str__(self):
		return " ".join(f"{KebabCase(name)}={value}" if not isinstance(value, str) else f"{KebabCase(name)}={SyntaxContext.repString(value)}" for name, value in self)

class SyntaxContextMeta(type):

	stringDelimiter : str
	indentation : str
	attributeSep : str
	pairSep : str
	compact : bool

	def __new__(cls, className, bases, namespace):
		return super().__new__(cls, className, bases, namespace)

	def __getattr__(cls, name) -> str:
		if ThreadsMeta.currentThread.ident in _CONTEXTS:
			return _CONTEXTS[ThreadsMeta.currentThread.ident][name]
		else:
			return DEFAULT_CONTEXT[name]
	
class SyntaxContext(metaclass=SyntaxContextMeta):

	stringDelimiter : str
	indentation : str
	attributeSep : str
	pairSep : str
	compact : bool

	def __init__(self, **kwargs):
		self.context = DEFAULT_CONTEXT | kwargs

	def __getattr__(self, name) -> str:
		return self.context.get(ThreadsMeta.currentThread.ident, DEFAULT_CONTEXT)[name]

	def __enter__(self):
		self.context[ThreadsMeta.currentThread.ident] = self.context
		return self
	
	def __exit__(self, *args, **kwargs):
		self.context.pop(ThreadsMeta.currentThread.ident, None)
	
	@classmethod
	def repString(cls, string : str) -> str:
		if ThreadsMeta.currentThread.ident in _CONTEXTS:
			delim = _CONTEXTS[ThreadsMeta.currentThread.ident]["stringDelimiter"]
		else:
			delim = DEFAULT_CONTEXT["stringDelimiter"]
		return f"{delim}{string.replace(delim, BACKSLASH+delim)}{delim}"