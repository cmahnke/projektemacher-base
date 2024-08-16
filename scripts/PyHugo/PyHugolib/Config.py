import os
import ctypes
import json

from .PyHugolib import PyHugolib


class Config(PyHugolib):
    def load(self, hugo_dir):
        load_config = self.library.LoadConfig
        load_config.argtypes = [ctypes.c_char_p]
        load_config.restype = ctypes.c_char_p
        if not os.path.isabs(hugo_dir):
            hugo_dir = os.path.abspath(hugo_dir)

        config_ptr = load_config(hugo_dir.encode("utf-8"))
        return json.loads(ctypes.string_at(config_ptr))

    def loadFile(self, cfg_file):
        load_config = self.library.LoadConfigFromFile
        load_config.argtypes = [ctypes.c_char_p]
        load_config.restype = ctypes.c_char_p
        if not os.path.isabs(cfg_file):
            cfg_file = os.path.abspath(cfg_file)

        config_ptr = load_config(cfg_file.encode("utf-8"))
        return json.loads(ctypes.string_at(config_ptr))
