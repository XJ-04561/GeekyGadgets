

try:
	from PseudoPathy import *
except:
	import os
	class Path(str):
		def __truediv__(self, other):
			return Path(os.path.join(self, other))