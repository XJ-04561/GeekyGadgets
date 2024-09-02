
from GeekyGadgets.Formatting.Case import *
from GeekyGadgets.Formatting.SISize import *
from GeekyGadgets.Formatting import *

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

def test_round_significant():
	
	d = 5

	# Simple numbers
	for i in range(-10, 10):
		n = 10**i
		if i < -3:
			assert format(n, f".{d-1}e") == roundSignificant(n, digits=d)
		elif i < 0:
			assert str(n).lstrip("0") == roundSignificant(n, digits=d)
		elif i == 0:
			assert "1" == roundSignificant(n, digits=d)
		elif i <= d-1:
			assert str(n)[:i+1] == roundSignificant(n, digits=d)
		elif i <= 3+d:
			assert format(str(n)[:d], f"0<{i}") == roundSignificant(n, digits=d)
		else:
			assert format(n, f".{d}e") == roundSignificant(n, digits=d)
	
	n = 0.0038507396872615287

	assert ".0038507" == roundSignificant(n, digits=d)
	