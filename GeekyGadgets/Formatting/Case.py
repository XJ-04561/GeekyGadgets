

from GeekyGadgets.Globals import *

from GeekyGadgets.This import this

screamingSnakeCase : re.Pattern = re.compile(r"^[A-Z_:.][A-Z_0-9:.]*$")
snakeCase : re.Pattern = re.compile(r"^[a-z_:.][a-z_0-9:.]*$")
camelCase : re.Pattern = re.compile(r"^[_]*[a-z:.][a-zA-Z0-9:.]*[_]*$")
pascalCase : re.Pattern = re.compile(r"^[_]*[A-Z:.][a-zA-Z0-9:.]*[_]*$")
kebabCase : re.Pattern = re.compile(r"^[a-z:.][a-z0-9:.-]*$")
titleCase : re.Pattern = re.compile(r"^(([A-Z0-9_:.-][a-z0-9_:.-]{3,}|[A-z0-9_:.-]{1,3})|\s)+$")
sentenceCase : re.Pattern = re.compile(r"(((^|[.])\s+[A-Z0-9_:.-][a-z0-9_:.-]*|[A-z0-9_:.-])|\s)+$")

camelKiller : re.Pattern = re.compile(r"(?<=[a-z0-9])(?=[A-Z0-9])")
pascalKiller : re.Pattern = re.compile(r"(?<=[a-z0-9])(?=[A-Z0-9])|(?<=[A-Z0-9])(?=[A-Z0-9]+(?!$))")
snakeKiller : re.Pattern = re.compile(r"[_]")
kebabKiller : re.Pattern = re.compile(r"[-]")
titleKiller : re.Pattern = re.compile(r"[ ,-]+")
sentenceKiller : re.Pattern = re.compile(r"\s+")

NAME_KILLER : re.Pattern = re.compile(r"([:.])")

CASES = {
	"ScreamingSnakeCase" : (screamingSnakeCase, snakeKiller),
	"SnakeCase" : (snakeCase, snakeKiller),
	"CamelCase" : (camelCase, camelKiller),
	"PascalCase" : (pascalCase, pascalKiller),
	"KebabCase" : (kebabCase, kebabKiller),
	"TitleCase" : (titleCase, titleKiller),
	"SentenceCase" : (sentenceCase, sentenceKiller),
}

CASE_KILLERS = [snakeKiller, snakeKiller, camelKiller, pascalKiller, kebabKiller, titleKiller]

class Case:
	def __new__(cls, fullname : str):
		for caseName, (casePat, caseKiller) in CASES.items():
			if casePat.fullmatch(fullname):
				if cls.__name__ != caseName:
					return "".join(cls.join(caseKiller.split(name)) if name not in ":." else name for name in NAME_KILLER.split(fullname))
				else:
					break
		return str(fullname)

class ScreamingSnakeCase(Case):
	@staticmethod
	def join(words : list[str]):
		return "_".join(map(str.upper, words))

class SnakeCase(Case):
	@staticmethod
	def join(words : list[str]):
		return "_".join(map(str.lower, words))

class CamelCase(Case):
	@staticmethod
	def join(words : list[str]):
		return words[0].lower() + "".join(map(str.capitalize, words[1:]))
	
class PascalCase(Case):
	@staticmethod
	def join(words : list[str]):
		return "".join(map(str.capitalize, words))

class KebabCase(Case):
	@staticmethod
	def join(words : list[str]):
		return "-".join(map(str.lower, words))

class TitleCase(Case):
	@staticmethod
	def join(words : list[str]):
		return " ".join(map(lambda x:x.capitalize() if len(x) > 3 else x.lower(), words))

class SentenceCase(Case):
	@staticmethod
	def join(words : list[str]):
		return f"{' '.join([words[0].capitalize() if words[0][1:].islower() else words[0]]+words[1:])}{'.' if words[-1].strip()[-1] != '.' else ''}"

# def camel2snake(string : str):
# 	return "_".join(camelKiller.findall(string))

# def camel2pascal(string : str):
# 	return "".join(map(*this.capitalize(), camelKiller.findall(string)))

# def pascal2snake(string : str):
# 	return "_".join(PascalKiller.findall(string))

# def pascal2camel(string : str):
# 	return "".join(word.capitalize() if i > 0 else word for i, word in enumerate(PascalKiller.findall(string)))

# def snake2camel(string : str):
# 	return "".join(word.capitalize() if i > 0 else word for i, word in enumerate(snakeKiller.findall(string.lower())))

# def snake2pascal(string : str):
# 	return "".join(map(*this.capitalize(), snakeKiller.findall(string.lower())))

# def toPascal(string : str):
# 	if PascalCase.fullmatch(string):
# 		return string
# 	elif camelCase.fullmatch(string):
# 		return snake2camel(string)
# 	elif snake_case.fullmatch(string):
# 		return snake2pascal(string)
# 	else:
# 		return string

# def toCamel(string : str):
# 	if PascalCase.fullmatch(string):
# 		return pascal2camel(string)
# 	elif camelCase.fullmatch(string):
# 		return string
# 	elif snake_case.fullmatch(string):
# 		return snake2camel(string)
# 	else:
# 		return string

# def toSnake(string : str):
# 	if PascalCase.fullmatch(string):
# 		return pascal2snake(string)
# 	elif camelCase.fullmatch(string):
# 		return camel2snake(string)
# 	elif snake_case.fullmatch(string):
# 		return string
# 	else:
# 		return string