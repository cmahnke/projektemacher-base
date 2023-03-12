import os, glob

import json

from PyHugolib import *


hugo_file = "config.toml"
hugo_dir = "../../../../"
hugo_config = hugo_dir + hugo_file
os.environ["LOGLEVEL"] = "INFO"

hugo = PyHugolib()

hugo.setDebug(True)
cfg = Config().load(hugo_config)

structure = Site().structure(hugo_config)

print("BaseURL is {}".format(cfg["baseURL"]))
print("Config is {}".format(cfg))

print("Structure is {}".format(structure))

print("Debug is {} ".format(hugo.getDebug()))
print("Env is {} ".format(hugo.getEnv()))
