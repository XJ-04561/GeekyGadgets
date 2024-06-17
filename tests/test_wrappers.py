
from GeekyGadgets.Wrappers import *
from GeekyGadgets.IO import ReplaceSTDOUT

def test_wrappers():
	
	import os
	os.makedirs(os.path.splitext(__file__)[0], exist_ok=True)
	os.chdir(os.path.splitext(__file__)[0])
	
	class TestWrapper(WrapsFunc):
		
		def __call__(self, *args, **kwargs):
			return self.func(*args, **kwargs)

	def f(a : int, b : float=12.):
		return a * b
	_f = f
	@TestWrapper
	def f(a : int, b : float=12.):
		return a * b

	with ReplaceSTDOUT() as replacer:
		help(_f)
		normalText = replacer.read()
	
	assert normalText

	with ReplaceSTDOUT() as replacer:
		help(f)
		wrappedText = replacer.read()

	assert wrappedText

	assert f(8) == _f(8)

	print (f"{normalText=}")
	print (f"{wrappedText=}")
	assert normalText == wrappedText

if __name__ == "__main__":
	test_wrappers()