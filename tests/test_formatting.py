
from GeekyGadgets.Formatting.Case import *

def test_case():
	
	cases = [ScreamingSnakeCase, SnakeCase, CamelCase, PascalCase, KebabCase]

	resultNames = [	"A_VERY_CONSTANT_SNAKE_NAME",
					"a_very_constant_snake_name",
					"aVeryConstantSnakeName",
					"AVeryConstantSnakeName",
					"a-very-constant-snake-name"]

	for name in resultNames:
		for case, expectedName in zip(cases, resultNames):
			assert case(name) == expectedName