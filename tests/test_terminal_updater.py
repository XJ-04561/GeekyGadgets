
from GeekyGadgets.TerminalUpdater import *
from GeekyGadgets.IO import ReplaceSTDOUT

def test_creation():

	import os
	os.makedirs(os.path.splitext(__file__)[0], exist_ok=True)
	os.chdir(os.path.splitext(__file__)[0])


	with ReplaceSTDOUT() as replacer:
		default = TerminalUpdater("Testing Spinner", "TestSpinner", 4)
		with default:
			import time
			assert default.running
			time.sleep(2)
		defaultOutput = replacer.read()
		assert not default.running

	with ReplaceSTDOUT() as replacer:
		spinner = TerminalUpdater("Testing Spinner", "TestSpinner", 4, indicator=Spinner)
		with spinner:
			import time
			assert spinner.running
			time.sleep(2)
		spinnerOutput = replacer.read()
		assert not spinner.running

	with ReplaceSTDOUT() as replacer:
		textProgress = TerminalUpdater("Testing TextProgress", "TestTextProgress", 4, indicator=TextProgress)
		with textProgress:
			import time
			assert textProgress.running
			time.sleep(2)
		textProgressOutput = replacer.read()
		assert not textProgress.running

	with ReplaceSTDOUT() as replacer:
		loadingBar = TerminalUpdater("Testing LoadingBar", "TestLoadingBar", 4, indicator=LoadingBar)
		with loadingBar:
			import time
			assert loadingBar.running
			time.sleep(2)
		loadingBarOutput = replacer.read()
		assert not loadingBar.running

	assert defaultOutput
	open("defaultOutput.txt", "w").write(defaultOutput)
	assert spinnerOutput
	open("spinnerOutput.txt", "w").write(spinnerOutput)
	assert textProgressOutput
	open("textProgressOutput.txt", "w").write(textProgressOutput)
	assert loadingBarOutput
	open("loadingBarOutput.txt", "w").write(loadingBarOutput)