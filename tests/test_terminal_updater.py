
from GeekyGadgets.TerminalUpdater import *
from GeekyGadgets.IO import CaptureOutput

def test_creation():

	import os
	os.makedirs(os.path.splitext(__file__)[0], exist_ok=True)
	os.chdir(os.path.splitext(__file__)[0])


	with CaptureOutput() as CU:
		default = TerminalUpdater("Testing Spinner", "TestSpinner", 4)
		with default:
			import time
			assert default.running
			time.sleep(2)
		defaultOutput = CU.read()
		assert not default.running

	with CaptureOutput():
		spinner = TerminalUpdater("Testing Spinner", "TestSpinner", 4, indicator=Spinner)
		with spinner:
			import time
			assert spinner.running
			time.sleep(2)
		spinnerOutput = CU.read()
		assert not spinner.running

	with CaptureOutput():
		textProgress = TerminalUpdater("Testing TextProgress", "TestTextProgress", 4, indicator=TextProgress)
		with textProgress:
			import time
			assert textProgress.running
			time.sleep(2)
		textProgressOutput = CU.read()
		assert not textProgress.running

	with CaptureOutput():
		loadingBar = TerminalUpdater("Testing LoadingBar", "TestLoadingBar", 4, indicator=LoadingBar)
		with loadingBar:
			import time
			assert loadingBar.running
			time.sleep(2)
		loadingBarOutput = CU.read()
		assert not loadingBar.running

	assert defaultOutput
	open("defaultOutput.txt", "w").write(defaultOutput)
	assert spinnerOutput
	open("spinnerOutput.txt", "w").write(spinnerOutput)
	assert textProgressOutput
	open("textProgressOutput.txt", "w").write(textProgressOutput)
	assert loadingBarOutput
	open("loadingBarOutput.txt", "w").write(loadingBarOutput)