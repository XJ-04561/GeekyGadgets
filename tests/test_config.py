
CONFIG_DICT = {
	"version" : 1.0,
	"video_options" : {
		"resolution" : [1080, 1920],
		"anti_aliasing" : "FXAA",
		"frequency" : 60, # Hz/FPS
		"driver" : {
			"name" : "nvidia",
			"version" : 535
		}
	},
	"controls" : {
		"mouse" : {
			"frequency" : 1000,
			"sensitivity" : 1.2
		},
		"keyboard" : {
			"forward" : 87,
			"backward" : 83,
			"left" : 65,
			"right" : 68,
			"jump" : 32
		}
	}
}

def test_toml():
	
	from GeekyGadgets.Configs import loadTOML, Config, ConfigCategory, FlagNotFound
	import os
	os.makedirs(os.path.splitext(__file__)[0], exist_ok=True)
	os.chdir(os.path.splitext(__file__)[0])
	
	config1 = loadTOML("tomlExample.toml")
	config2 = CONFIG_DICT
	config3 = Config.fromDict(config2)

	assert str(config1) == str(config2) == str(config3)
	assert config1 == config2 == config3

	assert config1["version"] == 1.0
	
	assert config1["video_options"] == {'resolution': [1080, 1920], 'anti_aliasing': 'FXAA', 'frequency' : 60, 'driver' : {'name' : 'nvidia', 'version' : 535}}
	
	assert config1["controls.mouse.sensitivity"] == 1.2
	
	assert config1["frequency"] == {'video_options': 60, 'controls.mouse': 1000}

	config1["video_options.vibrance"] = 100
	config2["video_options"]["vibrance"] = 100

	assert config1["video_options"] == config2["video_options"]

	try:
		config1["video_options.resolution.height"] = 1440
		assert False, "A non-category object can't be part of a hierarchy."
	except TypeError:
		# "resolution" is a list and can't be indexed by the string "height"
		pass

	try:
		config1["video_options.resolution.height"]
		assert False, "Flag has hierarchy which does not exist."
	except FlagNotFound:
		pass

	try:
		config1["video_options.resolution.height"]
		assert False, "Flag has hierarchy which does not exist."
	except KeyError:
		# `FlagNotFound` inherits from KeyError, so that behavior is consistent with a dict.
		pass

def test_methods():

	from GeekyGadgets.Configs import loadTOML, Config, ConfigCategory, FlagNotFound
	import os
	os.makedirs(os.path.splitext(__file__)[0], exist_ok=True)
	os.chdir(os.path.splitext(__file__)[0])
	
	config1 = loadTOML("tomlExample.toml")
	
	from copy import deepcopy
	config3 = deepcopy(CONFIG_DICT)

	config2 = Config.fromDict(config3)

	config3["new_section"] = ConfigCategory()
	
	assert config2 != config3

	config2.update(config3)

	assert config2 == config3

	config2["new_section.value"] = 2

	assert config2.get("new_section.other_value") == None

	config3["new_section"]["other_value"] = 6

	assert config2.get("new_section.other_value") == None

	assert config2 != config3
	
	config2.update(config3)
	
	assert config2 != config3

	config3.update(config2)

	assert config2 == config3

def test_operators():

	from GeekyGadgets.Configs import loadTOML, Config, ConfigCategory, FlagNotFound
	import os
	os.makedirs(os.path.splitext(__file__)[0], exist_ok=True)
	os.chdir(os.path.splitext(__file__)[0])
	
	config1 = loadTOML("tomlExample.toml")
	
	from copy import deepcopy
	config3 = deepcopy(CONFIG_DICT)

	config2 = Config.fromDict(config3)

	assert config1 | config1 == config1
	assert config2 | config2 == config2
	assert config3 | config3 == config3

	config3["new_section"] = ConfigCategory()

	assert config1 | config3 == config3
	assert config3 | config1 == config3
	assert config3 | config3 == config3

	config2["new_section.value"] = 2

	assert config2 | config3 != config3
	assert config3 | config2 != config3
	
	print(config2 | config3)
	print(type(config2 | config3))

	assert config2 | config3 == config2
	assert config3 | config2 == config2

	config3["new_section"]["other_value"] = 6
	
	assert config2 | config3 != config3
	assert config3 | config2 != config3

	assert config2 | config3 != config2
	assert config3 | config2 != config2

	config1 |= config3

	assert config1 | config2 != config2
	assert config1 | config3 == config3