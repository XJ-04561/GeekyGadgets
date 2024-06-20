
from GeekyGadgets.SQL import *

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