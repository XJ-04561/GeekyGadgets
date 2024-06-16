
from GeekyGadgets.Logging import *

def test_logged():
	
	import os
	os.makedirs(os.path.splitext(__file__)[0], exist_ok=True)
	os.chdir(os.path.splitext(__file__)[0])
	from GeekyGadgets.Iterators import Chain
	logging.basicConfig(filename="root.log")

	class A(Logged):
		def greet(self):
			self.LOG.info(f"Hello, I'm {self.__class__.__name__}!")
			return f"INFO:root:Hello, I'm {self.__class__.__name__}!"
	class B(A): pass
	class C(B): pass
	class D(A): pass
	class E(Logged):
		def greet(self):
			self.LOG.info(f"Hello, I'm {self.__class__.__name__}!")
			return f"INFO:root:Hello, I'm {self.__class__.__name__}!"
	
	a = A()
	b = B()
	c = C()
	d = D()
	e = E()

	open("root.log", "w").close()
	for row, obj in zip(Chain([None], open("root.log", "r")), [a, b, c, d, e, None]):
		string = obj.greet()
		if row is None:
			continue
		else:
			assert row.strip() == string