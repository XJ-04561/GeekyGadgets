
from GeekyGadgets.Globals import *
from GeekyGadgets.SpecialTypes import NameSpace
from GeekyGadgets.Formatting.Case import KebabCase

class CSS(NameSpace):
	def __repr__(self):
		return repr("; ".join(map("{0[0]} : {0[1]}".format, self)))

class Tag:
	
	content : list["Tag"]
	attributes : dict[str,Any]

	def __init__(self, name : str, *content : "str|Tag", **attributes) -> None:
		self.name = name
		self.content = list(content)
		self.attributes = NameSpace({KebabCase(name):value if name != "style" else CSS(value) for name, value in attributes.items()})

	def __iter__(self):
		for element in self.content:
			yield element

	def __str__(self):
		return f"<{self.name} {self.attributes}>{''.join(map(str, self))}</{self.name}>"
	
	def __repr__(self):
		return repr(str(self))
	
	def __hash__(self):
		return hash(str(self))
	
	def __eq__(self, other : Hashable):
		return hasattr(other, "__hash__") and hash(self) == hash(other)