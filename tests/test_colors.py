
from GeekyGadgets.Colors import *
from GeekyGadgets.Colors.HTML import *

import pytest

@pytest.mark.skip
def test_ansi_colors():
	
	from GeekyGadgets.Colors.ANSI import RedText, GreenText, BlueText

# @pytest.mark.skip
def test_ansi_HTML():
	
	from GeekyGadgets.Colors.HTML import RedText, GreenText, BlueText

	assert RedText("A short message to be colored!") == "<span style=\"color:Red\">A short message to be colored!</span>"
	assert GreenText("A short message to be colored!") == "<span style=\"color:Green\">A short message to be colored!</span>"
	assert BlueText("A short message to be colored!") == "<span style=\"color:Blue\">A short message to be colored!</span>"

	assert RedText("A short message to be colored!") == "<span style=\"color:Red\">A short message to be colored!</span>"
	assert GreenText("A short message to be colored!") == "<span style=\"color:Green\">A short message to be colored!</span>"
	assert BlueText("A short message to be colored!") == "<span style=\"color:Blue\">A short message to be colored!</span>"
	assert CyanText("A short message to be colored!") == "<span style=\"color:Cyan\">A short message to be colored!</span>"
	assert MagentaText("A short message to be colored!") == "<span style=\"color:Magenta\">A short message to be colored!</span>"
	assert WhiteText("A short message to be colored!") == "<span style=\"color:White\">A short message to be colored!</span>"
	assert BlackText("A short message to be colored!") == "<span style=\"color:Black\">A short message to be colored!</span>"
	assert GrayText("A short message to be colored!") == "<span style=\"color:Gray\">A short message to be colored!</span>"
	assert OrangeText("A short message to be colored!") == "<span style=\"color:Orange\">A short message to be colored!</span>"
	assert BrownText("A short message to be colored!") == "<span style=\"color:Brown\">A short message to be colored!</span>"
	assert DarkGrayText("A short message to be colored!") == "<span style=\"color:DarkGray\">A short message to be colored!</span>"
	assert RedBackground("A short message to be colored!") == "<span style=\"background:Red\">A short message to be colored!</span>"
	assert GreenBackground("A short message to be colored!") == "<span style=\"background:Green\">A short message to be colored!</span>"
	assert BlueBackground("A short message to be colored!") == "<span style=\"background:Blue\">A short message to be colored!</span>"
	assert CyanBackground("A short message to be colored!") == "<span style=\"background:Cyan\">A short message to be colored!</span>"
	assert MagentaBackground("A short message to be colored!") == "<span style=\"background:Magenta\">A short message to be colored!</span>"
	assert WhiteBackground("A short message to be colored!") == "<span style=\"background:White\">A short message to be colored!</span>"
	assert BlackBackground("A short message to be colored!") == "<span style=\"background:Black\">A short message to be colored!</span>"
	assert GrayBackground("A short message to be colored!") == "<span style=\"background:Gray\">A short message to be colored!</span>"
	assert OrangeBackground("A short message to be colored!") == "<span style=\"background:Orange\">A short message to be colored!</span>"
	assert BrownBackground("A short message to be colored!") == "<span style=\"background:Brown\">A short message to be colored!</span>"
	assert DarkGrayBackground("A short message to be colored!") == "<span style=\"background:DarkGray\">A short message to be colored!</span>"