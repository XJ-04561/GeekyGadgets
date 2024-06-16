
from GeekyGadgets.Wrappers import *

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

	_oldstdout = sys.stdout
	sys.stdout = open("stdout.txt", "w")
	import time, threading
	
	help(_f)
	sys.stdout.close()
	expectedOut = open("stdout.txt", "r").read()
	sys.stdout = open("stdout.txt", "w")
	help(f)

	assert expectedOut

	assert f(8) == _f(8)

	sys.stdout.close()
	sys.stdout = _oldstdout

	assert open("stdout.txt", "r").read() == expectedOut

if __name__ == "__main__":
	test_wrappers()