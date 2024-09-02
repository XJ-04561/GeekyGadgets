
from GeekyGadgets.Semantics.Markdown.Globals import *
import GeekyGadgets.Functions as _Funcs
import GeekyGadgets.Iterators.Walkers as _Walkers
import GeekyGadgets.Semantics.Markdown.Blocks as _Blocks
import GeekyGadgets.Semantics.Markdown.Text as _Text

class MarkdownVersion:
	
	BLOCKS : list[Block] = [_Blocks.TextBlock]
	INLINES : list[Inline] = [_Text.LineBreak]
	BLOCK_PATTERN : re.Pattern
	INLINE_PATTERN : re.Pattern
	DEFAULT_BLOCK : Block = _Blocks.TextBlock
	DEFAULT_INLINE : Inline|str = str

	def __init_subclass__(cls) -> None:
		cls.BLOCK_PATTERN = re.compile("|".join(f"(?P<{blockCls.__name__}>{blockCls.PATTERN})" for blockCls in cls.BLOCKS))
		cls.INLINE_PATTERN = re.compile("|".join(f"(?P<{inlineCls.__name__}>{inlineCls.PATTERN})" for inlineCls in cls.INLINES))

class GeekyMarkdown(MarkdownVersion):
	
	BLOCKS : list[Block] = sorted((blockCls for blockCls in _Walkers.SubClassWalker(Block) if not isinstance(blockCls, ABC)), key=lambda x:x.PRIORITY, reverse=True)
	INLINES : list[Inline] = sorted((inlineCls for inlineCls in _Walkers.SubClassWalker(Inline) if not isinstance(inlineCls, ABC)), key=lambda x:x.PRIORITY, reverse=True)

def parseBlocks(string : str, markdown=GeekyMarkdown) -> list[Block]:
	
	content = []
	topLevelMatches = list(markdown.BLOCK_PATTERN.finditer(string))
	absStart = 0
	for match in topLevelMatches:
		if absStart < match.start():
			content.append(markdown.DEFAULT_BLOCK.parse(string[absStart:match.start()], markdown=markdown))
		for blockCls in markdown.BLOCKS:
			if match.group(blockCls.__name__) is not None:
				break
		else:
			raise ValueError(f"Regex match but no class associated with match(={match}). Classes were removed from the markdown version while parsing. Markdown version was: {markdown}")
		content.append(blockCls.parse(match.group(), markdown=markdown))
		absStart = match.end()
	else:
		if absStart < len(string):
			content.append(markdown.DEFAULT_BLOCK.parse(string[absStart], markdown=markdown))
	return content

def parseInline(string : str, markdown=GeekyMarkdown) -> list[str|Markdown]:
	
	content : list[str|Markdown|list[Markdown]] = [""]
	N = len(string)
	opened = []
	position = 0
	for m in markdown.INLINE_PATTERN.finditer(string):
		for inlineCls in markdown.INLINES:
			if m.group(inlineCls.__name__) is not None:
				break
		else:
			raise ValueError(f"Regex match but no class associated with match(={m}). Classes were removed from the markdown version while parsing. Markdown version was: {markdown}")
		if isinstance(content[-1], list):
			for i, item in enumerate(content[-1]):
				if isinstance(item, inlineCls):
					path = []
					while i < len(content[-1])-1:
						lowerItem = content[-1].pop()
						path.append(type(lowerItem))
						content[-1][-1].append(lowerItem)
					item = content[-1].pop()
					if content[-1]:
						content[-1][-1].append(item)
					else:
						content[-1] = item
					for lowerCls in reversed(path):
						content[-1].append(lowerCls())
					break
			else:
				content[-1].append(inlineCls())
		else:
			if position < m.start():
				content.append(string[position:m.start()])
			content.append([inlineCls()])
		position = m.end()
	else:
		if content and isinstance(content[-1], list):
			content[-1][-1].append(string[position:])
			lastObj = content[-1].pop()
			while content[-1]:
				content[-1][-1].append(lastObj)
				lastObj = content[-1].pop()
			content[-1] = lastObj
		elif position < len(string):
			content.append(string[position:])
	return content

	# topLevelMatches = list(markdown.INLINE_PATTERN.finditer(string))
	# absStart = 0
	# for match in topLevelMatches:
	# 	if absStart < match.start():
	# 		content.append(markdown.DEFAULT_INLINE.parse(string[absStart:match.start()], markdown=markdown))
	# 	for blockCls in markdown.INLINES:
	# 		if match.group(blockCls.__name__) is not None:
	# 			break
	# 	else:
	# 		raise ValueError(f"Regex match but no class associated with match(={match}). Classes were removed from the markdown version while parsing. Markdown version was: {markdown}")
	# 	content.append(blockCls.parse(match.group(), markdown=markdown))
	# 	absStart = match.end()
	# else:
	# 	if absStart < len(string):
	# 		content.append(markdown.DEFAULT_INLINE.parse(string[absStart], markdown=markdown))
	# return content