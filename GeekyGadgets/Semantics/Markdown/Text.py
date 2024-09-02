
import GeekyGadgets.Semantics.Markdown.Globals as _GL
import GeekyGadgets.Classy as _Classy
import GeekyGadgets.Formatting.Functions as _Formatting

class FormattedText(_GL.Inline, _GL.ABC):
	
	PRIORITY : int = 1
	PATTERN : _GL.re.Pattern
	DELIMITER : str
	ALTERNATE_DELIMITERS : tuple[str] = ()
	
	def __str__(self):
		return f"{self.DELIMITER}{''.join(self.content)}{_Formatting.flipString(self.DELIMITER)}"
	
	def __format__(self, fs : str):
		for dl in self.ALTERNATE_DELIMITERS:
			if fs.endswith(dl):
				return format(f"{dl}{''.join(self.content)}{_Formatting.flipString(dl)}", fs.removesuffix(dl))
		return format(f"{self.DELIMITER}{''.join(self.content)}{self.DELIMITER}", fs)

class Italic(FormattedText):
	PRIORITY : int = 1
	PATTERN : _GL.re.Pattern = _GL.re.compile(r"(?<![*])[*]|(?<!_)_")
	DELIMITER = "*"
	PRIORITY : int = 2
	ALTERNATE_DELIMITER = ("_",)
	HTML : _GL._HTML.HTML = _GL._HTML.Em
	
class Bold(FormattedText):
	PRIORITY : int = 2
	PATTERN : _GL.re.Pattern = _GL.re.compile(r"[*][*]|__")
	DELIMITER = "**"
	ALTERNATE_DELIMITERS = ("__",)
	HTML : _GL._HTML.HTML = _GL._HTML.Strong

class Strikethrough(FormattedText):
	PRIORITY : int = 1
	PATTERN : _GL.re.Pattern = _GL.re.compile(r"[~][~]")
	DELIMITER = "~~"
	HTML : _GL._HTML.HTML = _GL._HTML.Del

class Monospace(FormattedText):
	PRIORITY : int = 10
	PATTERN : _GL.re.Pattern = _GL.re.compile(r"[`]")
	DELIMITER = "`"
	HTML : _GL._HTML.HTML = _GL._HTML.Code

class Spoiler(FormattedText):
	PRIORITY : int = 1
	PATTERN : _GL.re.Pattern = _GL.re.compile(r"(<!\)[|]")
	DELIMITER = "|"
	HTML : _GL._HTML.HTML = _GL._HTML.Magic.Spoiler

class LineBreak(FormattedText):
	PRIORITY : int = 1
	PATTERN : _GL.re.Pattern = _GL.re.compile(r"  $(?=\S)")
	DELIMITER = "\n"
	HTML : _GL._HTML.HTML = _GL._HTML.Br

class HyperLink(FormattedText):
	PRIORITY : int = 1
	PATTERN : _GL.re.Pattern = _GL.re.compile(r"([[].*?[]])[(][^\n]*?[)]")
	DELIMITER = "("
	HTML : _GL._HTML.HTML = _GL._HTML.A