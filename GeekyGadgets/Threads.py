

from GeekyGadgets.Globals import *

class DummyLock:
	def acquire(self, blocking: bool = ..., timeout: float = ...):
		return True
	def release(self):
		pass
	@property
	def locked(self):
		return False