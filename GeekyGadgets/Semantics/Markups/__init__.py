
from GeekyGadgets.Semantics.Markups.Globals import Markup, RuntimeCreatedMarkup as _RuntimeCreatedMarkup
from GeekyGadgets.Semantics.Markups.Globals import Attributes as MarkupAttributes

MARKUP_TYPES : list[type[Markup]] = [*Markup.__subclasses__(), _RuntimeCreatedMarkup]