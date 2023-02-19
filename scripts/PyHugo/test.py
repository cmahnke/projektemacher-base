import os, glob

import json

from PyHugolib import *


hugo_file = "config.toml"
hugo_dir = "../../../../"
hugo_config = hugo_dir + hugo_file

PyHugolib().setDebug(True)
cfg = Config().load(hugo_config)


print(cfg["baseURL"])
