
import GeekyGadgets.Illustrative.Globals as _GL

import GeekyGadgets.Iterators.Walkers as _Walkers
import GeekyGadgets.Colors.General as _Colors
import GeekyGadgets.Formatting.Functions as _Formatting
import GeekyGadgets.Illustrative.Graphs as _Graphs
import GeekyGadgets.Illustrative.Plots as _Plots
import GeekyGadgets.Semantics.Markups as _Markups
import GeekyGadgets.Semantics.Markups.HTML as _HTML
import GeekyGadgets.Semantics.Markups.SVG as _SVG
import GeekyGadgets.Semantics.Markdown as _Markdown
import GeekyGadgets.Classy as _Classy
import GeekyGadgets.Functions as _Funcs
import GeekyGadgets.Math.Stats.Functions as _StatFuncs
import GeekyGadgets.SpecialTypes as _SPT

_PAGE_BACKGROUND_PATTERN = _GL.re.compile(r"(?<=--PAGE-BACKGROUND : ).+")

class IllustrateDocument(_GL.Illustrator):
	
	HTML : _SPT.NameSpace = _SPT.NameSpace(
		CSS=open(_GL.os.path.join(_GL.os.path.split(__file__)[0], "CSS", "IllustrateDocument.css"), "r").read()
	)
	header : _GL.Iterable[_Markups.Markup|_Markdown.Markdown] = []
	frontPage : _GL.Iterable[_Markups.Markup|_Markdown.Markdown] = []
	@property
	def favicon(self) -> _HTML.Link:
		import urllib.parse
		
		return _HTML.Link(
			rel="icon",
			type="image/svg+xml",
			href="data:image/svg+xml,"+ urllib.parse.quote(_SVG.Svg(
				_SVG.Rect(x=4, y=1, height=14, width=8, fill="transparent", stroke="#a0a0a0", strokeWidth=1),
				viewBox="0 0 16 16"
			).compile()
		))

	title : str = "Document"
	content : list[_GL.Illustrator|_Markups.Markup|_Markdown.Markdown]

	def __init__(self, *sections : _GL.Illustrator|_Markups.Markup|_Markdown.Markdown, title : str="Illustration") -> None:
		self.content = list(sections)
		self.title = title

	def illustrateHTML(self, *, file : _GL.BinaryIO=None, background : _Colors.Color|None=None, **kwargs) -> _Markups.Markup:
		
		page = _HTML.Html(
			head := _HTML.Head(
				_HTML.Title(self.title),
				self.favicon,
				_HTML.Meta(property="article:published_time", content=_Formatting.dateFormat(), dataRh="true"),
				_HTML.Style(
					_PAGE_BACKGROUND_PATTERN.sub(background, _GL.BASE_CSS)
					if background is not None
					else _GL.BASE_CSS
				),
				*(
					_HTML.Style(string)
					for string in set(
						obj.HTML.CSS
						for obj in _Walkers.DepthFirst([self],
											  cond=lambda x: hasattr(x, "HTML") and "CSS" in x.HTML,
											  recurseCond=lambda x: isinstance(x, _GL.Iterable) and isinstance(x, (_GL.Illustrator, list, tuple, set, _GL.Iterator)))
					)
				),
				*(
					_HTML.Script(string, type="text/javascript")
					for string in set(
						obj.HTML.JS
						for obj in _Walkers.DepthFirst([self],
											  cond=lambda x: hasattr(x, "HTML") and "JS" in x.HTML,
											  recurseCond=lambda x: isinstance(x, _GL.Iterable) and isinstance(x, (_GL.Illustrator, list, tuple, set, _GL.Iterator)))
					)
				),
			),
			body := _HTML.Body(
				main := _HTML.Main(
					*(_HTML.Section(
						*(sectionContent.illustrateHTML(**kwargs),)
						if isinstance(sectionContent, _GL.Illustrator)
						else (sectionContent,) if not isinstance(sectionContent, (list, tuple, set, _GL.Iterator))
						else (content.illustrateHTML(**kwargs) if isinstance(content, _GL.Illustrator) else content for content in sectionContent),
						Class="GeekyIllustration secondary"
					)
					for sectionContent in self.content
					),
					Class="GeekyIllustration"
				),
				Class="GeekyIllustration"
			),
			Class="GeekyIllustration"
		)
		
		if self.frontPage:
			main.addChild(0, _HTML.Section(
				*(
					item.illustrateHTML(**kwargs)
					if isinstance(item, _GL.Illustrator)
					else item
					for item in self.frontPage
				),
				Class="FrontPage secondary"
			))
		
		if self.header:
			body.addChild(0, _HTML.Header(*self.header, Class="FixedHeader secondary"))
		
		if file is not None:
			file.write(page.compile())
			file.flush()
		return page
	
	def __iter__(self):
		if self.frontPage:
			yield self.frontPage
		yield from iter(self.content)

class IllustrateFigure(IllustrateDocument):
	
	HTML : _SPT.NameSpace = _SPT.NameSpace(
		CSS=IllustrateDocument.HTML.CSS + "\n" + open(_GL.os.path.join(_GL.os.path.split(__file__)[0], "CSS", "IllustrateFigure.css"), "r").read()
	)
	header : None = None
	frontPage : None = None
	@property
	def favicon(self):
		import urllib.parse

		if not self.content:
			pass
		elif isinstance(self.content[0], (_Graphs.Graph, _Plots.Plot)):
			return _HTML.Link(
				rel="icon",
				type="image/svg+xml",
				href=f"data:image/svg+xml,{urllib.parse.quote(self.content[0].illustrateSVG().compile())}"
			)
		elif self.content and isinstance(self.content[0], IllustrativeCollection):
			return _HTML.Link(
				rel="icon",
				type="image/svg+xml",
				href="data:image/svg+xml,"+ urllib.parse.quote(_SVG.Svg(
					_SVG.Rect(x=0, y=0, height=7, width=7, fill="#404040", stroke="#a0a0a0", strokeWidth=0.5),
					_SVG.Rect(x=10, y=0, height=7, width=7, fill="#404040", stroke="#a0a0a0", strokeWidth=0.5),
					_SVG.Rect(x=10, y=10, height=7, width=7, fill="#404040", stroke="#a0a0a0", strokeWidth=0.5),
					_SVG.Rect(x=0, y=10, height=7, width=7, fill="#404040", stroke="#a0a0a0", strokeWidth=0.5),
					viewBox="0 0 16 16"
				).compile()
			))
		return _HTML.Link(
			rel="icon",
			type="image/svg+xml",
			href="data:image/svg+xml,"+ urllib.parse.quote(_SVG.Svg(
				_SVG.Rect(x=1, y=1, height=14, width=14, fill="transparent", stroke="#a0a0a0", strokeWidth=1),
				viewBox="0 0 16 16"
			).compile()
		))

	title : str = "Figure"
	content : list[_GL.Illustrator|_Markups.Markup|_Markdown.Markdown]

	@_GL.overload
	def __init__(self, iterable : _GL.Iterable[_GL.Illustrator|_Markups.Markup|_Markdown.Markdown], *, title : str="Figure") -> None: ...
	@_GL.overload
	def __init__(self, *items : _GL.Illustrator|_Markups.Markup|_Markdown.Markdown, title : str="Figure") -> None: ...
	def __init__(self, iterable : _GL.Iterable[_GL.Illustrator|_Markups.Markup|_Markdown.Markdown]|_GL.Illustrator|_Markups.Markup|_Markdown.Markdown, *items : _GL.Illustrator|_Markups.Markup|_Markdown.Markdown, title : str="Figure") -> None:
		
		if not items and _Funcs.isType(iterable, _GL.Iterable[_GL.Illustrator|_Markups.Markup|_Markdown.Markdown]):
			self.title = title
			self.content = [IllustrativeCollection(iterable)]
		elif isinstance(iterable, IllustrativeCollection):
			self.title = iterable.title if title is None else title
			self.content = [iterable]
		elif isinstance(iterable, (_GL.Illustrator, _Markups.Markup, _Markdown.Markdown)) and all(isinstance(x, (_GL.Illustrator, _Markups.Markup, _Markdown.Markdown)) for x in items):
			if not items and title == "Figure":
				self.title = getattr(iterable, "title", getattr(iterable, "name", "Figure"))
			else:
				self.title = title
			self.content = [(iterable, *items)]
		else:
			raise ValueError(f"Items in a Figure must be a subclass to one of: `Illustrator_Markups.Markup_Markdown.Markdown`")

	def illustrateHTML(self, *, file : _GL.BinaryIO=None, background : _Colors.Color|None=None, **kwargs) -> _Markups.Markup:
		
		page = super().illustrateHTML(**kwargs, background=background)

		if self.content and isinstance(self.content[0], _GL.Iterable) and len(self.content[0]) > 1:
			fs = _StatFuncs.factors(len(self.content[0]))
			if fs:
				large = fs[0]
				small = len(self.content[0]) // large
			else:
				large = _StatFuncs.ceil(_StatFuncs.sqrt(len(self.content[0])))
				small = 1 + len(self.content[0]) // large
			page.children[0].addChild(_HTML.Style(f"@media screen and (orientation : landscape) {{section.MonoFigure {{aspect-ratio : {large} / {small};}}}} @media screen and (orientation : portrait) {{section.MonoFigure {{aspect-ratio : {small} / {large};}}}}"))

		main = page.children[1].children[0] if isinstance(page.children[1].children[0], _HTML.Main) else page.children[1].children[1]
		
		classes = set(filter(None, getattr(main.children[0], "Class", "").split()))
		classes.remove("secondary")
		classes.add("MonoFigure")
		
		main.children[0].Class = " ".join(classes)

		if file is not None:
			file.write(page.compile())
			file.flush()
		return page

class IllustrativeCollection(_GL.Illustrator):

	@_Classy.Default
	def HTML(self) -> _SPT.NameSpace:
		return _SPT.NameSpace(
			JS="\n".join({
				open(_GL.os.path.join(_GL.os.path.split(__file__)[0], "JS", "IllustrateCollection.js"), "r").read()
			} | {obj.HTML.JS for obj in self.content if hasattr(obj, "HTML") and "JS" in obj.HTML}),
			CSS="\n".join({
				open(_GL.os.path.join(_GL.os.path.split(__file__)[0], "CSS", "IllustrateCollection.css"), "r").read()
			} | {obj.HTML.CSS for obj in self.content if hasattr(obj, "HTML") and "CSS" in obj.HTML})
		)
	
	content : list

	title : str|None
	description : str|None
	id : str = _Classy.CachedDefault(lambda self: f"IllustrativeCollection_{id(self):x}")
	Class : str = _Classy.Default(lambda self: "IllustrativeCollection")

	@_GL.overload
	def __init__(self, iterable : _GL.Iterable[_GL.Illustrator], *, title : str="Collection Viewer", description : str|None=None, id : str|None=None) -> None: ...
	@_GL.overload
	def __init__(self, *items : _GL.Illustrator, title : str="Collection Viewer", description : str|None=None, id : str|None=None) -> None: ...
	def __init__(self, iterable : _GL.Iterable[_GL.Illustrator]|_GL.Illustrator, *items : _GL.Illustrator, title : str="Collection Viewer", description : str|None=None, id : str|None=None) -> None:
		if not items and isinstance(iterable, _GL.Iterable):
			self.content = list(iterable)
		else:
			self.content = list((iterable, ) + items)
		self.title = title
		self.description = description
		if id is not None:
			self.id = id

	def illustrateHTML(self, *, file : _GL.BinaryIO=None, **kwargs) -> _Markups.Markup:
		
		if file is not None:
			IllustrateFigure(self).illustrateHTML(file=file, **kwargs)

		page = (fig := _HTML.Div(
			_HTML.Div( # .SvgContainer
				_HTML.Div( # Box with inset shadow on its ::after
					_HTML.Div( # Box with overflow : hidden;
						_HTML.Div( # centrally position aspect-ratio : 1/1;
							showIllustration := _Funcs.first(
								filter(lambda x: isinstance(x, _GL.Illustrator), self.content)
							).illustrateHTML(**kwargs)
						)
					)
				),
				Class="SvgContainer primary"
			),
			aside := _HTML.Aside(
				header := _HTML.Header(
					_HTML.H1(self.title if self.title is not None else ""),
					_HTML.P(self.description if self.description is not None else "")
				),
				asideContainer := _HTML.Nav(),
				Class="secondary"
			),
			Class="GeekyIllustration CollectionViewer",
			name=self.id
		))
		hide = True
		for content in self.content:
			if not isinstance(content, _GL.Illustrator):
				asideContainer.addChild(_HTML.Div(_HTML.Div(_HTML.Div(content))))
			elif hide:
				asideContainer.addChild(_HTML.Div(_HTML.Div(_HTML.Div(showIllustration, Class="showing", onclick="expandGraph(this)"))))
				hide = False
			else:
				asideContainer.addChild(_HTML.Div(_HTML.Div(_HTML.Div(content.illustrateHTML(**kwargs), onclick="expandGraph(this)"))))

		return page
	
	