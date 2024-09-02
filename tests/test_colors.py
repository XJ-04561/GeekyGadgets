
from GeekyGadgets.Colors import *
from GeekyGadgets.Colors.HTML import *

import pytest

def test_color_shift():
	from GeekyGadgets.Colors.General import RGB, HSV, HSL
	from GeekyGadgets.Logging import setLevel
	setLevel(100)
	import matplotlib.pyplot as plt
	from math import log, log10

	os.makedirs(os.path.splitext(__file__)[0], exist_ok=True)
	os.chdir(os.path.splitext(__file__)[0])

	assert abs(RGB(145, 126, 120) - HSL(14, 10, 52).rgb()) < 0.02
	assert abs(RGB(145, 126, 120) - HSV(14, 17, 57).rgb()) < 0.02
	assert abs(RGB(145, 126, 120) - RGB(145, 126, 120).hsv().rgb()) < 0.02

	data = [[254, 226, 174], [0, 0, 0], [253, 188, 68], [0, 0, 0], [255, 248, 241], [0, 0, 0], [253, 188, 68], [255, 248, 241], [0, 0, 0], [253, 188, 68], [252, 210, 130], [255, 165, 0], [0, 0, 0], [255, 248, 241], [0, 0, 0], [253, 188, 68], [0, 0, 0], [253, 188, 68], [234, 166, 41], [0, 0, 0], [253, 188, 68], [0, 0, 0], [255, 248, 241], [253, 188, 68], [0, 0, 0], [255, 248, 241], [0, 0, 0], [254, 226, 174], [253, 188, 68], [253, 188, 68], [255, 248, 241], [0, 0, 0], [253, 188, 68], [254, 226, 174], [0, 0, 0], [254, 226, 174], [253, 188, 6]]
	names = ["toolbar", "toolbar_text", "frame", "tab_background_text", "toolbar_field", "toolbar_field_text", "tab_line", "popup", "popup_text", "button_background_active", "button_background_hover", "icons_attention", "icons", "ntp_background", "ntp_text", "popup_border", "popup_highlight_text", "popup_highlight", "sidebar_border", "sidebar_highlight_text", "sidebar_highlight", "sidebar_text", "sidebar", "tab_background_separator", "tab_loading", "tab_selected", "tab_text", "toolbar_bottom_separator", "toolbar_field_border_focus", "toolbar_field_border", "toolbar_field_focus", "toolbar_field_highlight_text", "toolbar_field_highlight", "toolbar_field_separator", "toolbar_field_text_focus", "toolbar_top_separator", "toolbar_vertical_separator"]
	lightColors = [RGB(*values) for values in data]
	colorThemes = {
		"lightColors" : lightColors,
		"invertedColors" : [c.hsl().invert(3).rgb() for c in lightColors],
		"darkenedColors01" : [c.darken(0.1) for c in lightColors],
		"darkenedColors05" : [c.darken(0.5) for c in lightColors],
		"darkenedColors08" : [c.darken(0.8) for c in lightColors],
		"darkenedColorsLog01" : [c.darken(0.1, func=log) for c in lightColors],
		"darkenedColorsLog05" : [c.darken(0.5, func=log) for c in lightColors],
		"darkenedColorsLog08" : [c.darken(0.8, func=log) for c in lightColors],
		"darkenedColorsLog10_01" : [c.darken(0.1, func=log10) for c in lightColors],
		"darkenedColorsLog10_05" : [c.darken(0.5, func=log10) for c in lightColors],
		"darkenedColorsLog10_08" : [c.darken(0.8, func=log10) for c in lightColors],
	}

	exportedColours = {}
	for name, lightColor, invertedColor in zip(names, colorThemes["lightColors"], colorThemes["invertedColors"]):
		if 0.1 < lightColor.hsl().lightness < 0.9:
			exportedColours[name] = lightColor
		else:
			exportedColours[name] = invertedColor
	colorThemes["exportedColors"] = list(exportedColours.values())

	for name, colors in colorThemes.items():
		print(name, colors[0], colors[0].hsl(), colors[0].hsl().invert(3))
		plt.barh(range(len(data)), 1.0, 1.0, color=list(map(RGB.hex, colors)), tick_label=names)
		plt.ylim(-0.5,len(data)-0.5)
		plt.xlim(0,1)
		plt.suptitle(name)
		plt.tight_layout()
		plt.savefig(f"{name}.svg")
		plt.clf()
	
	with open("colors.json", "w") as f:
		f.write("{\n")
		f.write(",\n".join(f"\t\"{name}\" : \"{value}\"" for name, value in exportedColours.items()))
		f.write("\n}\n")

@pytest.mark.skip
def test_ansi_colors():
	
	from GeekyGadgets.Colors.ANSI import RedText, GreenText, BlueText

@pytest.mark.skip
def test_ansi_HTML():
	
	from GeekyGadgets.Colors.HTML import RedText, GreenText, BlueText

	assert RedText("A short message to be colored!") == "<span style=\"color : Red\">A short message to be colored!</span>"
	assert GreenText("A short message to be colored!") == "<span style=\"color : Green\">A short message to be colored!</span>"
	assert BlueText("A short message to be colored!") == "<span style=\"color : Blue\">A short message to be colored!</span>"

	assert RedText("A short message to be colored!") == "<span style=\"color : Red\">A short message to be colored!</span>"
	assert GreenText("A short message to be colored!") == "<span style=\"color : Green\">A short message to be colored!</span>"
	assert BlueText("A short message to be colored!") == "<span style=\"color : Blue\">A short message to be colored!</span>"
	assert CyanText("A short message to be colored!") == "<span style=\"color : Cyan\">A short message to be colored!</span>"
	assert MagentaText("A short message to be colored!") == "<span style=\"color : Magenta\">A short message to be colored!</span>"
	assert WhiteText("A short message to be colored!") == "<span style=\"color : White\">A short message to be colored!</span>"
	assert BlackText("A short message to be colored!") == "<span style=\"color : Black\">A short message to be colored!</span>"
	assert GrayText("A short message to be colored!") == "<span style=\"color : Gray\">A short message to be colored!</span>"
	assert OrangeText("A short message to be colored!") == "<span style=\"color : Orange\">A short message to be colored!</span>"
	assert BrownText("A short message to be colored!") == "<span style=\"color : Brown\">A short message to be colored!</span>"
	assert DarkGrayText("A short message to be colored!") == "<span style=\"color : DarkGray\">A short message to be colored!</span>"
	assert RedBackground("A short message to be colored!") == "<span style=\"background : Red\">A short message to be colored!</span>"
	assert GreenBackground("A short message to be colored!") == "<span style=\"background : Green\">A short message to be colored!</span>"
	assert BlueBackground("A short message to be colored!") == "<span style=\"background : Blue\">A short message to be colored!</span>"
	assert CyanBackground("A short message to be colored!") == "<span style=\"background : Cyan\">A short message to be colored!</span>"
	assert MagentaBackground("A short message to be colored!") == "<span style=\"background : Magenta\">A short message to be colored!</span>"
	assert WhiteBackground("A short message to be colored!") == "<span style=\"background : White\">A short message to be colored!</span>"
	assert BlackBackground("A short message to be colored!") == "<span style=\"background : Black\">A short message to be colored!</span>"
	assert GrayBackground("A short message to be colored!") == "<span style=\"background : Gray\">A short message to be colored!</span>"
	assert OrangeBackground("A short message to be colored!") == "<span style=\"background : Orange\">A short message to be colored!</span>"
	assert BrownBackground("A short message to be colored!") == "<span style=\"background : Brown\">A short message to be colored!</span>"
	assert DarkGrayBackground("A short message to be colored!") == "<span style=\"background : DarkGray\">A short message to be colored!</span>"
	