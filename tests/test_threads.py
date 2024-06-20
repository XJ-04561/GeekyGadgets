
from GeekyGadgets.Threads import *

def test_future():
	
	import time
	import random
	
	def waitAndHash(letter):
		time.sleep(0.1+random.random()/2)
		return hash(letter)
	letters = "ABCDEFGHIJKLMNOPQRSTUVXYZ"

	threads = [Thread(target=waitAndHash, args=(letter,)) for letter in letters]
	futures : list[Future]= []
	for thread in threads:
		thread.start()
		futures.append(thread.future)
	for future in futures:
		assert not future.ready
	for future, letterHash in zip(futures, map(hash,letters)):
		assert future.call() == letterHash
	
	threads = [Thread(target=waitAndHash, args=(letter,)) for letter in letters]
	futures = []
	for thread in threads:
		thread.start()
		futures.append(thread.future)
	
	assert all(map(lambda x:x.group == None, futures))
	
	group = ThreadGroup(threads)
	for future in futures:
		assert future.group.alive
		assert future.group.anyAlive
		assert future.group.allAlive
	group.wait()
	
	for future, letterHash in zip(futures, map(hash,letters)):
		assert future.value == letterHash

	group = ThreadGroup()
	threads = [Thread(target=waitAndHash, args=(letter,), group=group) for letter in letters]
	futures = []
	for thread in threads:
		thread.start()
		futures.append(thread.future)
	
	group.wait()
	
	for future, letterHash in zip(futures, map(hash,letters)):
		assert future.value == letterHash
	
	t = Thread(target=waitAndHash, args=(["A"],))
	t.start()
	try:
		t.future.call()
	except Exception as e:
		exc = e
	assert isinstance(exc, TypeError)
	
def test_thread_group():
	import time
	import random
	def waitAndHash(letter):
		time.sleep(0.1+random.random()/2)
		return hash(letter)
	letters = "ABCDEFGHIJKLMNOPQRSTUVXYZ"

	threads = [Thread(target=waitAndHash, args=(letter,)) for letter in letters]
	
	assert not any(thread.alive for thread in threads)

	group = ThreadGroup(threads)
	group.start()

	assert all(thread.alive for thread in threads)
	
	group.wait()

	assert not any(thread.alive for thread in threads)

	group = ThreadGroup()
	threads = [Thread(target=waitAndHash, args=(letter,), group=group) for letter in letters]
	
	group.start()

	assert all(thread.alive for thread in threads)
	
	group.wait()

	assert not any(thread.alive for thread in threads)

def test_thread():
	import random, time

	def generateNumber(theDict):
		theDict[current_thread().name] = 1 + random.random()
	def waitForSeconds(theDict):
		time.sleep(0.1+theDict[current_thread().name]/2)
	def writeResults(theDict):
		theDict[current_thread().name] = 0
	
	theDict = {}
	group = ThreadGroup()
	threads = [Thread(pre=generateNumber, target=waitForSeconds, post=writeResults, args=(theDict,), group=group) for _ in range(6)]
	group.start()

	assert len(theDict) == len(threads)
	assert not any(n == 0 for n in theDict.values())

	group.wait()

	assert all(n == 0 for n in theDict.values())

