
from GeekyGadgets.Semantics.Globals import Attributes
from GeekyGadgets.Semantics.Markups.Globals import Markup
import GeekyGadgets.Semantics.Markups.HTML as _HTML

class Spoiler(_HTML.HTML):
	
	def __init__(self: _HTML._Globals._TAG, *content: _HTML._Globals.AnyStr | Markup, ATTRS: dict | Attributes = ..., **attributes: _HTML._Globals.AnyStr | int | float | bool) -> None:
		self.onclick = "this.style.background = 'transparent'; this.ariaHidden = 'false';"
		self.ariaHidden = "true"
		self.style.display = "inline"
		self.style.background = "currentcolor"
		self.userSelect = "none"
		super().__init__(*content, ATTRS=ATTRS, **attributes)
	