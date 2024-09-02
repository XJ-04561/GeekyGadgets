
from GeekyGadgets.Colors.Globals import *

import GeekyGadgets.Iterators as _Iterators
import GeekyGadgets.Math.Stats.Functions as _StatFuncs

__all__ = ("Color", "HSV", "RGB", "ColorScale")

_T = TypeVar("_T")

class Color(Subscriptable, ABC):
	
	factors : tuple[float,float,float]
	constants : tuple[float,float,float]
	decimals : tuple[int,int,int] = [None,None,None]
	units : tuple[str,str,str] = ["","",""]

	__name__ = property(lambda self: self.__class__.__name__)
	
	def __init__(self, *args : tuple[Number, Number, Number]|Number) -> None:
		if len(args) == 1:
			self.factors = args[0]
		else:
			self.factors = tuple(f/c for c, f in zip(self.constants, args))

	def __getitem__(self, key):
		return self.factors[key]

	def __setitem__(self, key, value):
		self.factors = tuple(f if key!=i else value for i, f in enumerate(self.factors))

	def __repr__(self):
		return f"<{self.__name__} object '{str(self)}' at {id(self):#x}>"

	def __str__(self):
		return f"{self.__class__.__name__}({', '.join(str(round(a*f, d))+u for a,f,d,u in zip(self.constants, self.factors, self.decimals, self.units))})"

	def __mul__(self, other : "Color|Number"):
		other = getattr(other, self.__name__.lower())() if isinstance(other, Color) else [other]*3
		return type(self)(tuple(v1*v2 for v1,v2 in zip(self,other)))
	def __rmul__(self, other : "Color|Number"):
		return self * other
	def __truediv__(self, other : "Color|Number"):
		other = getattr(other, self.__name__.lower())() if isinstance(other, Color) else [other]*3
		return type(self)(tuple(v1/v2 for v1,v2 in zip(self,other)))
	def __rtruediv__(self, other : "Color|Number"):
		other = getattr(other, self.__name__.lower())() if isinstance(other, Color) else [other]*3
		return type(self)(tuple(v1/v2 for v1,v2 in zip(other,self)))
	def __add__(self, other : "Color|Number"):
		other = getattr(other, self.__name__.lower())() if isinstance(other, Color) else [other]*3
		return type(self)(tuple(v1+v2 for v1,v2 in zip(self,other)))
	def __radd__(self, other : "Color|Number"):
		return self + other
	def __sub__(self, other : "Color|Number"):
		other = getattr(other, self.__name__.lower())() if isinstance(other, Color) else [other]*3
		return type(self)(tuple(v1-v2 for v1,v2 in zip(self,other)))
	def __rsub__(self, other : "Color|Number"):
		other = getattr(other, self.__name__.lower())() if isinstance(other, Color) else [other]*3
		return type(self)(tuple(v1-v2 for v1,v2 in zip(other,self)))
	def __abs__(self) -> float:
		return _StatFuncs.sqrt(sum(f**2 for f in self.factors))

	@abstractmethod
	def hex(self) -> str: ...
	@abstractmethod
	def rgb(self) -> "RGB": ...
	@abstractmethod
	def hsl(self) -> "HSL": ...
	@abstractmethod
	def hsv(self) -> "HSV": ...
	@overload
	def to(self : "_COLOR", format : Literal["hex"]) -> str: ...
	@overload
	def to(self : "_COLOR", format : Literal["rgb"]) -> "RGB": ...
	@overload
	def to(self : "_COLOR", format : Literal["hsl"]) -> "HSL": ...
	@overload
	def to(self : "_COLOR", format : Literal["hsv"]) -> "HSV": ...
	@overload
	def to(self : "_C1", format : "type[_C2]") -> "_C2": ...
	@overload
	def to(self : "_C1", format : "_C2") -> "_C2": ...
	def to(self : "_COLOR", format : 'Literal["hex","rgb","hsl","hsv"]|type[_C2]|_C2') -> "str|RGB|HSV|HSL|_C2":
		if format == "hex":
			return self.hex()
		elif format == "rgb":
			return self.rgb()
		elif format == "hsl":
			return self.hsl()
		elif format == "hsv":
			return self.hsv()
		elif issubclass(format.__class__, Color):
			return self.to(format.__class__.__name__.lower())
		elif isinstance(format, Color.__class__) and issubclass(format, Color):
			return self.to(format.__name__.lower())
		else:
			raise ValueError(f"Not a recognized color format {format}")
	
	def blend(self : "_COLOR", *colors : "Color|tuple[int,int,int]", weights : tuple[float]=None) -> "_COLOR":
		weights = weights or [1.0]*(len(colors)+1)
		
		if type(self) is HSV:
			return (weights[0]*self.hsv() + sum(c.hsv()*w for c, w in zip(colors, weights[1:]))) / sum(weights)
		else:
			return HSV.to((weights[0]*self.hsv() + sum(c.hsv()*w for c, w in zip(colors, weights[1:]))) / sum(weights), self.__name__.lower())
	
	def invert(self : "_COLOR", channel : int=0) -> "_COLOR":
		if channel == 0:
			return type(self)(tuple(1-f for f in self.factors))
		else:
			return type(self)(tuple(1-f if i == channel-1 else f for i, f in enumerate(self.factors)))
	
	def transition(self : "_COLOR", new : "Color", frames : int) -> "list[_COLOR]":
		return [self.blend(new, (w, 1-w)) for w in _Iterators.Spaced(0, 1.0, frames)]
	
	def amplify(self : "_COLOR", factor : Interval[0,1], channel : int, func : Callable[[float],float]=lambda x:x) -> "_COLOR":
		color = self.__class__(self.factors)
		color[channel-1] = 1 - color.factors[channel-1]
		color = color.amplify(factor, channel, func=func)
		color[channel-1] = 1 - color.factors[channel-1]
		return color
	
	def dampen(self : "_COLOR", factor : Interval[0,1], channel : int, func : Callable[[float],float]=lambda x:x) -> "_COLOR":
		color = self.__class__(self.factors)
		if factor == 0:
			return color
		elif factor == 1:
			color[channel-1] = 0
			return color
		elif color.factors[channel-1] == 0:
			return color
		else:
			a, b = 0, 1
			v0, v = color.factors[channel-1], color.factors[channel-1]
			fv0 = func(v0) * (1-factor)
			for i in range(5):
				fv = func(v)
				if fv < fv0:
					a, v = v, (b+a)/2
				elif fv > fv0:
					b, v = v, (b+a)/2
				else:
					break
			color[channel-1] = v
			return color

	def darken(self : "_COLOR", factor : Interval[0,1], func : Callable[[float],float]=lambda x:x) -> "_COLOR":
		return self.hsv().dampen(factor=factor, func=func, channel=3).to(self.__class__.__name__.lower())
	
	def brighten(self : "_COLOR", factor : Interval[0,1], func : Callable[[float],float]=lambda x:x) -> "_COLOR":
		return self.hsv().amplify(factor=factor, func=func, channel=3).to(self.__class__.__name__.lower())
	
	def saturate(self : "_COLOR", factor : Interval[0,1], func : Callable[[float],float]=lambda x:x) -> "_COLOR":
		return self.hsv().amplify(factor=factor, func=func, channel=2).to(self.__class__.__name__.lower())

	def fade(self : "_COLOR", factor : Interval[0,1], func : Callable[[float],float]=lambda x:x) -> "_COLOR":
		return self.hsv().dampen(factor=factor, func=func, channel=2).to(self.__class__.__name__.lower())
	
	def hueShift(self : "_COLOR", value : Interval[0,1]) -> "_COLOR":
		color = self.hsv()
		return self.__class__((color.factors[0]+value, color.factors[1], color.factors[2]))
	
	def bleach(self : "_COLOR", factor : Interval[0,1], func : Callable[[float],float]=lambda x:x) -> "_COLOR":
		return self.hsl().amplify(factor=factor, func=func, channel=3).to(self.__class__.__name__.lower())

_COLOR = TypeVar("_COLOR", bound=Color)
_C1 = TypeVar("_C1", bound=Color)
_C2 = TypeVar("_C2", bound=Color)

class HSV(Color):
	
	hue = property(lambda self:self[0])
	saturation = property(lambda self:self[1])
	value = property(lambda self:self[2])

	constants = (360, 100, 100)
	units = ("deg", "%", "%")

	@overload
	def __init__(self, hue : float, saturation : float, value : float): ...
	@overload
	def __init__(self, factors : tuple[float,float,float]): ...
	def __init__(self, *args : tuple[Number, Number, Number]|Number) -> None:
		return super().__init__(*args)
		
	def rgb(self) -> "RGB[int, int, int]":
		return RGB(tuple(
			(1 + (f - 1)*self.saturation)*self.value
			# (f + (1-self.saturation) * (1 - f))*self.value
			for f in (
				_StatFuncs.limit(0, _StatFuncs.triangle(self.hue+offset)*3-1, 1)
				for offset in [0, -1/3, -2/3]
			)
		))
	def hex(self) -> str:
		return self.rgb().hex()
	def hsv(self) -> "HSV[float,float,float]":
		return HSV(self.factors)
	def hsl(self):
		return HSL(
			(
				self.hue,
				(self.value-(lightness := self.value * (2 - self.saturation) / 2)) / lightness
					if 0 < lightness <= 0.5
					else (self.value-lightness) / (1-lightness)
						if 0.5 < lightness < 0
						else 0,
				lightness
			)
		)
	
	def invert(self : "_COLOR", channel : int=0) -> "_COLOR":
		if channel == 0:
			return type(self)((self[0]+0.5 % 1, 1-self[1], 1-self[2]))
		elif channel == 1:
			return type(self)((self[0]+0.5 % 1, self[1], self[2]))
		else:
			return type(self)(tuple(1-f if i == channel-1 else f for i, f in enumerate(self.factors)))

class HSL(Color):
	
	hue = property(lambda self:self[0])
	saturation = property(lambda self:self[1])
	lightness = property(lambda self:self[2])

	constants = (360, 100, 100)
	units = ("deg", "%", "%")

	@overload
	def __init__(self, hue : float, saturation : float, lightness : float): ...
	@overload
	def __init__(self, factors : tuple[float,float,float]): ...
	def __init__(self, *args : tuple[Number, Number, Number]|Number) -> None:
		return super().__init__(*args)
		
	def rgb(self) -> "RGB[int, int, int]":
		high, low = min(1, self.lightness*2), max(0, self.lightness*2-1)
		return RGB(tuple(
			_StatFuncs.limit(0, self.saturation*(f - 0.5)*(high - low)+ (high + low)/2, 1)
			for f in (
				_StatFuncs.limit(0, _StatFuncs.triangle(self.hue+offset)*3-1, 1)
				for offset in [0, -1/3, -2/3]
			)
		))
	def hex(self) -> str:
		return self.rgb().hex()
	def hsv(self) -> "HSV[float,float,float]":
		value = self.lightness + self.saturation * (
			self.lightness
			if self.lightness <= 0.5
			else 1 - self.lightness
		)
		return HSV(
			(
				self.hue,
				2*(1 - self.lightness/value)
					if value != 0
					else 0,
				value
			)
		)
	def hsl(self):
		return HSL(self.factors)
	
	def invert(self : "_COLOR", channel : int=0) -> "_COLOR":
		if channel == 0:
			return type(self)((self[0]+0.5 % 1, 1-self[1], 1-self[2]))
		elif channel == 1:
			return type(self)((self[0]+0.5 % 1, self[1], self[2]))
		else:
			return type(self)(tuple(1-f if i == channel-1 else f for i, f in enumerate(self.factors)))

class RGB(Color):
	red = property(lambda self:self[0])
	green = property(lambda self:self[1])
	blue = property(lambda self:self[2])
	constants = (255, 255, 255)
	@overload
	def __init__(self, red : int|float, green : int|float, blue : int|float): ...
	@overload
	def __init__(self, factors : tuple[float,float,float]): ...
	def __init__(self, *args : tuple[Number, Number, Number]|Number) -> None:
		return super().__init__(*args)
	
	def rgb(self) -> "RGB[int, int, int]":
		return self
	def hex(self) -> str:
		return f"#{''.join(format(round(255*v), '0>2x') for v in self)}"
	def hsv(self) -> "HSV[float, float, float]":
		
		(a2i, a2), (b2i, b2), (c2i, c2) = sorted(enumerate(self.factors), reverse=True, key=lambda x:x[1])
		if a2 == 0:
			return HSV((0, 0, 0))
		elif a2 == b2 == c2:
			return HSV((0, 0, a2))
		elif b2 == c2:
			return HSV((a2i/3, (a2-c2) / a2, a2))
		else:
			return HSV((
				a2i / 3 + ((-1)**((b2i-0.5)%3 < a2i)) * (b2-c2)/(a2-c2) / 6,
				(a2-c2) / a2,
				a2
			))
	def hsl(self):
		
		(a2i, a2), (b2i, b2), (c2i, c2) = sorted(enumerate(self.factors), reverse=True, key=lambda x:x[1])
		if a2 == b2 == c2 == 0:
			return HSL((0, 0, 0))
		elif a2 == b2 == c2 == 1:
			return HSL((0, 0, 1))
		elif a2 == b2 == c2:
			return HSL((0, 0, a2))
		else:
			hue = a2i / 3 + ((-1)**((b2i-0.5)%3 < a2i)) * (b2-c2)/(a2-c2) / 6

		if c2 == 0: # saturation = 1 & lightness <= 0.5
			return HSL((hue, 1, (a2)/2))
		elif a2 == 1: # saturation = 1 & lightness > 0.5
			return HSL((hue, 1, (1+c2)/2))
		else:
			return HSL((
				hue,
				a2 - c2,
				(a2 + c2)/2
			))
	
	def invert(self: _COLOR, channel: int = 0) -> _COLOR:
		if channel == 0:
			strength = (1 - sum(self.factors) / 3) / (sum(self.factors) / 3)
			return type(self)(tuple((1-f)*strength for f in self.factors))
		else:
			return super().invert(channel)

class ColorScale:
	
	colors : tuple[Color]
	keyframes : tuple[float]

	def __init__(self, *colors, keyframes=None):
		if keyframes:
			keyframes = keyframes
		elif len(colors) <= 1:
			keyframes = [0.]
		else:
			keyframes = list(_Iterators.Spaced(0, 1, len(colors)))
		if keyframes[0] < keyframes[-1]:
			self.keyframes = keyframes
			self.colors = colors
		else:
			self.keyframes = keyframes[::-1]
			self.colors = colors[::-1]

	def __iter__(self):
		return iter(zip(self.keyframes, self.colors))

	def __getitem__(self, weight : float) -> Color:
		
		for i, (p1, p2) in enumerate(zip(_Iterators.Chain([0], self.keyframes), _Iterators.Chain(self.keyframes, [1]))):
			if p1 <= weight <= p2:
				break
		
		if i == 0:
			return self.colors[0]
		elif i == len(self.keyframes):
			return self.colors[-1]
		else:	
			return self.colors[i-1].blend(
				self.colors[i],
				weights=[
					(weight-p1) / (p2-p1),
					(p2-weight) / (p2-p1)
				])