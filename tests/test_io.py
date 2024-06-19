
from GeekyGadgets.IO import *

import pytest

@pytest.mark.skip
def test_re_printer():

	rePrinter = RePrinter()

@pytest.mark.skip
def test_split_io():

	splitIo = SplitIO()
	splitIo.write("DJSLVMVB,MREBOBMER")
	assert splitIo.read() == "DJSLVMVB,MREBOBMER"

@pytest.mark.skip
def test_split_binary_io():

	splitBinaryIo = SplitBinaryIO()
	splitBinaryIo.write("DJSLVMVB,MREBOBMER")
	assert splitBinaryIo.read() == "DJSLVMVB,MREBOBMER"

@pytest.mark.skip
def test_split_text_io():

	splitTextIo = SplitTextIO()
	splitTextIo.write("DJSLVMVB,MREBOBMER")
	assert splitTextIo.read() == "DJSLVMVB,MREBOBMER"

def test_local_buffer_io():

	localBufferIo = LocalBufferIO()
	localBufferIo.write("DJSLVMVB,MREBOBMER")
	assert localBufferIo.read() == "DJSLVMVB,MREBOBMER"

def test_local_io():

	localIo = LocalIO()
	localIo.write("DJSLVMVB,MREBOBMER")
	assert localIo.read() == "DJSLVMVB,MREBOBMER"

@pytest.mark.skip
def test_replace_io():

	replaceIo = ReplaceIO()
	replaceIo.write("DJSLVMVB,MREBOBMER")
	assert replaceIo.read() == "DJSLVMVB,MREBOBMER"

@pytest.mark.skip
def test_siphon_io():

	siphonIo = SiphonIO()
	siphonIo.write("DJSLVMVB,MREBOBMER")
	assert siphonIo.read() == "DJSLVMVB,MREBOBMER"

