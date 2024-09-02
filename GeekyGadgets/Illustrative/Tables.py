
from GeekyGadgets.Illustrative.Globals import *

import GeekyGadgets.Iterators as _Iterators
import GeekyGadgets.Classy as _Classy
import GeekyGadgets.SpecialTypes as _SPT
import GeekyGadgets.Semantics.Markdown as _Markdown
import GeekyGadgets.Semantics.Markups as _Markups
import GeekyGadgets.Semantics.Markups.HTML as _HTML

__all__ = ("Table", )

class Table(Illustrator):
	
	HTML : _SPT.NameSpace = _SPT.NameSpace(
		CSS=open(os.path.join(os.path.split(__file__)[0], "CSS", "Table.css"), "r").read()
	)

	columns : tuple[str] = _Classy.Default(lambda self: list(_Iterators.AlphaRange(len(self.data[0]))))
	data : list[list[Any]]

	@overload
	def __init__(self, data : Iterable, *, columns : str, title : str="Table", description : str|None=None) -> None: ...
	def __init__(self, data : Iterable, **kwargs) -> None:
		
		self.data = [[col for col in row] for row in data]
		if not all(len(row) == len(data[0]) for row in data):
			raise ValueError(f"Data must be contiguous. Rowlengths were {list(map(len, data))}")
		if "columns" in kwargs:
			self.columns = list(kwargs["columns"])
		self.title = kwargs.get("title", "Table")
		self.description = kwargs.get("description")

	def add(self, row : Iterable, /):
		row = list(row)
		if len(row) != len(self.data[0]):
			raise ValueError(f"Data must be contiguous. Tried adding row of length {len(row)} to table with {len(self.data[0])} columns.")
		self.data.append(row)
	
	def illustrateHTML(self, *, file : TextIO|None=None, **kwargs) -> _Markups.Markup:


		page = _HTML.Figure(Class="IllustrativeTable")

		if self.title:
			page.addChild(_HTML.H2(self.title))
		if self.description:
			page.addChild(_HTML.P(self.description))
		if self.title or self.description:
			page.addChild(_HTML.Hr())
		
		page.addChild(
			_HTML.Table(
				_HTML.Thead(
					_HTML.Tr(*(
						_HTML.Th(name, style="visibility : none;")
						if isinstance(self.data[0][i], Illustrator)
						else _HTML.Th(name)
						for i, name in enumerate(self.columns)
					))
				),
				_HTML.Tbody(
					*(
						_HTML.Tr(*(_HTML.Td(value.illustrateHTML() if isinstance(value, Illustrator) else value) for value in row))
						for row in self.data
					)
				),
				Class="GeekyIllustration"
		))
		
		if file is not None:
			file.write(page.compile())
			file.flush()
		return page
	
	def illustrateMARKDOWN(self, *, file : TextIO|None=None, **kwargs) -> _Markdown.Markdown:
		from GeekyGadgets.Semantics.Markdown import Table

		page = Table(self.data, head=self.columns)

		if file is not None:
			if isinstance(file, BinaryIO):
				file.write(page.compile().encode(file.encoding))
			else:
				file.write(page.compile())
		
		return page
