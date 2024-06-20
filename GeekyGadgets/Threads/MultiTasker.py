
from GeekyGadgets.Threads.Globals import *
from GeekyGadgets.Hooks import *
from GeekyGadgets.Classy import Default, threaded
from GeekyGadgets.Reporting import Reporter, Advisor

from GeekyGadgets.Threads.Thread import Thread, Future
from GeekyGadgets.Threads.Groups import ThreadGroup
from GeekyGadgets.Threads.Meta import ThreadsMeta

__all__ = ("MultiTasker", "task", "threadTask")

def runTask(self : "MultiTasker", name : str, func : function, /, *args, **kwargs):
	try:
		while not self.advisor.isComplete(name):
			if self.advisor.request(name):
				func(*args, **kwargs)
				self.reporter.Finished()
				break
			self.reporter.Progress(self.advisor.askProgress(name), name)
			time.sleep(0.25)
		else:
			self.reporter.Skipped()
	except:
		self.reporter.Failed()
		raise

def task(func : function):

	@wraps(func)
	def _taskWrapper(self : MultiTasker, name : str, /, *args, **kwargs):
		self.workers.add(ThreadsMeta.currentThread)
		runTask(self, name, func, *args, **kwargs)
	
	return _taskWrapper

def threadTask(func : function):
	return threaded(task(func))

class MultiTasker(Logged):
	
	workers : "set[Thread]"
	results : list
	hooks : Hooks = Default(lambda self:GlobalHooks, lambda self, hooks:(setattr(self.reporter, "hooks", hooks), setattr(self.advisor, "hooks", hooks)))
	reporter : Reporter
	advisor : Advisor

	def __init__(self, *, hooks : Hooks=GlobalHooks):

		self.workers = set()
		self.results = []
		self.reporter = Reporter(category=type(self).__name__)
		self.advisor = Advisor(category=type(self).__name__)
		self.hooks = hooks
		
		self.LOG.info(f"Created {type(self)} object at 0x{id(self):0>16X}")

	def wait(self):
		for worker in tuple(self.workers):
			self.results.append(worker.future.call())
			self.workers.discard(worker)
	