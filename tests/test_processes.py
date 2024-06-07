
from GeekyGadgets.Processes import *
import sys

EXE = sys.executable

def test_process():

	COMMANDS = [
		(f"{EXE} success.py", [0], True),
		(f"{EXE} fail.py", [1], False),
		(f"{EXE} success || {EXE} fail", [0, None], True),
		(f"{EXE} success && {EXE} fail", [0, 1], False),
		(f"{EXE} fail || {EXE} success", [1, 0], True),
		(f"{EXE} fail && {EXE} success", [1, None], False),
		
		(f"{EXE} startpipe.py | {EXE} endpipe.py > simplepipe.txt", [0, 0], True),
		(f"{EXE} startpipe.py | {EXE} midpipe.py | {EXE} endpipe.py > doublepipe.txt", [0, 0], True),
		(f"{EXE} startpipe.py | {EXE} midpipe.py | {EXE} midpipe.py | {EXE} midpipe.py | {EXE} midpipe.py | {EXE} endpipe.py > longpipe.txt", [0, 0], True)
	]
	
	for commandString, returncodes, success in COMMANDS:
		command = Command(commandString)

		assert not command.success
		command.wait()
		command.success
		command.start()
		command.wait()

		assert command.success == success
		assert command.exitcodes == returncodes
