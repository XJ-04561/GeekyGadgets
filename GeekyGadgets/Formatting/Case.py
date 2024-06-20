

from GeekyGadgets.Globals import *
from GeekyGadgets.This import this

screamingSnakeCase : re.Pattern = re.compile("^[A-Z_][A-Z_0-9]*$")
snakeCase : re.Pattern= re.compile("^[a-z_][a-z_0-9]*$")
camelCase : re.Pattern= re.compile("^[_]*[a-z][a-zA-Z0-9]*[_]*$")
pascalCase : re.Pattern= re.compile("^[_]*[A-Z][a-zA-Z0-9]*[_]*$")
kebabCase : re.Pattern= re.compile("^[a-z][a-z0-9-]*$")

CASES = [screamingSnakeCase, snakeCase, camelCase, pascalCase, kebabCase]

# camelKiller : re.Pattern= re.compile(r"([A-Z]+(?:[A-Z]|$|[_])|[A-Z][a-z0-9]+|^[a-z][a-z0-9]*|[a-z0-9]+)")
# pascalKiller : re.Pattern= re.compile(r"[A-Z0-9][a-z0-9]+|[A-Z0-9]+|[a-z0-9]+")
# snakeKiller : re.Pattern= re.compile(r"([^_]+)")
# kebabKiller : re.Pattern= re.compile(r"([^-]+)")

camelKiller : re.Pattern= re.compile(r"(?<=[a-z0-9])(?=[A-Z0-9])")
pascalKiller : re.Pattern= re.compile(r"(?<=[a-z0-9])(?=[A-Z0-9])|(?<=[A-Z0-9])(?=[A-Z0-9]+(?!$))")
snakeKiller : re.Pattern= re.compile(r"[_]")
kebabKiller : re.Pattern= re.compile(r"[-]")

CASE_KILLERS = [snakeKiller, snakeKiller, camelKiller, pascalKiller, kebabKiller]

class Case(str):
	def __new__(cls, name : str):
		for case, caseKiller in zip(CASES, CASE_KILLERS):
			if case.fullmatch(name):
				words = caseKiller.split(name)
				break
		return super().__new__(str, cls.join(words))

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