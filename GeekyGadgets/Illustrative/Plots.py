

from GeekyGadgets.Illustrative.Globals import *

import GeekyGadgets.Formatting as _Formatting
import GeekyGadgets.Functions as _Funcs
import GeekyGadgets.Colors.General as _Colors
import GeekyGadgets.Iterators as _Iterators
import GeekyGadgets.Classy as _Classy
import GeekyGadgets.Math as _Math
import GeekyGadgets.Math.Stats.Binning as Binning
import GeekyGadgets.Math.Stats as _MathStats
import GeekyGadgets.Math.Stats.Functions as _StatFuncs
import GeekyGadgets.Semantics.Markups.SVG as _SVG
import GeekyGadgets.Semantics.Markups.SVG.Magic as _Magic

_X, _Y = TypeVar("_X"), TypeVar("_Y")

class Plot(Illustrator):
	"""
	Graph Attributes:
	```python
		title : str|None
		description : str|None
		labels : Iterable[str]|dict[int,str]|None
		yTitle : str
		xTitle : str
		xLim : tuple[Number,Number]|None
		yLim : tuple[Number,Number]|None
		xTicks : Iterable[Number]|int|None
		yTicks : Iterable[Number]|int|None
		xLabels : Iterable[str]|None
		yLabels : Iterable[str]|None
		defaultColor : _Colors.Color|None
		significantDigits : int
		yLabelsTilt : bool
		xLabelsTilt : bool
	```
	"""
	
	SHOW_LEGEND : bool = _Classy.Default(lambda self: len(self.labels) > 1)
	DEFAULT_COLOR = _Colors.ColorScale(_Colors.HSV(0., .8, 1.), _Colors.HSV(1., .8, 1.))
	CSS : str = ""
	"""To select for specific `svg` element, use format tag {plotID}"""

	

	data : Iterable
	labels : dict[int,str]
	defaultColor : _Colors.Color
	colors : Iterable[_Colors.Color|tuple[_Colors.Color,_Colors.Color]] = _Classy.Default(lambda self:list(zip(self.colorsStroke, self.colorsFill)))
	colorsStroke : Iterable[_Colors.Color]
	colorsFill : Iterable[_Colors.Color]
	fillOpacity : dict[int,float] = cached_property(lambda self:{-1:0.2})
	strokeOpacity : dict[int,float] = cached_property(lambda self:{-1:1.0})
	background : _Colors.Color|str = "var(--PRIMARY-BACKGROUND)"
	significantDigits : int = 3

	title : str|None = _Classy.CachedDefault(lambda self: _Formatting.Case.TitleCase(self.__class__.__name__))
	description : str|None = _Classy.Default(lambda self: _Funcs.first(self.labels.values(), None) if len(self.labels) == 1 else None)
	xTitle : str|None = None
	yTitle : str|None = None
	xLim : tuple[Number,Number]|None = (0, 100)
	yLim : tuple[Number,Number]|None = (0, 100)
	xTicks : list[Number]|None = None
	yTicks : list[Number]|None = None
	xLabels : tuple[str]|None = None
	yLabels : tuple[str]|None = None
	xRange : Number = property(lambda self:self.xLim[1]-self.xLim[0] if self.xLim is not None else None)
	yRange : Number = property(lambda self:self.yLim[1]-self.yLim[0] if self.yLim is not None else None)
	xLabelsTilt : bool = False
	yLabelsTilt : bool = False
	xLabelsWidth : Number = 6
	yLabelsWidth : Number = 6
	xLabelOffsets : list[float] = _Classy.CachedDefault["xLabels"](lambda self: [1]*len(self.xLabels))
	yLabelOffsets : list[float] = _Classy.CachedDefault["yLabels"](lambda self: [1]*len(self.yLabels))
	xLabelsJustify : Number = _Classy.CachedDefault["xLabels"](lambda self: ["middle"]*len(self.xLabels))
	yLabelsJustify : Number = _Classy.CachedDefault["yLabels"](lambda self: ["middle"]*len(self.yLabels))
	legendOffset : tuple[Number,Number] = (0,0)

	maskFillIdList = _Classy.CachedDefault["data"](lambda self: [f"X{_Funcs.randomAlpha()}" for _ in range(len(self.data))])
	maskStrokeIdList = _Classy.CachedDefault["data"](lambda self: [f"X{_Funcs.randomAlpha()}" for _ in range(len(self.data))])
	gradientFillIdList = _Classy.CachedDefault["data"](lambda self: [f"X{_Funcs.randomAlpha()}" for _ in range(len(self.data))])
	gradientStrokeIdList = _Classy.CachedDefault["data"](lambda self: [f"X{_Funcs.randomAlpha()}" for _ in range(len(self.data))])

	colorsStroke : Iterable[_Colors.Color] = _Classy.Default(lambda self: self.colorsFill)
	@_Classy.Default
	def colorsFill(self) -> Iterable[_Colors.Color]:
		N = len(self.data)
		return [_Colors.ColorScale(self.DEFAULT_COLOR[i/N]) for i in range(N)]
	
	@overload
	def __init__(self, *, title : str|None=None, description : str|None=None, labels : Iterable[str]|dict[int,str]|None=None, colors : Iterable[_Colors.Color|tuple[_Colors.Color,_Colors.Color]], colorsStroke : Iterable[_Colors.Color], colorsFill : Iterable[_Colors.Color], yTitle : str="Y", xTitle : str="X", xLim : tuple[Number,Number]|None=None, yLim : tuple[Number,Number]|None=None, xTicks : Iterable[Number]|int|None=None, yTicks : Iterable[Number]|int|None=None, xLabels : Iterable[str]|None=None, yLabels : Iterable[str]|None=None, defaultColor : _Colors.Color|None=None, significantDigits : int=5, yLabelsTilt : bool=False, xLabelsTilt : bool=False): ...
	def __init__(self, **graphAttrs):
		if graphAttrs.get("labels") is None:
			self.labels = {}
		elif isinstance(graphAttrs["labels"], dict):
			self.labels = graphAttrs.pop("labels").copy()
		else:
			self.labels = dict(enumerate(graphAttrs.pop("labels")))
		for name, value in graphAttrs.items():
			setattr(self, name, value)

	def showLegend(self):
		self.SHOW_LEGEND = True
	def hideLegend(self):
		self.SHOW_LEGEND = False
	
	def resetFillOpacity(self):
		try:
			del self.fillOpacity
		except:
			pass
	def setFillOpacity(self, id=-1, value=0):
		self.fillOpacity[id] = value
	def getFillOpacity(self, id=None):
		if id is None:
			return self.fillOpacity
		elif id in self.fillOpacity:
			return self.fillOpacity[id]
		else:
			return self.fillOpacity.get(-1)
	
	def resetStrokeOpacity(self):
		try:
			del self.strokeOpacity
		except:
			pass
	def setStrokeOpacity(self, id=-1, value=0):
		self.strokeOpacity[id] = value
	def getStrokeOpacity(self, id=None):
		if id is None:
			return self.strokeOpacity
		elif id in self.strokeOpacity:
			return self.strokeOpacity[id]
		else:
			return self.strokeOpacity.get(-1)

	def validate(self):
		
		if len(self.xTicks) != len(self.xLabels):
			raise ValueError(f"Number of ticks along the X-axis ({len(self.xTicks)}) does not match the number of labels ({len(self.xLabels)}) for the axis.")
		if len(self.yTicks) != len(self.yLabels):
			raise ValueError(f"Number of ticks along the X-axis ({len(self.yTicks)}) does not match the number of labels ({len(self.yLabels)}) for the axis.")
		if min(self.xTicks) < self.xLim[0]:
			raise ValueError(f"Lowest value tick along the X-axis {min(self.xTicks)} must not be lower than the lower limit of ({self.xLim[0]}) the axis.")
		if max(self.xTicks) > self.xLim[-1]:
			raise ValueError(f"Highest value tick along the X-axis {max(self.xTicks)} must not be greater than the upper limit of ({self.xLim[-1]}) the axis.")
		if min(self.yTicks) < self.yLim[0]:
			raise ValueError(f"Lowest value tick along the Y-axis {min(self.yTicks)} must not be lower than the lower limit of ({self.yLim[0]}) the axis.")
		if max(self.yTicks) > self.yLim[-1]:
			raise ValueError(f"Highest value tick along the Y-axis {max(self.yTicks)} must not be greater than the upper limit of ({self.yLim[-1]}) the axis.")

	def illustrateHTML(self, *, color : _Colors.Color|_Colors.ColorScale|None=None, **kwargs):
		from GeekyGadgets.Semantics.Markups.HTML import Figure, Div
		return Figure(Div(self.illustrateSVG(color=color, **kwargs)))
		
	def illustrateSVG(self, *, color : _Colors.Color|_Colors.ColorScale|None=None, **kwargs):

		self.validate()

		AXES_FONT_SIZE = 4
		TITLE_FONT_SIZE = AXES_FONT_SIZE + 1
		DESC_FONT_SIZE = AXES_FONT_SIZE - 1
		Y_TICK_FONT_SIZE = 2 if sum(map(len, self.yLabels)) / len(self.yLabels) > 3 else 3
		Y_TICK_SPACE = 2 * AXES_FONT_SIZE
		
		X_TICK_FONT_SIZE = 2 if sum(map(len, self.xLabels)) / len(self.xLabels) > 3 else 3
		X_TICK_SPACE = 2 * AXES_FONT_SIZE
		

		LEFT = -1 - Y_TICK_SPACE - AXES_FONT_SIZE*bool(self.yTitle)
		RIGHT = 105
		TOP = -5 - TITLE_FONT_SIZE*bool(self.title) - DESC_FONT_SIZE*bool(self.description)
		BOTTOM = 101 + X_TICK_SPACE + AXES_FONT_SIZE*bool(self.xTitle)
		LINE_WIDTH = 0.25

		

		from GeekyGadgets.Semantics.Markups.SVG import Svg, Line, Rect, Text, Tspan, G as Group, Title, Defs, LinearGradient, Stop, Mask, Style
		import GeekyGadgets.Semantics.Markups.SVG.Magic as _Magic

		page = Svg(
			Style(open(os.path.join(os.path.split(__file__)[0], "CSS", "BASE_SVG.css"), "r").read(), type="text/css"),
			Style(self.CSS+f"/*{self.xLabelsWidth}*/", type="text/css"),
			Rect(x=0, y=0, height=100, width=100, fill=self.background, strokeWidth=0),
			clipFillDefs := Defs(),
			clipStrokeDefs := Defs(),
			gradientFillDefs := Defs(),
			gradientStrokeDefs := Defs(),
			yAxis := Group(name="yAxis", Class="PlotY-Axis"), #Line(x1=0, y1=100, x2=0, y2=0)),
			xAxis := Group(name="xAxis", Class="PlotX-Axis"), #Line(x1=0, y1=100, x2=100, y2=100)),
			header := Group(name="header", Class="PlotHeader"),
			legend := Group(name="legend", Class="Legend"),
			height="100%",
			width="100%",
			viewBox=f"{LEFT} {TOP} {RIGHT+abs(LEFT)} {BOTTOM+abs(TOP)}",
			Class="GeekyIllustration Plot"
		)
		
		if self.yTitle:
			yAxis.addChild(Text(self.yTitle, x=LEFT+AXES_FONT_SIZE, y=50, textAnchor="middle", fontSize=AXES_FONT_SIZE, transform=f"rotate(270 {LEFT+AXES_FONT_SIZE},50)"))
		if self.xTitle:
			xAxis.addChild(Text(self.xTitle, x=50, y=BOTTOM-AXES_FONT_SIZE+1, textAnchor="middle", fontSize=AXES_FONT_SIZE))

		if self.title:
			header.addChild(Text(self.title, x=50, y=TOP+TITLE_FONT_SIZE+2, fontSize=TITLE_FONT_SIZE, textAnchor="middle"))
			if self.description:
				header.addChild(Text(self.description, x=50, y=TOP+TITLE_FONT_SIZE+2+DESC_FONT_SIZE, fontSize=DESC_FONT_SIZE, textAnchor="middle"))

		dY = 100 / self.yRange
		for i, value, label in zip(_Iterators.Count(), self.yTicks, self.yLabels):
			pos = 100 - dY*(value-self.yLim[0])
			yAxis.addChild(Line(x1=-self.yLabelOffsets[i], y1=pos, x2=0, y2=pos, strokeWidth=LINE_WIDTH))
			if not label:
				pass
			elif self.yLabelsTilt:
				yAxis.addChild(_Magic.Text(label, x=-self.yLabelOffsets[i]-.25, y=pos+Y_TICK_FONT_SIZE/3, fontSize=Y_TICK_FONT_SIZE, rowLength=self.yLabelsWidth, strokeWidth=0.01, textAnchor="end", transform=f"rotate(-45 {-1.25},{pos+Y_TICK_FONT_SIZE/3})"))
			else:
				yAxis.addChild(_Magic.Text(label, x=-self.yLabelOffsets[i]-.25, y=pos+Y_TICK_FONT_SIZE/3, fontSize=Y_TICK_FONT_SIZE, rowLength=self.yLabelsWidth, strokeWidth=0.01, textAnchor="end"))

		dX = 100 / self.xRange
		for i, value, label in sorted(zip(_Iterators.Count(), self.xTicks, self.xLabels), key=lambda x:self.xLabelOffsets[x[0]], reverse=True):
			pos = dX*(value-self.xLim[0])
			xAxis.addChild(tickGroup := Group(name=value))
			tickGroup.addChild(Line(x1=pos, y1=100, x2=pos, y2=101, strokeWidth=LINE_WIDTH))
			if self.xLabelOffsets[i] > 1:
				tickGroup.addChild(Line(x1=pos, y1=101, x2=pos, y2=100+self.xLabelOffsets[i], strokeOpacity="0.2", strokeWidth=LINE_WIDTH))
			
			if not label:
				pass
			elif self.xLabelsTilt:
				tickGroup.addChild(_Magic.Text(label, x=pos, y=100+self.xLabelOffsets[i]+X_TICK_FONT_SIZE, fontSize=X_TICK_FONT_SIZE, rowLength=self.xLabelsWidth, strokeWidth=0.03, textAnchor="start", transform=f"rotate(45 {pos},{100+1+X_TICK_FONT_SIZE})"))
			else:
				tickGroup.addChild(_Magic.Text(label, x=pos, y=100+self.xLabelOffsets[i]+X_TICK_FONT_SIZE, fontSize=X_TICK_FONT_SIZE, rowLength=self.xLabelsWidth, strokeWidth=0.03, textAnchor=self.xLabelsJustify[i]))

		if isinstance(self.colors, Iterable):
			colors = list(self.colors)
		else:
			colors = list(_Iterators.Repeat(self.colors, len(self.data)))
		if not isinstance(colors[0], (list,tuple)):
			colors = list(zip((c if isinstance(c, _Colors.ColorScale ) else _Colors.ColorScale(c) for c in colors), (c if isinstance(c, _Colors.ColorScale ) else _Colors.ColorScale(c) for c in colors)))
		
		for i, (maskFillID, maskStrokeID, gradientFillID, gradientStrokeID, (gradientFill, gradientStroke)) in enumerate(zip(self.maskFillIdList, self.maskStrokeIdList, self.gradientFillIdList, self.gradientStrokeIdList, colors)):

			clipFillDefs.addChild(Mask(id=maskFillID))
			clipStrokeDefs.addChild(Mask(id=maskStrokeID))
			gradientFillDefs.addChild(LinearGradient(
				*(Stop(offset=f"{100*value}%", stopColor=color.hex()) for value, color in gradientFill),
				id=gradientFillID,
				x1=0,
				x2=0,
				y1=0,
				y2=1
			))
			gradientStrokeDefs.addChild(LinearGradient(
				*(Stop(offset=f"{100*value}%", stopColor=color.hex()) for value, color in gradientStroke),
				id=gradientStrokeID,
				x1=0,
				x2=0,
				y1=0,
				y2=1
			))
			page.addChild(
				Rect(
					x=0-LINE_WIDTH/2,
					y=0-LINE_WIDTH/2,
					width=100+LINE_WIDTH,
					height=100+LINE_WIDTH,
					fill=f"url(#{gradientFillID})",
					strokeWidth=0,
					mask=f"url(#{maskFillID})"
			))
			page.addChild(
				Rect(
					x=0-LINE_WIDTH/2,
					y=0-LINE_WIDTH/2,
					width=100+LINE_WIDTH,
					height=100+LINE_WIDTH,
					fill=f"url(#{gradientStrokeID})",
					strokeWidth=0,
					mask=f"url(#{maskStrokeID})"
			))
		if self.SHOW_LEGEND:
			ROW_LENGTH = _Math.ceil(_Math.sqrt(sum(map(len, self.labels.values()))))

			legend.addChild(legendBox := Rect(
				x=100-self.legendOffset[0]-ROW_LENGTH*DESC_FONT_SIZE-LINE_WIDTH,
				y=self.legendOffset[1],
				width=ROW_LENGTH*DESC_FONT_SIZE+LINE_WIDTH,
				height=LINE_WIDTH,
				stroke="var(--SECONDARY-COLOR)",
				fill="var(--SECONDARY-BACKGROUND)",
				fillOpacity=2/16,
				strokeWidth=LINE_WIDTH
			))
			page.addChild(Defs(
				legendMask := Mask(
					legendMaskRect := Rect(
						x=100-self.legendOffset[0]-(ROW_LENGTH*DESC_FONT_SIZE)-LINE_WIDTH/2,
						y=self.legendOffset[1]+LINE_WIDTH/2,
						width=ROW_LENGTH*DESC_FONT_SIZE-LINE_WIDTH,
						height=0
					),
					fill="white",
					strokeWidth=0
				),
				id=(legendClipID := f"X{_Funcs.randomAlpha()}")
			))
			
			height = LINE_WIDTH
			for i, label in self.labels.items():
				legend.addChild(textBox := _Magic.Text(label, x=100-self.legendOffset[0]-DESC_FONT_SIZE*2, y=self.legendOffset[1]+DESC_FONT_SIZE+height, fontSize=DESC_FONT_SIZE, rowLength=ROW_LENGTH*1.5, textAnchor="end", mask=f"url(#{legendClipID})"))
				nRows = len(textBox.children)
				legend.addChild(Rect(x=100-self.legendOffset[0]-DESC_FONT_SIZE*2*(3/4), y=self.legendOffset[1]+(nRows-1/2)*DESC_FONT_SIZE/2+DESC_FONT_SIZE/4+height, width=DESC_FONT_SIZE/2, height=DESC_FONT_SIZE/2, strokeWidth=1/4, mask=f"url(#{legendClipID})", fill=f"url(#{self.gradientFillIdList[i]})", fillOpacity=2/16, stroke=f"url(#{self.gradientStrokeIdList[i]})"))
				height += DESC_FONT_SIZE*3/4+DESC_FONT_SIZE*nRows
			legendBox.height += height+LINE_WIDTH
			legendMaskRect.height += height
		
		page.addChild(Rect(x=0, y=0, height=100, width=100, fill="transparent", stroke="var(--PRIMARY-COLOR)", strokeWidth=LINE_WIDTH))

		return page

class Plot1D(Plot):
	
	data : tuple[Iterable[_X]]

	title : str
	description : str|None

	xTitle : str|None
	xLim : tuple[Number,Number] = property(lambda self: (0, len(self.data)+1))
	xTicks : list[Number] = property(lambda self: list(range(self.xLim[0]+1, self.xLim[1])))
	@_Classy.CachedDefault["xTicks"]
	def xLabels(self) -> tuple[str]:
		return list(_Iterators.AlphaRange(len(self.xTicks)))
	@_Classy.CachedDefault["xLabels","xLabelsTilt"]
	def xLabelsWidth(self) -> int:
		if self.xLabelsTilt:
			return 90 / (len(self.xLabels)) * 1.4
		else:
			return (90 / (len(self.xLabels)))

	yTitle : str|None
	@_Classy.CachedDefault["yTicks"]
	def yLim(self) -> tuple[Number,Number]:
		return (self.yTicks[0], self.yTicks[-1])
	@_Classy.CachedDefault["yLim"]
	def yTicks(self) -> list[Number]:
		if _Classy.CachedDefault.isSet(self, "yLim"):
			return list(_Iterators.Spaced(self.yLim[0], self.yLim[-1], 5))
		else:
			return _Formatting.SISize.numericScale(min(map(min, self.data)), max(map(max, self.data)), 5, 10)
	@_Classy.CachedDefault["yTicks","yLim"]
	def yLabels(self) -> tuple[str]:
		return tuple(_Formatting.SISize.floatEmphasize(tick, *self.yLim, length=self.significantDigits) for tick in self.yTicks)

class Plot2D(Plot):
	
	SHOW_AUC : bool = False

	data : tuple[Iterable[tuple[_X,tuple[_Y]]]]
	seriesAUC : set[int]

	title : str
	description : str|None

	xTitle : str = "X"
	
	@_Classy.Default
	def xLim(self) -> tuple[Number,Number]:
		return (self.xTicks[0], self.xTicks[-1])
	@_Classy.CachedDefault["xLim"]
	def xTicks(self) -> list[Number]:
		if _Classy.CachedDefault.willDefault(self, "xLim"):
			return _Formatting.SISize.numericScale(min(min(map(lambda xy:xy[0], series)) for series in self.data), max(max(map(lambda xy:xy[0], series)) for series in self.data), 5, 10)
		else:
			return list(_Iterators.Spaced(self.xLim[0], self.xLim[-1], 5))
	@_Classy.CachedDefault["xLim","xTicks"]
	def xLabels(self) -> tuple[str]:
		# return tuple(_Formatting.SISize.floatEmphasize(tick, *self.xLim, length=self.significantDigits) for tick in self.xTicks)
		return tuple(_Formatting.SISize.roundSignificant(tick, digits=self.significantDigits) for tick in self.xTicks)
	
	yTitle : str = "Y"
	@_Classy.Default
	def yLim(self) -> tuple[Number,Number]:
		return (self.yTicks[0], self.yTicks[-1])
	@_Classy.CachedDefault["yLim"]
	def yTicks(self) -> list[Number]:
		if _Classy.CachedDefault.willDefault(self, "yLim"):
			return _Formatting.SISize.numericScale(min(min(map(lambda xy:min(xy[1]), series)) for series in self.data), max(max(map(lambda xy:max(xy[1]), series)) for series in self.data), 5, 10)
		else:
			return list(_Iterators.Spaced(self.yLim[0], self.yLim[-1], 5))
	@_Classy.CachedDefault["yTicks","yLim"]
	def yLabels(self) -> tuple[str]:
		# return tuple(_Formatting.SISize.floatEmphasize(tick, *self.yLim, length=self.significantDigits) for tick in self.yTicks)
		return tuple(_Formatting.SISize.roundSignificant(tick, digits=self.significantDigits) for tick in self.yTicks)
	
	style : Literal["line","scatter","curve","heat"] = "line"
	errorStyle : Literal["clone","widen","shadow","whiskers","boxplot"] = "shadow"
	markerSprites : dict[int,_Magic.Sprite] = cached_property(lambda self: {-1 : _Magic.Cross})

	def __init__(self, *data : Iterable[tuple[_X,_Y]], **graphAttrs):
		
		self.seriesAUC = set()
		self.data = tuple(
			sorted(
				(
					(
						x0,
						tuple(y for x,y in series if x0 == x)
					)
					for x0 in set(x for x,y in series)
				),
				key=lambda x:x[0]
			)
			for series in data
		)
		super().__init__(**graphAttrs)

	@_Classy.CachedDefault["style"]
	def symbolWidth(self):
		return max(2, 0.9 * 100*min(abs(x2-x1) for data in self.data for (x1,y1),(x2,y2) in _Iterators.Echo(data)) / self.xRange)
	
	@_Classy.Default["style", "errorStyle"]
	def drawFunc(self):
		
		if self.style == "line":
			return lambda XY, id, width=1, **kwargs: (
				(
					pLine := _Magic.drawLine(
						XY := [(x, sum(ySet)/len(ySet)) for x,ySet in XY if ySet] if isinstance(XY[0][1], Iterable) else XY,
						strokeWidth=width,
						**({"stroke":"white","fill":"transparent"}|(kwargs if self.errorStyle != "widen" else kwargs|{"stroke":"black","strokeDasharray":"2,2"}))
					),
				),
				(
					_SVG.Polyline(
						points=f"{0},{100} {pLine.points} {100},{100}",
						strokeWidth=width,
						**{"stroke":"transparent","fill":"white"}|kwargs
					),
				)
				if self.SHOW_AUC or id in self.seriesAUC
				else ()
			)
		elif self.style == "scatter":
			return lambda XY, id, width=1, **kwargs: (
				(
					_Magic.drawSprites(
						XY := [(x, y) for x,ySet in XY for y in ySet] if isinstance(XY[0][1], Iterable) else XY,
						sprite=self.markerSprites[id]
							   if id in self.markerSprites
							   else self.markerSprites[-1],
						width=width*self.symbolWidth,
						height=width*self.symbolWidth,
						**({"stroke":"white","fill":"transparent"}|(kwargs if self.errorStyle != "widen" else kwargs|{"stroke":"black"}))
					),
				),
				()
			)
		elif self.style == "curve":
			return lambda XY, id, width=1, **kwargs: (
				(
					pCurve := _Magic.drawCurve(
						XY := [(x, sum(ySet)/len(ySet)) for x,ySet in XY if ySet] if isinstance(XY[0][1], Iterable) else XY,
						strokeWidth=width,
						**({"stroke":"white","fill":"transparent"}|(kwargs if self.errorStyle != "widen" else kwargs|{"stroke":"black","strokeDasharray":"2,2"}))
					),
				),
				(
					_SVG.Path(
						d=f"M {0},{100} L {0},{100} {XY[0][0]},{XY[0][1]} {pCurve.d.partition(' S ')[1]} L {XY[-1][0]},{XY[-1][1]} {100},{100}",
						strokeWidth=width,
						**{"stroke":"transparent","fill":"white"}|kwargs
					),
				)
				if self.SHOW_AUC or id in self.seriesAUC
				else ()
			)
		elif self.style == "heat":
			return lambda XY, id, width=1, **kwargs: ((), ())
		else:
			return lambda XY, id, width=1, **kwargs: ((), ())
		
	@_Classy.Default["style", "errorStyle"]
	def drawErrorFunc(self):
		if self.errorStyle == "clone":
			return lambda XY, id, width=1, **kwargs: (
				(
					_SVG.G(
						*self.drawFunc(
							[(x, min(ySet)) for x,ySet in XY],
							id=id,
							width=width,
							**{"stroke":"white","fill":"transparent"}|kwargs
						)[0],
						*self.drawFunc(
							[(x, max(ySet)) for x,ySet in XY],
							id=id,
							width=width,
							**{"stroke":"white","fill":"transparent"}|kwargs
						)[0]
					),
				),
				()
			)
		elif self.errorStyle == "widen":
			if self.style == "line":
				return lambda XY, id, width=1, **kwargs: (
					(
						_Magic.drawLineEnclosed(
							[(x, min(ySet)) for x,ySet in XY],
							[(x, max(ySet)) for x,ySet in XY],
							strokeWidth=width,
							**kwargs|{"stroke":"white","fill":"white"}
						),
					),
					()
				)
			elif self.style == "curve":
				return lambda XY, id, width=1, **kwargs: (
					(
						_Magic.drawCurveEnclosed(
							[(x, min(ySet)) for x,ySet in XY],
							[(x, max(ySet)) for x,ySet in XY],
							strokeWidth=width,
							**kwargs|{"stroke":"white","fill":"white"}
						),
					),
					()
				)
			elif self.style == "scatter":
				return lambda XY, id, width=1, **kwargs: (
					(
						_SVG.G(
							*(
								_SVG.Ellipse(
									cx=x,
									cy=(max(ySet)-min(ySet))/2+min(ySet),
									ry=(max(ySet)-min(ySet))/2,
									rx=width*self.symbolWidth/2,
									strokeWidth=0
								)
								for x,ySet in XY
								if ySet
							),
							**kwargs|{"stroke":"white","fill":"white"}
						),
					),
					()
				)
		elif self.errorStyle == "shadow":
			if self.style == "line":
				return lambda XY, id, width=1, **kwargs: (
					(
						_Magic.drawLineEnclosed(
							[(x, min(ySet)) for x,ySet in XY],
							[(x, max(ySet)) for x,ySet in XY],
							strokeWidth=width,
							**kwargs|{"opacity":0.33,"stroke":"white","fill":"white"}
						),
					),
					()
				)
			elif self.style == "curve":
				return lambda XY, id, width=1, **kwargs: (
					(
						_Magic.drawCurveEnclosed(
							[(x, min(ySet)) for x,ySet in XY],
							[(x, max(ySet)) for x,ySet in XY],
							strokeWidth=width,
							**kwargs|{"opacity":0.33,"stroke":"white","fill":"white"}
						),
					),
					()
				)
			elif self.style == "scatter":
				return lambda XY, id, width=1, **kwargs: (
					(),
					(
						_SVG.G(
							*(
								_SVG.Ellipse(
									cx=x,
									cy=(max(ySet)-min(ySet))/2+min(ySet),
									ry=(max(ySet)-min(ySet))/2,
									rx=width*self.symbolWidth/2,
									strokeWidth=0
								)
								for x,ySet in XY
								if ySet
							),
							**(kwargs|{"opacity":0.33,"fill":"white","stroke":"white"})
						),
					)
				)
		elif self.errorStyle == "whiskers":
			if self.style != "heat":
				return lambda XY, id, width=1, **kwargs: (
					(
						_SVG.G(
							*(
								_Magic.I(x=x, y=min(ySet), width=width*self.symbolWidth, height=max(ySet)-min(ySet), **kwargs|{"stroke":"white","fill":"transparent"})
								if len(ySet) > 1
								else _Magic.X(x=x, y=min(ySet), width=width*self.symbolWidth, height=width*self.symbolWidth/2, **kwargs|{"stroke":"white","fill":"transparent"})
								for x,ySet in XY
							)
						),
					),
					()
				)
		elif self.errorStyle == "boxplot":
			if self.style == "heat":
				return lambda XY, id, width=1, **kwargs: ((),())
			else:
				return lambda XY, id, width=1, **kwargs: (
					(
						strokes := _SVG.G(
							*(
								_Magic.BoxPlot(Q=_StatFuncs.quantiles(ySet), x=x, y=min(ySet), width=width*self.symbolWidth, **kwargs|{"stroke":"white","fill":"transparent"})
								if len(ySet) >= 3 else _Magic.I(x=x, y=min(ySet), width=width*self.symbolWidth, height=max(ySet)-min(ySet), **kwargs|{"stroke":"white","fill":"transparent"})
								if len(ySet) > 1 else _Magic.X(x=x, y=min(ySet), width=width*self.symbolWidth, height=width*self.symbolWidth/2, **kwargs|{"stroke":"white","fill":"transparent"})
								for x,ySet in XY
							)
						),
					),
					(
						_SVG.G(
							*(
								inner for obj in strokes if isinstance(obj, _Magic.BoxPlot) if setattr(inner := obj.inner, "fill", "white") is None and setattr(inner, "stroke", "transparent") is None and setattr(inner, "opacity", 0.33) is None
							)
						),
					)
				)
		return lambda XY, id, width=1, **kwargs: ((),())

	def setStyle(self, style : str|None=None,line=False,scatter=False,curve=False,heat=False):
		if style is not None:
			self.style = style
		elif line:
			self.style = "line"
		elif scatter:
			self.style = "scatter"
		elif curve:
			self.style = "curve"
		elif heat:
			self.style = "heat"
		else:
			self.style = None
	
	def setErrorStyle(self, style : str|None=None, clone=False, widen=False, shadow=False, whiskers=False, boxplot=False):
		if style is not None:
			self.errorStyle = style
		elif clone:
			self.errorStyle = "clone"
		elif widen:
			self.errorStyle = "widen"
		elif shadow:
			self.errorStyle = "shadow"
		elif whiskers:
			self.errorStyle = "whiskers"
		elif boxplot:
			self.errorStyle = "boxplot"
		else:
			self.errorStyle = None
	
	def showAUC(self, id=-1):
		self.showAreaUnderCurve(id)
	def showAreaUnderCurve(self, id=-1):
		if id < 0:
			self.SHOW_AUC = True
		else:
			self.seriesAUC.add(id)

	def hideAUC(self, id=-1):
		self.hideAreaUnderCurve(id)
	def hideAreaUnderCurve(self, id=-1):
		if id < 0:
			self.SHOW_AUC = False
		else:
			self.seriesAUC.discard(id)
	
	def illustrateHTML(self, *, width : Number=0.8, **kwargs):
		from GeekyGadgets.Semantics.Markups.HTML import Figure, Div
		return Figure(Div(self.illustrateSVG(width=width, **kwargs)))
		
	def illustrateSVG(self, *, width : Number=0.8, **kwargs):
		
		from GeekyGadgets.Semantics.Markups.SVG import Defs, Polyline, Rect, Line
		page = super().illustrateSVG(**kwargs)
		clipFillDefs, clipStrokeDefs, gradientFillDefs, gradientStrokeDefs, *_ = filter(lambda x:isinstance(x, Defs), page.children)

		dX = 100 / self.xRange
		dY = 100 / self.yRange

		for i, maskStroke, maskFill, data in zip(_Iterators.Count(), clipStrokeDefs, clipFillDefs, self.data):

			# Add main plotting style
			XY = [(dX*(x-self.xLim[0]), tuple(100-dY*(y-self.yLim[0]) for y in ySet)) for x, ySet in data if ySet]
			for strokers, fillers in map(lambda f:f(XY, id=i, width=width), [self.drawFunc, self.drawErrorFunc][::-1**(self.errorStyle == "widen")]):
				
				strokers : Iterable[_SVG.SVG]
				fillers : Iterable[_SVG.SVG]
				
				for stroker in strokers:
					if not stroker.hasAttr("stroke"):
						stroker.stroke = "white"
					if not stroker.hasAttr("fill"):
						stroker.fill = "black"
					strokeOpacity = self.getStrokeOpacity(id=i)
					if strokeOpacity < 1 and not stroker.hasAttr("opacity"):
						stroker.opacity = strokeOpacity
					maskStroke.addChild(stroker)
				
				for filler in fillers:
					if not filler.hasAttr("stroke"):
						filler.stroke = "black"
					if not filler.hasAttr("fill"):
						filler.fill = "white"
					fillOpacity = self.getStrokeOpacity(id=i)
					if fillOpacity < 1 and not filler.hasAttr("opacity"):
						filler.opacity = fillOpacity
					maskFill.addChild(filler)
		
		return page
	
class LinePlot(Plot2D):
	
	style : Literal["line"] = "line"
	errorStyle : Literal["clone","widen","shadow","whiskers","boxplot"] = "boxplot"

class ScatterPlot(Plot2D):
	
	style : Literal["scatter"] = "scatter"
	errorStyle : Literal["widen","shadow","whiskers","boxplot"] = "boxplot"

class CurvePlot(Plot2D):
	
	style : Literal["curve"] = "curve"
	errorStyle : Literal["clone","widen","shadow","whiskers","boxplot"] = "shadow"

class BarPlot(Plot1D):
	
	OVERLAY : bool = False

	data : tuple[tuple[_X]]
	
	def __init__(self, *data : Iterable[_X], **graphAttrs):
		if data:
			self.data = tuple(tuple(series) for series in data)
		super().__init__(**graphAttrs)
	
	def illustrateHTML(self, *, width : float=0.95, border : float=0.05, fill : bool=False, **kwargs):
		from GeekyGadgets.Semantics.Markups.HTML import Figure, Div
		return Figure(Div(self.illustrateSVG(width=width, border=border, fill=fill)))
		
	def illustrateSVG(self, *, width : float=0.95, border : float=0.05, fill : bool=False, **kwargs):

		if len(self.data) == 0:
			raise ValueError(f"{self.__class__.__name__} does not have enough data: {self.data =}")

		N = len(self.data)
		M = max(map(len, self.data))

		dH = 100 / self.yRange
		dX = 100 / (2*M)

		if self.OVERLAY:
			positions = [list(_Iterators.Spaced((1-width) * dX, 100 - dX*(1+width), M))] * N
		else:
			groups = list(_Iterators.Spaced((1-width) * dX, 100 - dX*(1+width), M))
			positions = [list(map((i*width*2*dX/N).__add__, groups)) for i in range(N)]
			dX /= N
		
		from GeekyGadgets.Semantics.Markups.SVG import Rect, Defs

		page = super().illustrateSVG(**kwargs)

		clipFillDefs, clipStrokeDefs, gradientFillDefs, gradientStrokeDefs, *_ = filter(lambda x:isinstance(x, Defs), page.children)

		for i, (series, maskFill, maskStroke) in enumerate(zip(self.data, clipFillDefs, clipStrokeDefs)):
			for j, value in enumerate(series):
				blockFill = Rect(
					x=positions[i][j]+border*width*dX,
					y=100-(height := dH*(value-self.yLim[0]))+border*width*dX,
					width=(1-border)*width*2*dX,
					height=height,
					strokeWidth=border*width*2*dX
				)
				blockStroke = blockFill.copy()

				blockFill.fill = "#202020"
				blockStroke.stroke = "white"

				maskFill.addChild(blockFill)
				maskStroke.addChild(blockStroke)
		
		return page

class BoxPlot(Plot1D):
	
	SHOW_LEGEND : bool = False
	data : tuple[tuple[_X]]

	xLim : tuple = (0, 100)
	xTicks : list[Number] = _Classy.CachedDefault["data"](lambda self: list(_Iterators.Spaced(0, 100, 1+2*len(self.data)))[1:-1:2])
	
	def __init__(self, *data : Iterable[_X], **graphAttrs):
		self.data = tuple(tuple(series) for series in data)
		super().__init__(**graphAttrs)
	
	
	def illustrateHTML(self, *, width : float|None=None, **kwargs):
		from GeekyGadgets.Semantics.Markups.HTML import Figure, Div
		return Figure(Div(self.illustrateSVG(width=width, **kwargs)))
		
	def illustrateSVG(self, *, width : float|None=None, **kwargs):

		if min(map(len, self.data)) < 5:
			raise ValueError(f"{self.__class__.__name__} does not have enough data: {self.data =}")

		N = len(self.data)

		width = width or min(0.2, 0.5/N)
		dH = 100 / self.yRange
		cH = -dH * self.yLim[0]
		dX = 100 / (2*N)

		positions = list(_Iterators.Spaced(0, 100, 1+2*N))[1:-1:2]
		
		LINE_WIDTH = 0.25

		from GeekyGadgets.Semantics.Markups.SVG import Rect, Line, Defs

		page = super().illustrateSVG(**kwargs)
		clipFillDefs, clipStrokeDefs, gradientFillDefs, gradientStrokeDefs, *_ = filter(lambda x:isinstance(x, Defs), page.children)

		for i, (maskStroke, maskFill, Y) in enumerate(zip(clipStrokeDefs, clipFillDefs, (tuple(100-(dH*q+cH) for q in _StatFuncs.quantiles(data)) for data in self.data))):
			maskStroke.addChild(Line(
				x1=positions[i]-width*dX, y1=Y[0],
				x2=positions[i]+width*dX, y2=Y[0],
				strokeWidth=LINE_WIDTH, stroke="white"
			))
			maskStroke.addChild(Line(
				x1=positions[i], y1=Y[0],
				x2=positions[i], y2=Y[1],
				strokeWidth=LINE_WIDTH, stroke="white",
				strokeDasharray=f"{LINE_WIDTH},{LINE_WIDTH}"
			))
			box2Stroke = Rect(
				x=positions[i]-width*dX, y=Y[2],
				width=2*width*dX, height=abs(Y[2] - Y[1]),
				fill="none", strokeWidth=LINE_WIDTH, stroke="white"
			)
			box3Stroke = box2Stroke.copy()
			box3Stroke.y = Y[3]
			box3Stroke.height = abs(Y[3] - Y[2])

			maskStroke.addChild(box2Stroke)
			maskStroke.addChild(box3Stroke)
			
			box2Fill = box2Stroke.copy()
			box3Fill = box3Stroke.copy()

			box2Fill.fill = box3Fill.fill = "#202020"
			box2Fill.stroke = box3Fill.stroke = "none"

			maskFill.addChild(box2Fill)
			maskFill.addChild(box3Fill)

			maskStroke.addChild(Line(
				x1=positions[i], y1=Y[3],
				x2=positions[i], y2=Y[4],
				strokeWidth=LINE_WIDTH, stroke="white",
				strokeDasharray=f"{LINE_WIDTH},{LINE_WIDTH}"
			))
			maskStroke.addChild(Line(
				x1=positions[i]-width*dX, y1=Y[4],
				x2=positions[i]+width*dX, y2=Y[4],
				strokeWidth=LINE_WIDTH, stroke="white"
			))
		
		return page

class Histogram(BarPlot):
	
	OVERLAY : bool = True

	_data : tuple[_X]

	data : list[list[int]]
	bins : int = 10
	quantiles = _Classy.Default(lambda self: list(map(_StatFuncs.quantiles, self._data)))

	xLim : tuple[_X,_X] = _Classy.Default(lambda self: (min(map(min, self._data)), max(map(max, self._data))))
	xTicks = _Classy.Default(lambda self: sorted(_Iterators.Chain(*self.quantiles)))
	@_Classy.Default
	def xLabels(self) -> tuple[str]:
		return tuple(_Formatting.floatEmphasize(tick, *self.xLim, length=self.significantDigits) for tick in self.xTicks)
	@_Classy.CachedDefault["_data"]
	def xLabelOffsets(self) -> list[float]:
		return [x[0] for x in sorted(
			(
				(1+2*(i%3), q)
				for i, quants in enumerate(self.quantiles)
					for q in quants
			),
			key=lambda x:x[1]
		)]
	@_Classy.CachedDefault["_data"]
	def xLabelsJustify(self) -> list[str]:
		return [x[2] for x in sorted(
			(
				(1+2*(i%3), q, justify)
				for i, quants in enumerate(self.quantiles)
					for q, justify in zip(quants, ("end","end","middle","start","start"))
			),
			key=lambda x:x[1]
		)]

	
	def __init__(self, *data : Iterable[_X], bins : int|Callable[[list[_X]],Number]=Binning.sturges, **graphAttrs):
		self._data = tuple(map(sorted, data))
		if isinstance(bins, int):
			self.bins = bins
		elif isinstance(bins, Callable):
			self.bins = round(bins(_Iterators.Chain(*self._data)))
		else:
			raise TypeError(f"`bins` must be either an integer or a function that takes the original data as input and outputs the number of bins to use.")
		
		super().__init__(**graphAttrs)
	
	def illustrateSVG(self, *, width: float = 0.95, border: float = 0.05, fill: bool = False, **kwargs):
		from GeekyGadgets.Semantics.Markups.SVG import G as Group, Line, Text
		page = super().illustrateSVG(width=width, border=border, fill=fill, **kwargs)
		if len(self._data) > 1:
			ticks = sorted(
				(
					(i, q)
					for i, quants in enumerate(self.quantiles)
						for q in quants
				),
				key=lambda x:(-self.xLabelOffsets[x[0]], x[1])
			)
			for child in page.children:
				if getattr(child, "name", None) == "xAxis":
					xAxis = child
					break
			else:
				return page
			
			for (i, quant), group in zip(ticks, filter(lambda x:isinstance(x, Group), xAxis)):
				if group.name == quant:
					for child in group.children:
						if isinstance(child, Line):
							child.stroke = f"url(#{self.gradientStrokeIdList[i]})"
						if isinstance(child, Text):
							child.fill = f"url(#{self.gradientStrokeIdList[i]})"
							child.stroke = "var(--PRIMARY-COLOR)"

		return page
	
	@_Classy.Default["bins"]
	def data(self) -> list[list[int]]:
		vMin, vMax = self.xLim
		
		histBins = [
			[
				sum(1 for value in data if xLeft <= value < xRight)
				for xLeft, xRight in _Iterators.Echo(_Iterators.Spaced(vMin, vMax, self.bins+1))
			]
			for data in self._data
		]
		for i, data in enumerate(self._data):
			histBins[i][-1] += sum(1 for v in data if v == vMax)
		return histBins
