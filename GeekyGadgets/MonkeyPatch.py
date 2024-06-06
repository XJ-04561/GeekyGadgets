
from GeekyGadgets.Globals import *

if PYTHON_VERSION < (3, 12):
	from GeekyGadgets.Iterators import Batched
	import itertools
	itertools.batched = Batched

