
from GeekyGadgets.Semantics.Globals import *

import GeekyGadgets.Classy as _Classy
import GeekyGadgets.Formatting.Case as _Case

_NOT_SET = object()

class Markup(Semantics, Subscriptable):

	_CLOSED = False
	_SUBCLASS_LOOKUP : dict
	_tagName : str
	_explicitAttributeNames = []
	_singletons = []
	
	end = ""

	parent : "Markup" = None
	before : "Markup" = property(lambda self: self.parent.content[self.parent.content.index(self)-1] if 1 < self.parent.content.index(self) else None)
	after : "Markup" = property(lambda self: self.parent.content[self.parent.content.index(self)+1] if self.parent.content.index(self) < len(self.parent.content)-1 else None)
	siblings : "tuple[Markup]" = _Classy.Default(lambda self: tuple(filter(lambda x:isinstance(x, Markup), self.parent.content)) if isinstance(self.parent, Markup) else ())
	children : "tuple[Markup]" = _Classy.Default(lambda self: tuple(filter(lambda x:isinstance(x, Markup), self.content)))

	content : "list[Markup|AnyStr]" = None
	attributes : Attributes[str,Any] = cached_property(lambda self: Attributes())

	def __init__(self : "_TAG", *content : "AnyStr|Markup", ATTRS : dict|Attributes={}, **attributes : AnyStr|int|float|bool) -> None:
		"""ATTRS can be used when (an) attribute(s) are not to be named using camelCase, as attributes are otherwise 
		converted to camelCase."""
		SETATTR(self, "content", list(content))
		for name, value in ATTRS.items():
			self.attributes[name] = value
		
		for name, value in attributes.items():
			if name in self._explicitAttributeNames:
				self.attributes[name] = value
			else:
				setattr(self.attributes, name, value)
	
	def __init_subclass__(cls, tagName=None, **kwargs) -> None:
		if tagName is not None:
			cls._tagName = tagName
		elif any(Markup in base.__bases__ for base in cls.__bases__):
			cls._tagName = _Case.CamelCase(cls.__name__)
		
		if Markup in cls.__bases__:
			cls._SUBCLASS_LOOKUP = {}
		elif any(Markup in base.__bases__ for base in cls.__bases__):
			for base in cls.__bases__:
				if Markup in base.__bases__:
					base._SUBCLASS_LOOKUP[cls._tagName] = cls
					break
		return super().__init_subclass__(**kwargs)
	
	def __iter__(self : "Markup") -> "Generator[Markup|AnyStr,None,None]":
		for element in self.content:
			yield element

	def __str__(self : "Markup") -> str:
		if self._CLOSED:
			return f"<{self._tagName}{' '*bool(self.attributes)}{self.attributes}{' '*bool(self.end)}{self.end}/>"
		elif len(self.content) == 1 and isinstance(self.content[0], str):
			return f"<{self._tagName}{' '*bool(self.attributes)}{self.attributes}{' '*bool(self.end)}{self.end}>{self.content[0]}</{self._tagName}>"
		elif not self.content:
			return f"<{self._tagName}{' '*bool(self.attributes)}{self.attributes}{' '*bool(self.end)}{self.end}></{self._tagName}>"
		else:
			ret = [f"<{self._tagName}{' '*bool(self.attributes)}{self.attributes}{' '*bool(self.end)}{self.end}>"]
			opened = [(self._tagName, iter(self))]
			
			if not SyntaxContext.compact:
				depth = 1
				indent = SyntaxContext.indentation
				while opened:
					for child in opened[-1][1]:
						if isinstance(child, Markup):
							if child._tagName in child._singletons:
								ret.append(f"{indent*depth}<{child._tagName}{' '*bool(child.attributes)}{child.attributes}{' '*bool(child.end)}{child.end}>")
							elif child._CLOSED or isinstance(child, Singlet):
								ret.append(f"{indent*depth}<{child._tagName}{' '*bool(child.attributes)}{child.attributes}{' '*bool(child.end)}{child.end}/>")
							elif len(child.content) == 1 and isinstance(child.content[0], str):
								ret.append(f"{indent*depth}<{child._tagName}{' '*bool(child.attributes)}{child.attributes}{' '*bool(child.end)}{child.end}>{child.content[0]}</{child._tagName}>")
							else:
								ret.append(f"{indent*depth}<{child._tagName}{' '*bool(child.attributes)}{child.attributes}{' '*bool(child.end)}{child.end}>")
								opened.append((child._tagName, iter(child)))
								depth += 1
								break
						else:
							ret.append(f"{indent*depth}{child}")
					else:
						name, _ = opened.pop()
						depth -= 1
						ret.append(f"{indent*depth}</{name}>")
			else:
				while opened:
					for child in opened[-1][1]:
						if isinstance(child, Markup):
							if child._tagName in child._singletons:
								ret.append(f"<{child._tagName}{' '*bool(child.attributes)}{child.attributes}{' '*bool(child.end)}{child.end}>")
							elif child._CLOSED or isinstance(child, Singlet):
								ret.append(f"<{child._tagName}{' '*bool(child.attributes)}{child.attributes}{' '*bool(child.end)}{child.end}/>")
							elif len(child.content) == 1 and isinstance(child.content[0], str):
								ret.append(f"<{child._tagName}{' '*bool(child.attributes)}{child.attributes}{' '*bool(child.end)}{child.end}>{child.content[0]}</{child._tagName}>")
							else:
								ret.append(f"<{child._tagName}{' '*bool(child.attributes)}{child.attributes}{' '*bool(child.end)}{child.end}>")
								opened.append((child._tagName, iter(child)))
								break
						else:
							ret.append(str(child))
					else:
						name, _ = opened.pop()
						ret.append(f"</{name}>")
			return ("\n" if not SyntaxContext.compact else "").join(ret)
	
	def __repr__(self : "Markup") -> str:
		if self._CLOSED:
			return f"<{self._tagName}{' '*bool(self.attributes)}{self.attributes}{' '*bool(self.end)}{self.end}/>"
		elif self.content:
			return f"<{self._tagName}{' '*bool(self.attributes)}{self.attributes}{' '*bool(self.end)}{self.end}> ... </{self._tagName}>"
		else:
			return f"<{self._tagName}{' '*bool(self.attributes)}{self.attributes}{' '*bool(self.end)}{self.end}></{self._tagName}>"
	
	def __hash__(self : "Markup") -> int:
		return hash(str(self))
	
	def __eq__(self, other : Hashable) -> bool:
		return hasattr(other, "__hash__") and hash(self) == hash(other)

	def __setattr__(self, name: str, value : Any) -> Any:
		if hasattr(self.__class__, name) or name.startswith("_"):
			SETATTR(self, name, value)
		elif name in self._explicitAttributeNames:
			self.setAttr(name, value)
		else:
			return setattr(self.attributes, name, value)
	
	def __getattr__(self, name: str) -> Any:
		return self.getAttr(name)
	
	def getAttr(self, name: str, _default=_NOT_SET) -> Any:
		if _default is not _NOT_SET:
			return getattr(self.attributes, name, _default)
		try:
			return getattr(self.attributes, name)
		except KeyError:
			raise AttributeError(f"{self.__class__.__name__!r} object has no attribute {name!r}.")
	
	def setAttr(self, name: str, value: Any) -> None:
		self.attributes[name] = value
	
	def hasAttr(self, name: str) -> None:
		return name in self.attributes

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
			SETATTR(child, "parent", self)
		return self
	
	def addBefore(self : "Markup", tag : "_TAG") -> "Markup":
		self.parent.addChild(self.parent.content.index(self), tag)
		if isinstance(tag, Markup):
			SETATTR(tag, "parent", self.parent)
		return self
	
	def addAfter(self : "Markup", tag : "_TAG") -> "Markup":
		self.parent.addChild(self.parent.content.index(self)+1, tag)
		if isinstance(tag, Markup):
			SETATTR(tag, "parent", self.parent)
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
	
	def clearContent(self) -> int:
		"""Removes all items within the elements content until none can be removed. Returns the number of items 
		remaining in the elements content. Thus, returns 0 if all content was successfully removed."""
		try:
			while self.content.pop(): pass
		except:
			pass
		finally:
			return len(self.content)
	
	@overload
	def removeSibling(self, sibling : "Markup", /): ...
	@overload
	def removeSibling(self, index : "int", /): ...
	def removeSibling(self, arg : "Markup", /):
		if isinstance(arg, int):
			self.parent.content.remove(self.siblings[arg])
		elif isinstance(arg, Markup):
			self.parent.content.remove(arg)
	
	def compile(self):
		return str(self)
	
	def copy(self):
		return type(self)(*(item.copy() if isinstance(item , Markup) else item for item in self.content), **self.attributes)
	
	@classmethod
	def closed(cls : "type[_TAG]", **attributes) -> "_TAG":
		
		obj = cls(**attributes)
		SETATTR(obj, "_CLOSED", True)
		return obj

class HasCSS(Semantics):
	
	style : AttributeCSS = _Classy.CachedDefault(lambda self: AttributeCSS())

	@style.setter
	def style(self, value : str|AttributeCSS):
		if isinstance(value, str):
			from GeekyGadgets.Semantics.Rulesets.CSS import evaluateValueStatement
			self.__dict__["style"] = AttributeCSS(
				(name.strip(), evaluateValueStatement(statement))
				for name, sep, statement in (statement.partition(":") for statement in value.strip(";").split(";"))
			)

class Document(Markup):
	def __str__(self):
		return NEWLINE.join(map(str, self))
	def __repr__(self: Markup) -> str:
		return list(map(repr, self))

_TAG = TypeVar("_TAG", bound=Markup)

class Singlet(ABC):
	def __str__(self : "Markup") -> str:
		
		return f"<{self._tagName} {self.attributes}{' '*bool(self.end)}{self.end} />"

class RuntimeCreatedMarkup(Markup): pass
