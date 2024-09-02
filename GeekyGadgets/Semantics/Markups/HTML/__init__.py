

from GeekyGadgets.Semantics.Markups import Globals as _Globals

class HTML(_Globals.HasCSS, _Globals.Markup):
	
	_singletons = [
		"area",
		"base",
		"br",
		"col",
		"command",
		"embed",
		"hr",
		"img",
		"input",
		"keygen",
		"link",
		"meta",
		"param",
		"source",
		"track",
		"wbr",
	]

	def compile(self):
		return "<!doctype html>\n"+str(self)

class Html(HTML): pass

# <!--...--> 	Defines a comment
# <!DOCTYPE>  	Defines the document type
class A(HTML): pass
class Abbr(HTML): pass
class Acronym(HTML): pass
class Address(HTML): pass
class Applet(HTML): pass
class Area(HTML): pass
class Article(HTML): pass
class Aside(HTML): pass
class Audio(HTML): pass
class B(HTML): pass
class Base(HTML): pass
class Basefont(HTML): pass
class Bdi(HTML): pass
class Bdo(HTML): pass
class Big(HTML): pass
class Blockquote(HTML): pass
class Body(HTML): pass
class Br(HTML): pass
class Button(HTML): pass
class Canvas(HTML): pass
class Caption(HTML): pass
class Center(HTML): pass
class Cite(HTML): pass
class Code(HTML): pass
class Col(HTML): pass
class Colgroup(HTML): pass
class Data(HTML): pass
class Datalist(HTML): pass
class Dd(HTML): pass
class Del(HTML): pass
class Details(HTML): pass
class Dfn(HTML): pass
class Dialog(HTML): pass
class Dir(HTML): pass
class Div(HTML): pass
class Dl(HTML): pass
class Dt(HTML): pass
class Em(HTML): pass
class Embed(HTML): pass
class Fieldset(HTML): pass
class Figcaption(HTML): pass
class Figure(HTML): pass
class Font(HTML): pass
class Footer(HTML): pass
class Form(HTML): pass
class Frame(HTML): pass
class Frameset(HTML): pass
class H1(HTML): pass
class H2(HTML): pass
class H3(HTML): pass
class H4(HTML): pass
class H5(HTML): pass
class HN(HTML):
	_classes = {}

	def __new__(cls, N : int):
		
		if N not in cls._classes:
			cls._classes[N] = HTML.__class__(f"H{N}", (HTML,), {})
		
		return cls._classes[N]
class Head(HTML): pass
class Header(HTML): pass
class Hgroup(HTML): pass
class Hr(_Globals.Singlet, HTML): pass
class I(HTML): pass
class Iframe(HTML): pass
class Img(_Globals.Singlet, HTML): pass
class Input(HTML): pass
class Ins(HTML): pass
class Kbd(HTML): pass
class Label(HTML): pass
class Legend(HTML): pass
class Li(HTML): pass
class Link(HTML): pass
class Main(HTML): pass
class Map(HTML): pass
class Mark(HTML): pass
class Menu(HTML): pass
class Meta(HTML): pass
class Meter(HTML): pass
class Nav(HTML): pass
class Noframes(HTML): pass
class Noscript(HTML): pass
class Object(HTML): pass
class Ol(HTML): pass
class Optgroup(HTML): pass
class Option(HTML): pass
class Output(HTML): pass
class P(HTML): pass
class Param(HTML): pass
class Picture(HTML): pass
class Pre(HTML): pass
class Progress(HTML): pass
class Q(HTML): pass
class Rp(HTML): pass
class Rt(HTML): pass
class Ruby(HTML): pass
class S(HTML): pass
class Samp(HTML): pass
class Script(HTML):
	def __init__(self: "_Globals._TAG", /, *content: "_Globals.AnyStr | _Globals._TAG", **attributes: "_Globals.AnyStr | int | float | bool") -> "_Globals.NoneType":
		if attributes.pop("defer", False):
			self.end = "defer"
		if attributes.pop("async", False):
			self.end = "async"
		super().__init__(*content, **attributes)
class Search(HTML): pass
class Section(HTML): pass
class Select(HTML): pass
class Small(HTML): pass
class Source(HTML): pass
class Span(HTML): pass
class Strike(HTML): pass
class Strong(HTML): pass
class Style(HTML): pass
class Sub(HTML): pass
class Summary(HTML): pass
class Sup(HTML): pass
from GeekyGadgets.Semantics.Markups.SVG import Svg # class Svg(HTML): pass
class Table(HTML): pass
class Tbody(HTML): pass
class Td(HTML): pass
class Template(HTML): pass
class Textarea(HTML): pass
class Tfoot(HTML): pass
class Th(HTML): pass
class Thead(HTML): pass
class Time(HTML): pass
class Title(HTML): pass
class Tr(HTML): pass
class Track(HTML): pass
class Tt(HTML): pass
class U(HTML): pass
class Ul(HTML): pass
class Var(HTML): pass
class Video(_Globals.Singlet, HTML): pass
class Wbr(HTML): pass

import GeekyGadgets.Semantics.Markups.HTML.Magic as Magic