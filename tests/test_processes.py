
from GeekyGadgets.Processes import *
import sys, os
from subprocess import Popen

EXE = sys.executable

def test_process():

	os.chdir(os.path.dirname(__file__))

	COMMANDS = [
		(f"{EXE} success.py", [0], True),
		(f"{EXE} fail.py", [1], False),
		(f"{EXE} success.py || {EXE} fail.py", [0, None], True),
		(f"{EXE} success.py && {EXE} fail.py", [0, 1], False),
		(f"{EXE} fail.py || {EXE} success.py", [1, 0], True),
		(f"{EXE} fail.py && {EXE} success.py", [1, None], True),
		
		(f"{EXE} startpipe.py | {EXE} endpipe.py > simplepipe.txt", [0, 0], True),
		(f"{EXE} startpipe.py | {EXE} midpipe.py | {EXE} endpipe.py > doublepipe.txt", [0, 0, 0], True),
		(f"{EXE} startpipe.py | {EXE} midpipe.py | {EXE} midpipe.py | {EXE} midpipe.py | {EXE} midpipe.py | {EXE} endpipe.py > longpipe.txt", [0, 0, 0, 0, 0, 0], True)
	]
	
	for i, (commandString, returncodes, success) in enumerate(COMMANDS):
		outDir = os.path.join(".", f"test_progress_{i}")
		os.makedirs(outDir, exist_ok=True)

		command = Command(commandString, dir=outDir)
		
		assert len(command.processes) == len(returncodes)

		assert not command.success
		
		command.start()
		command.wait()

		assert command.exitcodes == returncodes
		assert command.success == success

	assert open(os.path.join(".", "test_progress_6", "simplepipe.txt"), "r").read() == "Start\n0\n1\n4\n9\n16\n25\n"
	assert open(os.path.join(".", "test_progress_7", "doublepipe.txt"), "r").read() == "Start\n0\n1\n8\n27\n64\n125\n"
	assert open(os.path.join(".", "test_progress_8", "longpipe.txt"), "r").read() == "Start\n0\n1\n64\n729\n4096\n15625\n"