import os
import ctypes
import json

from .PyHugolib import PyHugolib

class Config(PyHugolib):
    def load(self, cfg_file, hugo_dir = ""):
        load_config = self.library.loadConfig
        load_config.argtypes = [ctypes.c_char_p]
        load_config.restype = ctypes.c_char_p
        if not os.path.isabs(cfg_file):
            cfg_file = os.path.abspath(cfg_file)
        if hugo_dir == "":
            hugo_dir = os.path.dirname(cfg_file)

        config_pointer = load_config(cfg_file.encode('utf-8'))
        return json.loads(ctypes.string_at(config_pointer))
