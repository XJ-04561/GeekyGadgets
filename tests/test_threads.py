
from GeekyGadgets.Threads import *

def test_future():
	
	import time
	import random
	
	def waitAndHash(letter):
		time.sleep(random.random())
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
		time.sleep(random.random())
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
		time.sleep(theDict[current_thread().name])
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

def test_thread_connection():
	tc = ThreadConnection(":memory:")

	tc.execute("CREATE TABLE test_table (id INTEGER PRIMARY KEY, name TEXT UNIQUE);")
	tc.execute("INSERT INTO test_table (name) VALUES ('My favorite!');")
	tc.execute("INSERT INTO test_table (name) VALUES (?);", ["My least favorite..."])

	rows = tc.execute("SELECT * FROM test_table;").fetchall()
	assert len(rows) == 2
	assert len(rows[0]) == 2
	assert len(rows[1]) == 2
	
	results = set([
		(1, "My favorite!"),
		(2, "My least favorite...")
	])

	assert rows[0] in results
	results.discard(rows[0])
	assert rows[0] not in results
	
	assert rows[1] in results
	results.discard(rows[1])
	assert rows[1] not in results