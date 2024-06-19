
from GeekyGadgets.Globals import *
from GeekyGadgets.TagDown import Tag

class ColoredHTML(Tag):
	
	@overload
	def __init__(self, content: str | Tag, *, color : str, background : str, fontStyle : str, **attributes) -> None: ...
	def __init__(self, content: str | Tag, **attributes) -> None:
		super().__init__("span", *content, **attributes)

class TextColor(ColoredHTML):
	
	color : str

	@overload
	def __init__(self, content: str | Tag, *, background : str, fontStyle : str, **attributes) -> None: ...
	def __init__(self, content: str | Tag, **attributes) -> None:
		super().__init__(*content, color=self.color, **attributes)

class BackgroundColor(ColoredHTML):
	
	background : str

	@overload
	def __init__(self, content: str | Tag, *, color : str, fontStyle : str, **attributes) -> None: ...
	def __init__(self, content: str | Tag, **attributes) -> None:
		super().__init__(*content, background=self.background, **attributes)

class FontStyle(ColoredHTML):
	
	fontStyle : str

	@overload
	def __init__(self, content: str | Tag, *, color : str, background : str, **attributes) -> None: ...
	def __init__(self, content: str | Tag, **attributes) -> None:
		super().__init__(*content, fontStyle=self.fontStyle, **attributes)

class RedText(TextColor):		color="Red"
class GreenText(TextColor):	color="Green"
class BlueText(TextColor):	color="Blue"
class CyanText(TextColor):	color="Cyan"
class MagentaText(TextColor):	color="Magenta"
class WhiteText(TextColor):	color="White"
class BlackText(TextColor):	color="Black"
class GrayText(TextColor):	color="Gray"
class OrangeText(TextColor):	color="Orange"
class BrownText(TextColor):	color="Brown"
class DarkGrayText(TextColor):color="DarkGray"

class RedBackground(BackgroundColor):		background="Red"
class GreenBackground(BackgroundColor):	background="Green"
class BlueBackground(BackgroundColor):	background="Blue"
class CyanBackground(BackgroundColor):	background="Cyan"
class MagentaBackground(BackgroundColor):	background="Magenta"
class WhiteBackground(BackgroundColor):	background="White"
class BlackBackground(BackgroundColor):	background="Black"
class GrayBackground(BackgroundColor):	background="Gray"
class OrangeBackground(BackgroundColor):	background="Orange"
class BrownBackground(BackgroundColor):	background="Brown"
class DarkGrayBackground(BackgroundColor):background="DarkGray"
