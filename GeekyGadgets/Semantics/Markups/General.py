
from GeekyGadgets.Semantics.Markups.Globals import *

import GeekyGadgets.Formatting.Case as _Case
import GeekyGadgets.Classy as _Classy
import GeekyGadgets.Functions as _Functions

__all__ = ("createMarkup", "parseMarkup", "parseInline", "createTagClass")

LOGGER = ROOT_LOGGER.getChild(__name__)
TAG_PATTERN = re.compile(r"""<\s*(?P<closing>/)?\s*(?P<name>[-\w:.]+)(?P<inline>(?:\s+[-\w:.]+\s*=\s*(?:".+?(?<!\\)"|'.+?(?<!\\)'|[^"'>/\s]+))*)(?:\s*(?P<closed>/))?\s*>""")
INLINE_ATTRIBUTE_PATTERN = re.compile(r"""(?P<name>[-\w:.]+)\s*=\s*(?P<quote>["'])?(?(quote)(.+?)(?<!\\)(?P=quote)|([^"'>\s]+))""")

def createTagClass(name : str, base : type[Markup]|None=RuntimeCreatedMarkup):
	
	from GeekyGadgets.Semantics.Markups import MARKUP_TYPES
	
	for muType in MARKUP_TYPES:
		if muType is not base and name in muType._SUBCLASS_LOOKUP:
			# LOGGER.debug(f"Found tag class {name!r} as a subclass of {muType}")
			return muType._SUBCLASS_LOOKUP[name]
	else:
		# LOGGER.debug(f"Could not find tag class for {name!r}, created it now as a subclass of {base}")
		return type(_Case.PascalCase(name), (base, ), {}, tagName=name)

def createMarkup(name : str, inline : dict={}, content : tuple[str|Markup]=(), markupType : type[Markup]=RuntimeCreatedMarkup, closed : bool=False) -> Markup:
	
	if name not in markupType._SUBCLASS_LOOKUP:
		tagClass = createTagClass(name, base=markupType)
		return tagClass.closed(*content, **inline) if closed else tagClass(*content, **inline)
	elif closed:
		return markupType._SUBCLASS_LOOKUP[name].closed(*content, **inline)
	else:
		return markupType._SUBCLASS_LOOKUP[name](*content, **inline)
		
_MARKUP = TypeVar("_MARKUP")
def parseMarkup(string, pos : int=0, endpos : int|None=None, markupType : type[_MARKUP]|type[Markup]=RuntimeCreatedMarkup) -> Document[str|_MARKUP|Markup]:
	
	from GeekyGadgets.Semantics.Markups import MARKUP_TYPES
	
	if endpos is None:
		endpos = len(string)

	ret : list[Markup] = []
	prev = 0
	
	# name, inline, text content
	opened : list[list[str,str,list[str|Markup]]] = []
	for match in TAG_PATTERN.finditer(string, pos=pos, endpos=endpos):
		# LOGGER.debug(f"Found tagName = {match.group('name')}")
		if prev < match.start() and not string[prev:match.start()].isspace():
			(opened[-1][2] if opened else ret).append(string[prev:match.start()].strip())
		if match.group("closed"):
			(opened[-1][2] if opened else ret).append(createMarkup(
				match.group("name"),
				inline=parseInline(match.group("inline")),
				content=[],
				markupType=markupType,
				closed=True
			))
		elif match.group("closing"):
			if opened and match.group("name").lower() == opened[-1][0].lower():
				(opened[-2][2] if len(opened) > 1 else ret).append(createMarkup(
					opened[-1][0],
					inline=parseInline(opened[-1][1]),
					content=opened[-1][2],
					markupType=markupType
				))
				opened.pop()
			elif opened and opened[-1][2] and isinstance(opened[-1][2][-1], str):
				opened[-1][2][-1] = opened[-1][2][-1] + match.group(0)
			elif opened:
				opened[-1][2].append(match.group(0))
			elif ret and isinstance(ret[-1], str):
				ret[-1] = ret[-1] + match.group(0)
			else:
				ret.append(match.group(0))
			
		elif any(match.group("name") in cls._singletons for cls in MARKUP_TYPES):
			(opened[-1][2] if opened else ret).append(createMarkup(
				match.group("name"),
				inline=parseInline(match.group("inline")),
				content=[],
				markupType=markupType
			))
		else:
			opened.append([match.group("name"), match.group("inline"), []])
		prev = match.end()
	
	if prev < endpos:
		prior = string[prev:endpos]
		if not prior.isspace():
			if opened:
				opened[-1][2].append(prior.strip())
			else:
				ret.append(prior.strip())

	while opened:
		current = opened.pop()
		(opened[-1][2] if opened else ret).append(createMarkup(
			current[0],
			inline=parseInline(current[1]),
			content=current[2],
			markupType=markupType
		))

	return Document(*ret)

def parseInline(string : str) -> dict:
	from GeekyGadgets.Functions import parseFloat, parseInt
	ret = {}
	for match in INLINE_ATTRIBUTE_PATTERN.finditer(string or ""):
		name, delimiter, stringValue, value = match.groups()

		if stringValue is not None:
			ret[name] = stringValue
			continue
		
		if (i := parseInt(value)) is not None:
			ret[name] = int(value)
		elif (f := parseFloat(value)) is not None:
			ret[name] = f
		elif value.lower() == "none":
			ret[name] = None
		elif value.lower() == "false":
			ret[name] = False
		elif value.lower() == "true":
			ret[name] = True
		else:
			ret[name] = value
	return ret

