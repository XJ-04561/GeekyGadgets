
from GeekyGadgets.Colors.Globals import *
from GeekyGadgets.Classy import Default

__all__ = ("Theme", "AnsiTheme")

class Theme:
	
	colorType : ColorType

	primary : ColorType
	secondary : ColorType = Default(lambda self:self.primary)
	tertiary : ColorType = Default(lambda self:self.secondary)
	quarternary : ColorType = Default(lambda self:self.tertiary)

	good : ColorType
	warning : ColorType
	bad : ColorType

	pre : ColorType
	progress : ColorType = Default(lambda self:self.energy)
	post : ColorType

	energy : ColorType = Default(lambda self:self.progress)

	@overload
	def __init__(self, name : str, *, primary : ColorType, secondary : ColorType, tertiary : ColorType, quarternary : ColorType, good : ColorType, warning : ColorType, bad : ColorType, pre : ColorType, progress : ColorType, post : ColorType, energy : ColorType): ...
	def __init__(self, name : str, **kwargs):
		for name, value in kwargs.items():
			if value is not None:
				setattr(self, name, value)

class AnsiTheme(Theme): pass