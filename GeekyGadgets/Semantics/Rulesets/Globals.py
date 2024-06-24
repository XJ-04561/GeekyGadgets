
from GeekyGadgets.Semantics.Globals import *

class Ruleset(SemanticsNameSpace):
	
	newline : str = "\n"
	sep : str = ";"
	spacing : str = " "
	pairSep : str = ":"
	listSep : str = " "
	delimiters : tuple[str,str] = ("{", "}")
	indentation : str = "\t"