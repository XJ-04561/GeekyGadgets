
from GeekyGadgets.Wrappers import *
from GeekyGadgets.IO import ReplaceSTDOUT

import pytest

@pytest.mark.skip
def test_wrappers():
	
	import os
	os.makedirs(os.path.splitext(__file__)[0], exist_ok=True)
	os.chdir(os.path.splitext(__file__)[0])
	
	class TestWrapper(Function): ...

	def f(a : int, b : float=12.):
		return a * b
	
	funcs = {"Original" : f, "Direct" : Function(f), "Subclass" : TestWrapper(f)}
	text = {}
	
	for name, func in funcs.items():
		with ReplaceSTDOUT() as replacer:
			help(func)
			text[name] = replacer.read()
	
	assert text["Original"]
	assert text["Direct"]
	assert text["Subclass"]
	
	assert funcs["Original"](8) == funcs["Direct"](8) == funcs["Subclass"](8)

	print (f"Original: {text['Original']!r}")
	print (f"Direct: {text['Direct']!r}")
	print (f"Subclass: {text['Subclass']!r}")
	
	assert text["Original"] == text["Direct"] == text["Subclass"]

if __name__ == "__main__":
	test_wrappers()