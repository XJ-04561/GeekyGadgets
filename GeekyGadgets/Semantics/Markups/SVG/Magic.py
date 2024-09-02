
import GeekyGadgets.Semantics.Markups.Globals as _Globals
import GeekyGadgets.Semantics.Markups.SVG as _SVG
import GeekyGadgets.Semantics.Markups.General as _General
import GeekyGadgets.Math as _Math
import GeekyGadgets.Functions as _Functions
import GeekyGadgets.Iterators as _Iterators
import GeekyGadgets.Classy as _Classy

_NOT_SET = object()
_WRAP_AFTER = " \t\n\r:.+/}\\])"
_WRAP_BEFORE = "- \t\n\r.+/{\\[("
_WRAP_FORCED = "\n\r"
_DIRECTIONS = {
	"up": 0,
	"right": 90,
	"down": 180,
	"left": 270
}
_TEXT_ANCHOR_PSEUDONYMS = {
	"left"		: "start",
	"center"	: "middle",
	"right"		: "end"
}
_X, _Y = _Globals.TypeVar("_X"), _Globals.TypeVar("_Y")

def drawLine(XY : _Globals.Iterable[_X,_Y], **kwargs):
	return _SVG.Polyline(
		points=" ".join(f"{x},{y}" for x, y in XY),
		**kwargs
	)

def drawLineEnclosed(XY1 : _Globals.Iterable[_X,_Y], XY2 : _Globals.Iterable[_X,_Y], **kwargs):
	return _SVG.Polyline(
		points=" ".join(f"{x},{y}" for x, y in XY1)
		+ " "
		+ " ".join(f"{x},{y}" for x, y in reversed(XY2))
		+ " "
		+",".join(map(format, _Functions.first(XY1))),
		**kwargs
	)

def drawCurve(XY : _Globals.Iterable[_X,_Y], **kwargs) -> _SVG.Path:
	
	if isinstance(XY, _Globals.Iterator):
		XY = tuple(XY)

	x0, y0 = _Functions.first(XY)
	xn, yn = _Functions.last(XY)
	return _SVG.Path(
		d=f"M {x0},{y0} S "
		+ " ".join(
			f"""{x2+(x1-x3)/4},{y2+(y1-y3)/4} {x2},{y2}"""
			for (x1, y1),(x2, y2),(x3, y3) in _Iterators.Echo(XY, 3))
		+ f" {xn},{yn} {xn},{yn}",
		**kwargs
	)

def drawCurveEnclosed(XY1 : _Globals.Iterable[_X,_Y], XY2 : _Globals.Iterable[_X,_Y], **kwargs) -> _SVG.Path:
	if isinstance(XY1, _Globals.Iterator):
		XY1 = tuple(XY1)
	if isinstance(XY2, _Globals.Iterator):
		XY2 = tuple(XY2)

	x10, y10 = _Functions.first(XY1)
	x1n, y1n = _Functions.last(XY1)
	x20, y20 = _Functions.first(XY2)
	x2n, y2n = _Functions.last(XY2)

	# (
	# 	x2-(x3-x1)/4
	# 	if y1 <= y2 >= y3
	# 	else x2
	# ) if x1 <= x2 <= x3
	# else (
	# 	x2+(_Math.atan((y2-y3)/(x2-x3) - (y2-y1)/(x2-x1)) * (x1-x3)/_Math.pi)
	# 	if y1 <= y2 >= y3
	# 	else y2-(y3-y1)/4
	# )

	# (
	# 	y2
	# 	if y1 <= y2 >= y3
	# 	else y1
	# ) if x1 <= x2 <= x3
	# else (
	# 	y2+(_Math.atan((y2-y3)/(x2-x3) - (y2-y1)/(x2-x1)) * (y1-y3)/_Math.pi)
	# 	if y1 <= y2 >= y3
	# 	else y2+(y1-y3)/4
	# )

	return _SVG.Path(
		d=f"M {x10},{y10} S "
		+ " ".join(
			f"""{x2+(x1-x3)/4},{y2+(y1-y3)/4} {x2},{y2}"""
			for (x1, y1),(x2, y2),(x3, y3) in _Iterators.Echo(XY1, 3))
		+ f" {x1n},{y1n} {x1n},{y1n} "
		+ f"L {x1n},{y1n} {x2n},{y2n} "
		+ " ".join(
			f"""{x2+(x1-x3)/4},{y2+(y1-y3)/4} {x2},{y2}"""
			for (x1, y1),(x2, y2),(x3, y3) in _Iterators.Echo(reversed(XY2), 3))
		+ f" {x20},{y20} {x20},{y20} "
		+ f"L {x20},{y20} {x10},{y10}",
		**kwargs
	)

def drawSprites(XY : _Globals.Iterable[_X,_Y], sprite : "type[Sprite]", **kwargs):
	return _SVG.G(
		*(sprite(
			x=x,
			y=y,
			**kwargs
		)
		for x, y in XY)
	)

@_Globals.cache
def starVectors(n : int, inner : float=0.5):
	outerPoints = ((_Math.sin(rad)/2,_Math.cos(rad)/2) for rad in map(lambda i:2*i*_Math.pi/n, range(n)))
	innerPoints = ((inner*_Math.sin(rad)/2,inner*_Math.cos(rad)/2) for rad in map(lambda i:((2*(i+1/2))*_Math.pi)/n, range(n)))
	return tuple(_Iterators.Alternate(outerPoints, innerPoints))

@_Globals.cache
def crossVectors(T : float=1/4):
	#        ____
	#       |    |
	#   ____|    |____
	#  |              |
	#  |____      ____|
	#	    |    |
	#	    |    | <- Starts here and goes up
	#
	return (
		(T/2,	-1/2),
		(T/2,	-T/2),
		(1/2,	-T/2),
		(1/2,	T/2	),
		(T/2,	T/2	),
		(T/2,	1/2	),
		(-T/2,	1/2	),
		(-T/2,	T/2	),
		(-1/2,	T/2	),
		(-1/2,	-T/2),
		(-T/2,	-T/2),
		(-T/2,	-1/2),
	)

class Line(_SVG.Line):
	@_Globals.overload
	def __init__(
		self: "Line",
		/,
		x1 : _Globals.Number | str,
		y1 : _Globals.Number | str,
		x2 : _Globals.Number | str,
		y2 : _Globals.Number | str,
		*,
		ATTRS: dict | _Globals.Attributes = ...,
		**attributes: _Globals.AnyStr | int | float | bool
	) -> _Globals.NoneType: ...
	@_Globals.overload
	def __init__(
		self: "Line",
		/,
		start : tuple[_Globals.Number | str],
		stop : tuple[_Globals.Number | str],
		*,
		ATTRS: dict | _Globals.Attributes = ...,
		**attributes: _Globals.AnyStr | int | float | bool
	) -> _Globals.NoneType: ...
	@_Globals.overload
	def __init__(
		self: "Line",
		/,
		span : tuple[tuple[_Globals.Number | str] , tuple[_Globals.Number | str]],
		*,
		ATTRS: dict | _Globals.Attributes = ...,
		**attributes: _Globals.AnyStr | int | float | bool
	) -> _Globals.NoneType: ...
	def __init__(self: "Line", *args, ATTRS: dict | _Globals.Attributes = {}, **attributes: _Globals.AnyStr | int | float | bool) -> _Globals.NoneType:

		args = list(args)

		if "span" in attributes:
			(x1, y1), (x2, y2) = attributes.pop("span")
		elif "start" in attributes and "stop" in attributes:
			(x1, y1), (x2, y2) = attributes.pop("start"), attributes.pop("stop")
		elif "x1" in attributes and "y1" in attributes and "x2" in attributes and "y2" in attributes:
			x1, y1, x2, y2 = attributes.pop("x1"), attributes.pop("y1"), attributes.pop("x2"), attributes.pop("y2")
		elif len(args) == 1:
			(x1, y1), (x2, y2) = args.pop(0)
		elif len(args) == 2:
			(x1, y1), (x2, y2) = args.pop(0), args.pop(0)
		elif len(args) == 4:
			x1, y1, x2, y2 = args.pop(0), args.pop(0), args.pop(0), args.pop(0)
		else:
			raise ValueError(f"No parameters given for `{self.__class__.__name__}`")
		return super().__init__(*args, x1=x1, y1=y1, x2=x2, y2=y2)

class Text(_SVG.Text):
	@_Globals.overload
	def __init__(
			self: "Text",
			*content: _Globals.AnyStr,
			x : _Globals.Number = 0,
			y : _Globals.Number = 0,
			dx : _Globals.Number = 0,
			dy : _Globals.Number = 0,
			textAnchor : _Globals.Literal["start","left"]|_Globals.Literal["middle","center"]|_Globals.Literal["end","right"] = ...,
			fontSize : _Globals.Number|str = "1em",
			rowLength : _Globals.Number = 80,
			rowDist : _Globals.Number|str = "1em",
			blockDist : _Globals.Number|str = "1em",
			startIndent : _Globals.Number|str = 0,
			rowIndent : _Globals.Number|str = 0,

			ATTRS: dict | _Globals.Attributes = {},
			**attributes: _Globals.AnyStr | _Globals.Number | bool | None
	) -> _Globals.NoneType: ...
	@_Globals.overload
	def __init__(
			self: "Text",
			*content: _Globals.AnyStr,
			x : _Globals.Number = 0,
			y : _Globals.Number = 0,
			dx : _Globals.Number = 0,
			dy : _Globals.Number = 0,
			textAnchor : _Globals.Literal["start","left"]|_Globals.Literal["middle","center"]|_Globals.Literal["end","right"] = ...,
			fontSize : _Globals.Number|str = "1em",
			rowLength : _Globals.Number = 80,
			rowGap : _Globals.Number|str = 0,
			blockGap : _Globals.Number|str = 0,
			startIndent : _Globals.Number|str = 0,
			rowIndent : _Globals.Number|str = 0,

			ATTRS: dict | _Globals.Attributes = {},
			**attributes: _Globals.AnyStr | _Globals.Number | bool | None
	) -> _Globals.NoneType: ...
		
	def __init__(
			self: "Text",
			*content: _Globals.AnyStr,
			ATTRS: dict | _Globals.Attributes = {},
			**attributes: _Globals.AnyStr | _Globals.Number | bool | None
	) -> _Globals.NoneType:
		if "x" in attributes:
			x = attributes["x"]
		else:
			x = attributes["x"] = 0
		
		if attributes.get("textAnchor") in _TEXT_ANCHOR_PSEUDONYMS:
				attributes["textAnchor"] = _TEXT_ANCHOR_PSEUDONYMS[attributes["textAnchor"]]
				
		rowLength = attributes.pop("rowLength", 80)
		if "rowGap" in attributes and attributes["rowGap"] is not None and not ("rowDist" in attributes and attributes["rowDist"] is not None):
			rowDist = _General.ValueUnit.parse(1, "em") + _General.ValueUnit.parse(attributes.pop("rowGap"))
		else:
			rowDist = _General.ValueUnit.parse(attributes.pop("rowDist", "1em"))
		rowIndent = _General.ValueUnit.parse(attributes.pop("rowIndent", _NOT_SET))
		startIndent = _General.ValueUnit.parse(attributes.pop("startIndent", _NOT_SET))
		if "blockGap" in attributes and attributes["blockGap"] is not None and not ("blockDist" in attributes and attributes["blockDist"] is not None):
			blockDist = rowDist + _General.ValueUnit.parse(attributes.pop("blockGap"))
		else:
			blockDist = _General.ValueUnit.parse(attributes.pop("blockDist", rowDist))
		
		firstSpanAttrs = {}
		restSpanAttrs = {}
		if startIndent is not _NOT_SET:
			firstSpanAttrs["dx"] = startIndent
		if rowIndent is not _NOT_SET:
			restSpanAttrs["dx"] = rowIndent
		firstSpanAttrs["dy"] = blockDist
		restSpanAttrs["dy"] = rowDist
		
		tSpans = []
		tSpanAttrs = {name:firstSpanAttrs[name] for name in firstSpanAttrs if name != "dy"}
		for string in map(str, content):
			last = 0
			stops = []
			for i, c in enumerate(string):
				if i - last >= rowLength and stops and stops[-1] - last > 2:
					xPos = x
					rowText = string[last:stops[-1]]

					last = stops[-1]
					stops.clear()
					tSpanAttrs = restSpanAttrs
				elif c in _WRAP_FORCED or i - last >= rowLength:
					xPos = x
					rowText = string[last:i]+"-"*bool(i - last >= rowLength)

					last = i+bool(c in _WRAP_FORCED)
					stops.clear()
					tSpanAttrs = restSpanAttrs
				elif c in _WRAP_BEFORE:
					stops.append(i)
				elif c in _WRAP_AFTER:
					stops.append(i+1)
			if last < len(string):
				xPos = x
				rowText = string[last:]
			tSpanAttrs = firstSpanAttrs

		super().__init__(*tSpans, ATTRS=ATTRS, **attributes)

class Centered(_Globals.ABC):
	_x : _Globals.Number = None
	x : _Globals.Number = property(lambda self: self._x - self.width/2, lambda self, value: setattr(self, "_x", value))
	_y : _Globals.Number = None
	y : _Globals.Number = property(lambda self: self._y - self.height/2, lambda self, value: setattr(self, "_y", value))
	width : _Globals.Number
	height : _Globals.Number

class Sprite:

	@_Globals.overload
	def __init__(self, x, y, width, height, *args, **kwargs) -> _Globals.NoneType: ...
	@_Globals.abstractmethod
	def __init__(self, *args, **kwargs) -> _Globals.NoneType:
		if "strokeWidth" not in kwargs:
			if hasattr(self, "width"):
				self.strokeWidth = self.width * 0.1
			elif hasattr(self, "radius"):
				self.strokeWidth = self.radius * 0.2
			elif  hasattr(self, "r"):
				self.strokeWidth = self.r * 0.2
			elif  hasattr(self, "rx") and hasattr(self, "ry"):
				self.strokeWidth = min(self.rx, self.ry) * 0.2
		return super().__init__(*args, **kwargs)

class Circle(_SVG.Circle, Sprite):
	
	def __init__(self, x, y, width=None, height=None, radius=None, *args, **kwargs) -> _Globals.NoneType:
		self.cx = x
		self.cy = y
		r = radius if radius is not None else width
		self.r = (r if isinstance(r, _Globals.Number) else _General.ValueUnit.parse(r))/2

		super().__init__(*args, **kwargs)

class Ellipse(_SVG.Ellipse, Sprite):
	
	def __init__(self, x, y, width=None, height=None, radius=None, *args, **kwargs) -> _Globals.NoneType:
		self.cx = x
		self.cy = y
		rx = width if width is not None else radius
		ry = height if height is not None else radius
		self.rx = (rx if isinstance(rx, _Globals.Number) else _General.ValueUnit.parse(rx))/2
		self.ry = (ry if isinstance(ry, _Globals.Number) else _General.ValueUnit.parse(ry))/2

		super().__init__(*args, **kwargs)

class Rect(_SVG.Rect, Sprite, Centered):
	
	def __init__(self, x, y, width, height, *args, **kwargs) -> _Globals.NoneType:
		self.x = x
		self.y = y
		self.width = _General.ValueUnit.parse(width)
		self.height = _General.ValueUnit.parse(height)
		
		super().__init__(*args, **kwargs)

class Square(_SVG.Rect, Sprite, Centered):
	
	def __init__(self, x, y, width=None, height=None, radius=None, *args, **kwargs) -> _Globals.NoneType:
		self.height = self.width = _General.ValueUnit.parse(width if width is not None else radius)
		
		self.x = x
		self.y = y
		
		super().__init__(*args, **kwargs)

class Polygon(_SVG.Polygon, Sprite):
	
	PATH : tuple[tuple[_Globals.Number,_Globals.Number]]

	def __init__(self, x, y, width=None, height=None, radius=None, points=None, *args, **kwargs) -> _Globals.NoneType:
		if points is not None:
			return super().__init__(*args, points=points, **kwargs)
		else:
			from GeekyGadgets.Math.LinAlg import translate, dot
			self.x = x
			self.y = y
			if width is not None and height is not None:
				self.width = _General.ValueUnit.parse(width)
				self.height = _General.ValueUnit.parse(height)
			elif width is not None:
				self.width = _General.ValueUnit.parse(width)
				self.height = _General.ValueUnit.parse(width)
			elif radius is not None:
				self.width = _General.ValueUnit.parse(radius)
				self.height = _General.ValueUnit.parse(radius)
			else:
				self.width = 1
				self.height = 1
			
			if "strokeWidth" not in kwargs:
				self.strokeWidth = self.width * 0.05
			
			X = dot(self.PATH, (self.width/2, 0))
			Y = dot(self.PATH, (0, -self.height/2))

			return super().__init__(*args, points=" ".join(f"{x+self.x},{y+self.y}" for x,y in zip(X, Y)), **kwargs)

class Cross(Polygon):
	
	THICKNESS : _Globals.Interval[0,1] = 1/4

	PATH = property(lambda self: crossVectors(self.THICKNESS))

	def __init__(self, x, y, width=None, height=None, thickness : _Globals.Interval[0,1]=1/4, radius=None, points=None, *args, **kwargs) -> _Globals.NoneType:
		if thickness is not None:
			self.THICKNESS = thickness
		super().__init__(x=x, y=y, width=width, height=height, radius=radius, points=points, *args, **kwargs)

class Star(Polygon):
	
	N : int = 5
	INNER : float = 0.5

	@property
	def PATH(self) -> list[tuple[_Globals.Number,_Globals.Number]]:
		return starVectors(self.N, self.INNER)
	
	def __init__(self, x, y, width=None, height=None, radius=None, points=None, N=5, inner : _Globals.Interval[0,1]=0.5, *args, **kwargs) -> _Globals.NoneType:
		self.N = N
		if inner is not None:
			self.INNER = inner
		if width is not None and height is not None:
			rx = _General.ValueUnit.parse(width) / 2
			ry = _General.ValueUnit.parse(height) / 2
		else:
			rx = ry = _General.ValueUnit.parse(width if width is not None else radius) / 2
		super().__init__(x, y, points=" ".join(f"{x+px*rx},{y-py*ry}" for px,py in self.PATH), *args, **kwargs)

class Vertices(_SVG.G, Sprite):
	
	X : _Globals.Number | _General.ValueUnit = 0
	Y : _Globals.Number | _General.ValueUnit = 0
	WIDTH : _Globals.Number | _General.ValueUnit = 1
	HEIGHT : _Globals.Number | _General.ValueUnit = 1
	ANGLE : _Globals.Number | None = None
	HORIZONTAL : bool = False
	CENTER : bool = False

	VECTORS : _Globals.Iterable[tuple[tuple[_Globals.Number,_Globals.Number]]] = ()
	@property
	def LINES(self) -> list[Line]:
		from GeekyGadgets.Math.LinAlg import rotate, translate, dot
		from GeekyGadgets.Math import cos, sin, sqrt
		
		if not self.HORIZONTAL:
			space = [
				[self.WIDTH	, 0				],
				[0			, self.HEIGHT	]
			]
		else:
			space = [
				[0			, self.WIDTH	],
				[self.HEIGHT, 0				]
			]

		if self.ANGLE is not None:
			rotations = (
				[(cosAngle:=cos(self.ANGLE)),	(sinAngle:=sqrt(1 - cosAngle**2))	],
				[-sinAngle,						cosAngle							]
			)
				
		vectors = []
		for v1, v2 in self.VECTORS:
			v1 = dot(space, v1)
			v2 = dot(space, v2)
			if self.CENTER:
				v1, v2 = translate((v1, v2), yD=self.HEIGHT/2)
			if self.ANGLE is not None:
				v1 = dot(rotations, v1)
				v2 = dot(rotations, v2)
			vectors.append(translate((v1, v2), xD=self.X, yD=self.Y))

		return list(map(Line, vectors))

	def __init__(
		self: "Vertices",
		/,
		x : _Globals.Number | str=0,
		y : _Globals.Number | str=0,
		width : _Globals.Number | None=None,
		height : _Globals.Number | None=None,
		*,
		angle : _Globals.Number | str | None=None,
		horizontal : bool=False,
		center : bool=False,
		ATTRS: dict | _Globals.Attributes = {},
		**attributes: _Globals.AnyStr | int | float | bool
	) -> _Globals.NoneType:
		
		self.X = _General.ValueUnit.parse(x)
		self.Y = _General.ValueUnit.parse(y)
		self.WIDTH = _General.ValueUnit.parse(width)
		self.HEIGHT = _General.ValueUnit.parse(height)

		if isinstance(angle, str):
			if angle.endswith("deg"):
				import GeekyGadgets.Math as Math
				angle = Math.radians(float(angle.removesuffix("deg")))
			elif angle.endswith("rad"):
				angle = float(angle.removesuffix("rad"))
			else:
				import GeekyGadgets.Math as Math
				angle = Math.radians(_DIRECTIONS[angle])
		
		assert angle is None or isinstance(angle, _Globals.Number)

		self.ANGLE = angle
		self.HORIZONTAL = horizontal
		self.CENTER = center
		
		if "strokeWidth" not in attributes and "stroke-width" not in ATTRS:
			self.strokeWidth = min(self.WIDTH,self.HEIGHT) / 10

		super().__init__(
			*self.LINES,
			ATTRS=ATTRS,
			**attributes
		)

class T(Vertices):

	VECTORS = (
		((-1/2	,	1),(1/2	,	1)),
		((0		,	0),(0	,	1)),
	)

class V(Vertices):

	VECTORS = (
		((-1/2	,	1),(0	,	0)),
		((0		,	0),(1/2	,	1)),
	)

class I(Vertices):

	VECTORS = (
		((-1/2	,	1),(1/2	,	1)),
		((0		,	0),(0	,	1)),
		((-1/2	,	0),(1/2	,	0)),
	)

class X(Vertices):

	VECTORS = (
		((-1/2	,	1),(1/2	,	0)),
		((-1/2	,	0),(1/2	,	1)),
	)

class Г(Vertices):

	VECTORS = (
		((-1/2	,	0),(-1/2,	1)),
		((-1/2	,	1),(1/2	,	1)),
	)

class Plus(Vertices):

	VECTORS = (
		((-1/2	,	1/2	),	(0		,	1/2	)),
		((0		,	1/2	),	(1/2	,	1/2	)),
		((0		,	1	),	(0		,	1/2	)),
		((0		,	1/2	),	(0		,	0	)),
	)

class BoxPlot(Vertices):
	
	Q : tuple[_Globals.Number,_Globals.Number,_Globals.Number,_Globals.Number,_Globals.Number] = ()

	@property
	def VECTORS(self) -> tuple[tuple[tuple[_Globals.Number],tuple[_Globals.Number]]]:
		Q0, Q1, Q2, Q3, Q4 = self.Q
		if Q4-Q0:
			y4 = 1
			y3 = (Q3-Q0)/(Q4-Q0)
			y2 = (Q2-Q0)/(Q4-Q0)
			y1 = (Q1-Q0)/(Q4-Q0)
			y0 = 0
		else:
			y4 = 1
			y3 = 3/4
			y2 = 2/4
			y1 = 1/4
			y0 = 0
		return (
			((-1/2	,	y4),(1/2	,	y4)), # Top horizontal			 -
			((0		,	y4),(0		,	y3)), # Top vertical			 |
			((-1/2	,	y3),(1/2	,	y3)), # Top box horizontal		 -
			((-1/2	,	y3),(-1/2	,	y1)), # Box left vertical	   |
			((-1/2	,	y2),(1/2	,	y2)), # Box middle horizontal	 -
			((1/2	,	y3),(1/2	,	y1)), # Box right vertical		   |
			((-1/2	,	y1),(1/2	,	y1)), # Bottom box horizontal		 -
			((0		,	y0),(0		,	y1)), # Bottom vertical			 |
			((-1/2	,	y0),(1/2	,	y0)), # Bottom horizontal		 -
		)


	def __init__(self: "BoxPlot", /, Q, x: _Globals.Number | str = 0, y: _Globals.Number | str = 0, width: _Globals.Number | None = None, *, angle: _Globals.Number | str | _Globals.NoneType = None, horizontal: bool = False, ATTRS: dict | _Globals.Attributes = {}, **attributes: _Globals.AnyStr | int | float | bool) -> _Globals.NoneType:
		self.Q = Q
		super().__init__(x=x, y=y, width=width, height=Q[4]-Q[0], angle=angle, horizontal=horizontal, ATTRS=ATTRS, **attributes)

	@property
	def inner(self):
		_,_,topLine,_,_,_,bottomLine,*_ = self.content
		return _SVG.Rect(
			x=topLine.x1,
			y=topLine.y1,
			width=bottomLine.x2-topLine.x1,
			height=bottomLine.y2-topLine.y1
		)
