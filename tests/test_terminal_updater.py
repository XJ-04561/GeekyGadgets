
from GeekyGadgets.TerminalUpdater import *

def test_creation():

	import os

	defaultTU = TerminalUpdater("Testing Spinner", "TestSpinner", 4, out=open(os.devnull, "w"))
	spinner = TerminalUpdater("Testing Spinner", "TestSpinner", 4, indicator=Spinner, out=open(os.devnull, "w"))
	textProgress = TerminalUpdater("Testing TextProgress", "TestTextProgress", 4, indicator=TextProgress, out=open(os.devnull, "w"))
	loadingBar = TerminalUpdater("Testing LoadingBar", "TestLoadingBar", 4, indicator=LoadingBar, out=open(os.devnull, "w"))

	with defaultTU:
		import time
		assert defaultTU.running
		time.sleep(2)
	assert not defaultTU.running

	with spinner:
		import time
		assert spinner.running
		time.sleep(2)
	assert not spinner.running

	with textProgress:
		import time
		assert textProgress.running
		time.sleep(2)
	assert not textProgress.running

	with loadingBar:
		import time
		assert loadingBar.running
		time.sleep(2)
	assert not loadingBar.running
