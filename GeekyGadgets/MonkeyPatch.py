
import GeekyGadgets.Globals as _Globals

if _Globals.PYTHON_VERSION < (3, 12):
	import itertools
	import GeekyGadgets.Iterators
	itertools.batched = GeekyGadgets.Iterators.Batched


