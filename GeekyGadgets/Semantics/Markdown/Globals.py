
from GeekyGadgets.Semantics.Globals import *
import GeekyGadgets.Classy as _Classy
import GeekyGadgets.Functions as _Funcs
import GeekyGadgets.Iterators.Itertools as _Itertools
import GeekyGadgets.Formatting.Functions as _Formatting
import GeekyGadgets.Semantics.Markups.HTML as _HTML

class Markdown(Semantics):

	PRIORITY : int
	PATTERN : re.Pattern
	HTML : _HTML.HTML = _HTML.Div

	content : "tuple[str|Markdown]"

	def __init__(self, *content : "str|Markdown") -> None:
		self.content = content

	def append(self, item):
		self.content = (*self.content, item)

	def compile(self):
		return str(self)
	
	@abstractmethod
	@classmethod
	def parse(cls : "type[Markdown]", string : str, markdown): ...

import GeekyGadgets.Semantics.Markdown.Parsing as _Parsing

class Block(Markdown):
	
	ENTRY_PATTERN : re.Pattern

	def __init__(self, content) -> None:
		self.content = content
	
	@classmethod
	def parse(cls: "Block", string: str, markdown : _Parsing.MarkdownVersion=_Parsing.GeekyMarkdown):
		return cls(_Parsing.parse(string, markdown=markdown))

class Inline(Markdown):
	
	PRIORITY : int = 1
	HTML : _HTML.HTML = _HTML.Span