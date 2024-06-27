
from GeekyGadgets.Semantics.Globals import *

class Markup(ABC, Semantics):

	_name : str

	parent : "Markup"
	before : "Markup" = property(lambda self: self.parent.content[self.parent.content.index(self)-1] if 1 < self.parent.content.index(self) else None)
	after : "Markup" = property(lambda self: self.parent.content[self.parent.content.index(self)+1] if self.parent.content.index(self) < len(self.parent.content)-1 else None)
	siblings : "tuple[Markup]" = Default["parent.content"](lambda self: tuple(filter(lambda x:isinstance(x, Markup), self.parent.content)))
	children : "tuple[Markup]" = Default["content"](lambda self: tuple(filter(lambda x:isinstance(x, Markup), self.content)))

	content : "list[Markup|AnyStr]" = Default(lambda self:[])
	attributes : dict[str,Any] = Default(lambda self:Attributes())

	def __init__(self : "_TAG", _name : str, /, *content : "AnyStr|Markup", **attributes : AnyStr|int|float|bool) -> None:
		from GeekyGadgets.Semantics.Rulesets.CSS import CascadingStyleSheet
		self._name = _name
		self.content = list(content)
		dict.update(self.attributes, {name:value if name != "style" else CascadingStyleSheet("", value) for name, value in attributes.items()})

	def __iter__(self : "Markup") -> "Generator[Markup|AnyStr,None,None]":
		for element in self.content:
			yield element

	def __str__(self : "Markup") -> str:
		sep = f"\n{SyntaxContext.indentation}" if not SyntaxContext.compact else ""
		return f"<{self._name} {self.attributes}>{''.join(map(lambda x: sep+str(x) if isinstance(x, Markup) else str(x), self))}{sep if isinstance(last(self), Markup) else ''}</{self.name}>"
	
	def __repr__(self : "Markup") -> str:
		return repr(str(self))
	
	def __hash__(self : "Markup") -> int:
		return hash(str(self))
	
	def __eq__(self, other : Hashable) -> bool:
		return hasattr(other, "__hash__") and hash(self) == hash(other)

	@overload
	def syntax(self, *, compact : bool=False, stringDelimiter : str, indentation : str) -> SyntaxContext: ...
	def syntax(self, **kwargs) -> SyntaxContext:
		return SyntaxContext(**kwargs)
	
	@overload
	def addChild(self : "Markup", child : "Markup", /) -> "Markup": ...
	@overload
	def addChild(self : "Markup", index : int, child : "Markup", /) -> "Markup": ...
	def addChild(self : "Markup", *args : "int|Markup") -> "Markup":
		if len(args) == 2:
			index, child = args
			self.content.insert(index, child)
		elif len(args) == 1:
			child, *_ = args
			self.content.append(child)
		else:
			raise ValueError(f"Markup.addChild expected 3 arguments, but got {1+len(args)}.")
		
		if isinstance(child, Markup):
			child.parent = self
		return self
	
	def addBefore(self : "Markup", tag : "_TAG") -> "Markup":
		self.parent.addChild(self.parent.content.index(self), tag)
		if isinstance(tag, Markup):
			tag.parent = self.parent
		return self
	
	def addAfter(self : "Markup", tag : "_TAG") -> "Markup":
		self.parent.addChild(self.parent.content.index(self)+1, tag)
		if isinstance(tag, Markup):
			tag.parent = self.parent
		return self
	
	@overload
	def removeChild(self, child : "Markup", /): ...
	@overload
	def removeChild(self, index : "int", /): ...
	def removeChild(self, arg : "Markup"):
		if isinstance(arg, int):
			self.content.remove(self.children[arg])
		elif isinstance(arg, Markup):
			self.content.remove(arg)

	@overload
	def removeContent(self, content : "Markup|AnyStr", /): ...
	@overload
	def removeContent(self, index : "int", /): ...
	def removeContent(self, arg : "Markup", /):
		if isinstance(arg, int):
			self.content.pop(arg)
		elif isinstance(arg, (Markup, AnyStr)):
			self.content.remove(arg)
	
	@overload
	def removeSibling(self, sibling : "Markup", /): ...
	@overload
	def removeSibling(self, index : "int", /): ...
	def removeSibling(self, arg : "Markup", /):
		if isinstance(arg, int):
			self.parent.content.remove(self.siblings[arg])
		elif isinstance(arg, Markup):
			self.parent.content.remove(arg)

class Document(Markup): ...
_TAG = TypeVar("_TAG", bound=Markup)

class DeclaredTag(Markup):
	def __init__(self: _TAG, /, *content: AnyStr | _TAG, **attributes: AnyStr | int | float | bool) -> None:
		super().__init__(SnakeCase(self.__class__.__name__), *content, **attributes)