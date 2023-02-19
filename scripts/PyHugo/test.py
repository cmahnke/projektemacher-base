import os, glob

import json

from PyHugolib import *


hugo_file = "config.toml"
hugo_dir = "../../../../"
hugo_config = hugo_dir + hugo_file

cfg = Config().load(hugo_config)


print(cfg["baseURL"])
