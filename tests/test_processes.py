
from GeekyGadgets.Processes import *
import sys, os
from subprocess import Popen

EXE = sys.executable

def test_process_single():
	
	os.makedirs(os.path.splitext(__file__)[0], exist_ok=True)
	os.chdir(os.path.splitext(__file__)[0])

	COMMANDS = [
		(f"{EXE} success.py", [0], True),
		(f"{EXE} fail.py", [1], False)
	]
	
	for i, (commandString, returncodes, success) in enumerate(COMMANDS):
		outDir = os.path.join(".", f"single_{i+1}")
		os.makedirs(outDir, exist_ok=True)

		command = Command(commandString, directory=outDir)
		
		assert len(command.processes) == len(returncodes)

		assert not command.success
		
		command.start()
		command.wait()
		command.dumpLogs()

		assert command.exitcodes == returncodes
		assert command.success == success
	
	assert open(os.path.join(".", "single_1", "python_success_1.out.log"), "r").read() == "success\n"
	assert open(os.path.join(".", "single_2", "python_fail_1.out.log"), "r").read() == "fail\n"

def test_process_logic():

	os.makedirs(os.path.splitext(__file__)[0], exist_ok=True)
	os.chdir(os.path.splitext(__file__)[0])

	COMMANDS = [
		(f"{EXE} success.py || {EXE} fail.py", [0, None], True),
		(f"{EXE} success.py && {EXE} fail.py", [0, 1], False),
		(f"{EXE} fail.py || {EXE} success.py", [1, 0], True),
		(f"{EXE} fail.py && {EXE} success.py", [1, None], True)
	]
	
	for i, (commandString, returncodes, success) in enumerate(COMMANDS):
		outDir = os.path.join(".", f"logic_{i+1}")
		os.makedirs(outDir, exist_ok=True)

		command = Command(commandString, directory=outDir)
		
		assert len(command.processes) == len(returncodes)

		assert not command.success
		
		command.start()
		command.wait()
		command.dumpLogs()

		assert command.exitcodes == returncodes
		assert command.success == success

	assert open(os.path.join(".", "logic_1", "python_success_1.out.log"), "r").read() == "success\n"
	assert not os.path.exists(os.path.join(".", "logic_1", "python_fail_2.out.log"))

	assert open(os.path.join(".", "logic_2", "python_success_1.out.log"), "r").read() == "success\n"
	assert open(os.path.join(".", "logic_2", "python_fail_2.out.log"), "r").read() == "fail\n"
	
	assert open(os.path.join(".", "logic_3", "python_fail_1.out.log"), "r").read() == "fail\n"
	assert open(os.path.join(".", "logic_3", "python_success_2.out.log"), "r").read() == "success\n"
	
	assert open(os.path.join(".", "logic_4", "python_fail_1.out.log"), "r").read() == "fail\n"
	assert not os.path.exists(os.path.join(".", "logic_4", "python_success_2.out.log"))

def test_process_pipe():

	os.makedirs(os.path.splitext(__file__)[0], exist_ok=True)
	os.chdir(os.path.splitext(__file__)[0])

	COMMANDS = [
		(f"{EXE} startpipe.py | {EXE} endpipe.py > simplepipe.txt", [0, 0], True),
		(f"{EXE} startpipe.py | {EXE} midpipe.py | {EXE} endpipe.py > doublepipe.txt", [0, 0, 0], True),
		(f"{EXE} startpipe.py | {EXE} midpipe.py | {EXE} midpipe.py | {EXE} midpipe.py | {EXE} midpipe.py | {EXE} endpipe.py > longpipe.txt", [0, 0, 0, 0, 0, 0], True)
	]
	
	for i, (commandString, returncodes, success) in enumerate(COMMANDS):
		outDir = os.path.join(".", f"pipe_{i+1}")
		os.makedirs(outDir, exist_ok=True)

		command = Command(commandString, directory=outDir)
		
		assert len(command.processes) == len(returncodes)

		assert not command.success
		
		command.start()
		command.wait()
		command.dumpLogs()

		assert command.exitcodes == returncodes
		assert command.success == success

	assert open(os.path.join(".", "pipe_1", "simplepipe.txt"), "r").read() == "Start\n0\n1\n4\n9\n16\n25\n"
	assert open(os.path.join(".", "pipe_2", "doublepipe.txt"), "r").read() == "Start\n0\n1\n8\n27\n64\n125\n"
	assert open(os.path.join(".", "pipe_3", "longpipe.txt"), "r").read() == "Start\n0\n1\n64\n729\n4096\n15625\n"


def test_process_capture_pipe():

	os.makedirs(os.path.splitext(__file__)[0], exist_ok=True)
	os.chdir(os.path.splitext(__file__)[0])

	COMMANDS = [
		(f"{EXE} startpipe.py", [0], True),
	]
	
	for i, (commandString, returncodes, success) in enumerate(COMMANDS):
		outDir = os.path.join(".", f"capture_pipe_{i+1}")
		os.makedirs(outDir, exist_ok=True)

		command = Command(commandString, directory=outDir)
		
		assert len(command.processes) == len(returncodes)

		assert not command.success
		
		command.start()
		command.wait()
		command.dumpLogs()

		assert command.exitcodes == returncodes
		assert command.success == success

	assert open(os.path.join(".", "capture_pipe_1", "python_startpipe_1.out.log"), "r").read() == "Start\n0\n1\n2\n3\n4\n5\n"
	assert command.processes[0].OUT.read() == "Start\n0\n1\n2\n3\n4\n5\n"