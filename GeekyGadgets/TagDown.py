
from GeekyGadgets.Globals import *
from GeekyGadgets.SpecialTypes import NameSpace
from GeekyGadgets.Formatting.Case import KebabCase

class Tag:
	
	content : list["Tag"]
	attributes : dict[str,Any]

	def __init__(self, name : str, *content : "str|Tag", **attributes) -> None:
		self.name = name
		self.content = list(content)
		self.attributes = NameSpace({KebabCase(name):value for name, value in attributes.items()})

	def __iter__(self):
		for element in self.content:
			yield element

	def __str__(self):
		return f"<{self.name} {self.attributes}>{''.join(map(str, self))}</{self.name}>"