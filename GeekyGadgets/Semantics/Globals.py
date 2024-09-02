
from GeekyGadgets.Globals import *

import GeekyGadgets.SpecialTypes as _SpecialTypes
import GeekyGadgets.Formatting.Case as _Case
import GeekyGadgets.Threads as _Threads
import GeekyGadgets.Classy as _Classy

DEFAULT_CONTEXT = {
	"stringDelimiter" : "\"",
	"INDENTATION" : "\t",
	"compact" : False
}
_CONTEXTS = {}

# class StringValues(ABC): ...
# StringValues.register(str)
# StringValues.register(_SpecialTypes.Percent)

class Semantics(ABC): ...
class SemanticsNameSpace(Semantics, _SpecialTypes.NameSpace):
	
	NEWLINE : str
	SEP : str
	SPACING : str
	PAIRSEP : str
	LISTSEP : str
	LISTJOIN : Callable[[list|tuple],str]
	DELIMITERS : tuple[str,str]
	INDENTATION : str

	def __init_subclass__(cls) -> _Case.NoneType:
		if hasattr(cls, "LISTSEP"):
			cls.LISTJOIN = lambda iterable: cls.LISTSEP.join(map(SyntaxContext.format, iterable))
		return super().__init_subclass__()

	def __getattribute__(self, name: str) -> Any:
		if name in self:
			return self[name]
		else:
			for case in [_Case.KebabCase, _Case.CamelCase, _Case.SnakeCase]:
				if case(name) in self:
					return self[case(name)]
			return self[name]
	
	def __setattr__(self, name: str, value: Any) -> None:
		if name in self:
			self[name] = value
		else:
			self[_Case.KebabCase(name)] = value
		
	def __delattr__(self, name: str) -> None:
		if name in self:
			self[name]
		else:
			self[_Case.KebabCase(name)]

	def __str__(self):
		cls = GETATTR(self, "__class__")
		if SyntaxContext.compact:
			return (
				f"{cls.DELIMITERS[0]}"
				f"{cls.SEP.join(
					f'{name}{cls.PAIRSEP}{cls.LISTJOIN(value) if isinstance(value, (list,tuple)) else SyntaxContext.format(value)}'
					for name, value in dict.items(self)
				)}"
				f"{cls.DELIMITERS[1]}"
			)
		else:
			return f"{cls.DELIMITERS[0]}{cls.NEWLINE}{cls.INDENTATION}{f'{cls.SEP}{cls.NEWLINE}{cls.INDENTATION}'.join(map(lambda x: f'{x[0]}{cls.SPACING}{cls.PAIRSEP}{cls.SPACING}{cls.LISTSEP.join(map(SyntaxContext.format, x[1])) if isinstance(x[1], (list,tuple)) else SyntaxContext.format(x[1])}', dict.items(self)))}{cls.NEWLINE}{cls.DELIMITERS[1]}"

	def __format__(self, fs):
		cls = GETATTR(self, "__class__")
		return f"{cls.DELIMITERS[0]}{cls.SEP.join(map(lambda x: f'{x[0]}{cls.PAIRSEP}{cls.LISTSEP.join(map(SyntaxContext.format, x[1])) if isinstance(x[1], (list,tuple)) else SyntaxContext.format(x[1])}', dict.items(self)))}{cls.DELIMITERS[1]}"

class Ruleset(SemanticsNameSpace):
	
	NEWLINE : str = "\n"
	SEP : str = ";"
	SPACING : str = " "
	PAIRSEP : str = ":"
	LISTSEP : str = " "
	DELIMITERS : tuple[str,str] = ("{", "}")
	INDENTATION : str = "\t"

	def __str__(self):
		cls = GETATTR(self, "__class__")
		if SyntaxContext.compact:
			return f"{cls.DELIMITERS[0]}{cls.SEP.join(map(lambda x: f'{_Case.SnakeCase(x[0])}{cls.PAIRSEP}{cls.LISTSEP.join(map(str, x[1])) if isinstance(x[1], (list,tuple)) else x[1]}', dict.items(self)))}{cls.DELIMITERS[1]}"
		else:
			return f"{cls.DELIMITERS[0]}{cls.NEWLINE}{cls.INDENTATION}{f'{cls.SEP}{cls.NEWLINE}{cls.INDENTATION}'.join(map(lambda x: f'{_Case.SnakeCase(x[0])}{cls.SPACING}{cls.PAIRSEP}{cls.SPACING}{cls.LISTSEP.join(map(str, x[1])) if isinstance(x[1], (list,tuple)) else x[1]}', dict.items(self)))}{cls.NEWLINE}{cls.DELIMITERS[1]}"

	def __format__(self, fs):
		cls = GETATTR(self, "__class__")
		return f"{cls.DELIMITERS[0]}{cls.SEP.join(map(lambda x: f'{_Case.SnakeCase(x[0])}{cls.PAIRSEP}{cls.LISTSEP.join(map(str, x[1])) if isinstance(x[1], (list,tuple)) else x[1]}', dict.items(self)))}{cls.DELIMITERS[1]}"

class AttributeCSS(Ruleset):
	
	NEWLINE = ""
	INDENTATION = ""
	DELIMITERS : tuple[str,str] = _Classy.ClassProperty(lambda self: (SyntaxContext.stringDelimiter, SyntaxContext.stringDelimiter))

	def __init__(self, properties : "dict[str,str|Number|_CSS.ValueStatement]") -> None:
		dict.update(self, properties)

class Attributes(SemanticsNameSpace):
	
	NEWLINE : str = ""
	SEP : str = " "
	SPACING : str = ""
	PAIRSEP : str = "="
	LISTSEP : str = ","
	DELIMITERS : tuple[str,str] = ("", "")
	INDENTATION : str = ""

	def __str__(self):
		cls = GETATTR(self, "__class__")
		return " ".join(f"{name}={SyntaxContext.format(value)}" for name, value in self)

class SyntaxContextMeta(type):

	stringDelimiter : str
	INDENTATION : str
	attributeSep : str
	PAIRSEP : str
	compact : bool

	def __new__(cls, className, bases, namespace):
		return super().__new__(cls, className, bases, namespace)

	def __getattr__(cls, name) -> str:
		if _Threads.ThreadsMeta.currentThread.ident in _CONTEXTS:
			return _CONTEXTS[_Threads.ThreadsMeta.currentThread.ident][name]
		else:
			return DEFAULT_CONTEXT[name]
	
class SyntaxContext(metaclass=SyntaxContextMeta):

	stringDelimiter : str
	INDENTATION : str
	attributeSep : str
	PAIRSEP : str
	compact : bool

	def __init__(self, **kwargs):
		self.context = DEFAULT_CONTEXT | kwargs

	def __getattr__(self, name) -> str:
		return self.context.get(_Threads.ThreadsMeta.currentThread.ident, DEFAULT_CONTEXT)[name]

	def __enter__(self):
		self.context[_Threads.ThreadsMeta.currentThread.ident] = self.context
		return self
	
	def __exit__(self, *args, **kwargs):
		self.context.pop(_Threads.ThreadsMeta.currentThread.ident, None)
	
	@classmethod
	def repString(cls, string : str) -> str:
		if _Threads.ThreadsMeta.currentThread.ident in _CONTEXTS:
			delim = _CONTEXTS[_Threads.ThreadsMeta.currentThread.ident]["stringDelimiter"]
		else:
			delim = DEFAULT_CONTEXT["stringDelimiter"]
		return f"{delim}{str(string).replace(delim, BACKSLASH+delim)}{delim}"
	
	@classmethod
	def format(cls, value):
		match value:
			case False:
				return "\"false\""
			case True:
				return "\"true\""
			case None:
				return "\"none\""
			case _:
				return SyntaxContext.repString(str(value))

import GeekyGadgets.Semantics.Rulesets.CSS as _CSS