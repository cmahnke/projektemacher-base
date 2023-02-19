import os
import ctypes
import json

from .PyHugolib import PyHugolib

class Site(PyHugolib):
    def structure(self, hugo_dir):
        oad_config = self.library.buildStructure
        load_config.argtypes = [ctypes.c_char_p]
        load_config.restype = ctypes.c_char_p
