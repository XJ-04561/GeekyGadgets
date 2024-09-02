
import GeekyGadgets.Semantics.Markdown.Globals as _GL
import GeekyGadgets.Classy as _Classy
import GeekyGadgets.Iterators as _Itertools
import GeekyGadgets.Semantics.Markdown.Text as _Text
import GeekyGadgets.Semantics.Markdown.Parsing as _Parsing

class TextBlock(_GL.Block):
	
	PRIORITY : int = 0
	PATTERN : _GL.re.Pattern = _GL.re.compile(r".*?$$")
	ENTRY_PATTERN : _GL.re.Pattern = _GL.re.compile(r"(.*?)$$")
	DELIMITER : str
	ALTERNATE_DELIMITERS : tuple[str] = ()
	
	def __str__(self):
		return f"{self.DELIMITER} {self.content}\n"
	
	@classmethod
	def parse(cls: "TextBlock", string: str, markdown : _Parsing.MarkdownVersion=_Parsing.GeekyMarkdown):
		return cls(_Parsing.parseInline(string))

class Heading(TextBlock, _GL.ABC):
	PRIORITY : int = 5
	PATTERN : _GL.re.Pattern = _GL.re.compile(r"^#{1,6} (.*?)$")
	DELIMITER = "#"

class Heading1(Heading):
	PATTERN = _GL.re.compile(r"^# (.*?)$")
	DELIMITER = "#"
class Heading2(Heading):
	PATTERN = _GL.re.compile(r"^## (.*?)$")
	DELIMITER = "##"
class Heading3(Heading):
	PATTERN = _GL.re.compile(r"^### (.*?)$")
	DELIMITER = "###"
class Heading4(Heading):
	PATTERN = _GL.re.compile(r"^#### (.*?)$")
	DELIMITER = "####"
class Heading5(Heading):
	PATTERN = _GL.re.compile(r"^##### (.*?)$")
	DELIMITER = "#####"
class Heading6(Heading):
	PATTERN = _GL.re.compile(r"^###### (.*?)$")
	DELIMITER = "######"
	
class QuoteBlock(TextBlock):
	PRIORITY : int = 6
	PATTERN = _GL.re.compile(r"^(?P<level>>+) .*?$((?P=level)>* .*?$)*")
	DELIMITER = ">"
	ALTERNATE_DELIMITERS = ()

class ItemList(TextBlock):
	PRIORITY : int = 4
	PATTERN = _GL.re.compile(r"^(?P<level>\s*)[*-+] .*?$((?P=level)\s*[*-+] .*?$|(?P=level)\s+ .*?$)*")
	DELIMITER = ">"
	ALTERNATE_DELIMITERS = ()

class CodeBlock(TextBlock):
	PRIORITY : int = 7
	DELIMITER = "```"

	syntaxHint : str|None

	def __init__(self, content: str, syntaxHint : str|None=None) -> None:
		super().__init__(content)
		self.syntaxHint = syntaxHint

	def __str__(self):
		return f"{self.DELIMITER}{self.syntaxHint or ''}\n{self.content}{self.DELIMITER}"

class Image(_GL.Block, _Text.HyperLink):
	PATTERN : _GL.re.Pattern = _GL.re.compile(r"!([[].*?[]])?[(][^\n]*?[)]")
	DELIMITER = "("

class Table(_GL.Block):
	
	leftDelimiter : str = "| "
	rightDelimiter : str = " |"
	innerDelimiter : str = " | "

	head : list[str|_GL.Any] = _Classy.Default(lambda self: [*_Itertools.AlphaRange(len(self.cells[0]))] if self.cells else [])
	headerSeparator = property(lambda self: [f"{':' if pos in ('left', 'center') else '-'}---{':' if pos in ('center', 'right') else '-'}" for pos in self.columnAlign])
	columnAlign : list[str|_GL.Any] = _Classy.Default(lambda self: ["center" for _ in self.head])
	cells : list[list[str|_GL.Any]]

	content : list[list[str|_GL.Any]] = property(lambda self: [self.head, self.headerSeparator, *self.cells])
	
	columns = property(lambda self: len(self.head))
	rows = property(lambda self: len(self.cells))
	
	def __init__(self, cells, *, head : _GL.Iterable[str]=None, columnAlign : str|_GL.Iterable[str]|None=None) -> None:
		
		self.cells = list(map(list, cells))
		if head is not None:
			self.head = list(head)
		if columnAlign is not None:
			if isinstance(columnAlign, str):
				self.columnAlign = [columnAlign.lower() for _ in range(self.columns)]
			else:
				self.columnAlign = list(map(str.lower, columnAlign))

	def __str__(self):
		return "\n".join(f"{self.leftDelimiter}{self.innerDelimiter.join(map(str,row))}{self.rightDelimiter}" for row in self.content)