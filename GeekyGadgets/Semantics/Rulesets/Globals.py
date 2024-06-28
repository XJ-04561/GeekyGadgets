
from GeekyGadgets.Semantics.Globals import *

class Ruleset(SemanticsNameSpace):
	
	newline : str = "\n"
	sep : str = ";"
	spacing : str = " "
	pairSep : str = ":"
	listSep : str = " "
	delimiters : tuple[str,str] = ("{", "}")
	indentation : str = "\t"

	def __str__(self):
		cls = GETATTR(self, "__class__")
		if SyntaxContext.compact:
			return f"{cls.delimiters[0]}{cls.sep.join(map(lambda x: f'{SnakeCase(x[0])}{cls.pairSep}{cls.listSep.join(map(str, x[1])) if isinstance(x[1], (list,tuple)) else x[1]}', dict.items(self)))}{cls.delimiters[1]}"
		else:
			return f"{cls.delimiters[0]}{cls.newline}{cls.indentation}{f'{cls.sep}{cls.newline}{cls.indentation}'.join(map(lambda x: f'{SnakeCase(x[0])}{cls.spacing}{cls.pairSep}{cls.spacing}{cls.listSep.join(map(str, x[1])) if isinstance(x[1], (list,tuple)) else x[1]}', dict.items(self)))}{cls.newline}{cls.delimiters[1]}"

	def __format__(self, fs):
		cls = GETATTR(self, "__class__")
		return f"{cls.delimiters[0]}{cls.sep.join(map(lambda x: f'{SnakeCase(x[0])}{cls.pairSep}{cls.listSep.join(map(str, x[1])) if isinstance(x[1], (list,tuple)) else x[1]}', dict.items(self)))}{cls.delimiters[1]}"