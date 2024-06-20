
from GeekyGadgets.Threads.Globals import *
from GeekyGadgets.Classy import ClassProperty
from GeekyGadgets.Threads.Thread import Thread

__all__ = ("ThreadsMeta", "set_profile", "set_profile_all_threads", "get_profile", "set_trace_function",
		   "set_trace_all_threads", "get_trace_function", "current_thread", "active_count", "enumerate_threads",
		   "main_thread")

class ThreadsMeta:
	
	@staticmethod
	@wraps(set_profile)
	def setProfile(func):
		return set_profile(func)
	
	@staticmethod
	@wraps(set_profile_all_threads)
	def setProfileAllThreads(func):
		return set_profile_all_threads(func)
	
	@ClassProperty
	def getProfile(self):
		return get_profile()
	
	@staticmethod
	@wraps(set_trace_function)
	def setTraceFunction(func):
		return set_trace_function(func)
	
	@staticmethod
	@wraps(set_trace_all_threads)
	def setTraceAllThreads(func):
		return set_trace_all_threads(func)
	
	@ClassProperty
	def getTraceFunction(self):
		return get_trace_function()
	
	@ClassProperty
	def currentThread(self) -> Thread:
		return current_thread()
	
	@ClassProperty
	def activeCount(self) -> int:
		return active_count()
	
	@ClassProperty
	def threads(self) -> list[Thread]:
		return enumerate_threads()
	
	@ClassProperty
	def mainThread(self) -> Thread:
		return main_thread()