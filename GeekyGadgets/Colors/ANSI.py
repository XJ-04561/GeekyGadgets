
from GeekyGadgets.Colors.Globals import *
import colors

__all__ = ("COLOR_STRINGS", "supportsColor", "AnsiStr", "YellowText", "MagentaText", "WhiteText", "RedText",
		   "GreenText", "CyanText", "DefaultTheme", "AnsiTheme")

class COLOR_STRINGS:
	yellow : str	= "yellow"
	magenta : str	= "magenta"
	white : str		= "white"
	red : str		= "red"
	green : str		= "green"
	cyan : str		= "cyan"

# Taken from django @ https://github.com/django/django/blob/main/django/core/management/color.py
@cache
def supportsColor(out=sys.stdout):
	"""
	From django @ https://github.com/django/django/blob/main/django/core/management/color.py
	Return True if the running system's terminal supports color,
	and False otherwise.
	"""
	try:
		import colorama # type: ignore

		# Avoid initializing colorama in non-Windows platforms.
		colorama.just_fix_windows_console()
	except (
		AttributeError,  # colorama <= 0.4.6.
		ImportError,  # colorama is not installed.
		# If just_fix_windows_console() accesses sys.stdout with
		# WSGIRestrictedStdout.
		OSError,
	):
		HAS_COLORAMA = False
	else:
		HAS_COLORAMA = True

	def vt_codes_enabled_in_windows_registry():
		"""
		Check the Windows Registry to see if VT code handling has been enabled
		by default, see https://superuser.com/a/1300251/447564.
		"""
		try:
			# winreg is only available on Windows.
			import winreg
		except ImportError:
			return False
		else:
			try:
				reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Console")
				reg_key_value, _ = winreg.QueryValueEx(reg_key, "VirtualTerminalLevel")
			except FileNotFoundError:
				return False
			else:
				return reg_key_value == 1

	# isatty is not always implemented, #6223.
	is_a_tty = hasattr(out, "isatty") and out.isatty()

	return is_a_tty and (
		sys.platform != "win32"
		or (HAS_COLORAMA and getattr(colorama, "fixed_windows_console", False))
		or "ANSICON" in os.environ
		or
		# Windows Terminal supports VT codes.
		"WT_SESSION" in os.environ
		or
		# Microsoft Visual Studio Code's built-in terminal supports colors.
		os.environ.get("TERM_PROGRAM") == "vscode"
		or vt_codes_enabled_in_windows_registry()
	)

if supportsColor():
	class AnsiStr(str, ColorObject):
		"""Use either by giving the ansi parameters at object construction or set the construction parameters as 
		attributes in a subclass, to simplify instantiation of strings with similar or same ANSI formatting.
		
		#### Parameters/attributes:
			`color      : str` - Text color
			`background : str` - Background color
			`fontStyles : str` - Font styling, like italicized or bold

		### Example
		```python
		redText = AnsiStr("Hello there!", color="red")
		```
		or
		```python
		class RedText(AnsiStr):
			color="red"
		
		redText1 = RedText("Hello there!")
		redText2 = RedText("Hello again!")
		```"""
		
		color : str = None
		background : str = None
		fontStyles : str = None

		@overload
		def __new__(cls, text : str): ...
		@overload
		def __new__(cls, text : str, *, color : str, background : str, fontStyles : str): ...
		def __new__(cls, text : str, *, color : str=None, background : str=None, fontStyles : str=None):
			return super().__new__(cls, colors.color(text, color or getattr(cls, "color", None), background or getattr(cls, "background", None), fontStyles or getattr(cls, "fontStyles", None)))

		def __format__(self, fs : str):
			if match := FORMAT_PATTERN.fullmatch(fs):
				filler = match.groupdict("filler") or " "
				direction = match.groupdict("direction") or "<"
				size = int(match.groupdict("size") or 0)
			else:
				return super().__format__(fs)
			
			match direction:
				case "<":
					return self + filler * max(size - len(self.raw), 0)
				case "^":
					l = len(self.raw)
					return filler*(max(size - l, 0) // 2)+self+filler*(max(size - l, 0) // 2 + max(size - l, 0) % 2)
				case ">":
					return filler * max(size - len(self.raw), 0) + self
				case _:
					return super().__format__(fs)
		
		def __add__(self, right):
			return type(self)(str.__add__(self, right))
		def __radd__(self, left):
			return type(self)(str.__add__(left, self))
		
		@cached_property
		def raw(self):
			return ANSI_MATCH.sub("", self)
else:
	class AnsiStr(str, ColorObject):
		"""# THE PYTHON ENVIRONMENT THAT IS RUNNING DOES NOT SUPPORT ANSI CODES, AND THIS CLASS IS THEREFORE JUST A 
		str & ColorObject SUBCLASS WITH METHODS FROM THE REAL AnsiStr DEFINED FOR CODE COMPATABILITY
		# THE FOLLOWING DOCSTRING IS RELEVANT TO THE AnsiStr THAT WOULD BE DEFINED IF IT HAD BEEN SUPPORTED
		
		Use either by giving the ansi parameters at object construction or set the construction parameters as 
		attributes in a subclass, to simplify instantiation of strings with similar or same ANSI formatting.
		
		#### Parameters/attributes:
			`color      : str` - Text color
			`background : str` - Background color
			`fontStyles : str` - Font styling, like italicized or bold

		### Example
		```python
		redText = AnsiStr("Hello there!", color="red")
		```
		or
		```python
		class RedText(AnsiStr):
			color="red"
		
		redText1 = RedText("Hello there!")
		redText2 = RedText("Hello again!")
		```"""
		
		color : str = None
		background : str = None
		fontStyles : str = None

		raw = property(lambda self:self)

		def __add__(self, right):
			return type(self)(str.__add__(self, right))
		def __radd__(self, left):
			return type(self)(str.__add__(left, self))

class YellowText(AnsiStr):
	color = "Yellow"
class MagentaText(AnsiStr):
	color = "Magenta"
class WhiteText(AnsiStr):
	color = "White"
class RedText(AnsiStr):
	color = "Red"
class GreenText(AnsiStr):
	color = "Green"
class CyanText(AnsiStr):
	color = "Cyan"

from GeekyGadgets.Colors.Themes import AnsiTheme

DefaultTheme = AnsiTheme("DefaultTheme", primary=AnsiStr, good=GreenText, warning=YellowText, bad=RedText, pre=YellowText, post=MagentaText)