import os
import ctypes
import json

from .PyHugolib import PyHugolib

class Site(PyHugolib):
    def structure(self, hugo_dir):
        build_structure = self.library.BuildStructure
        build_structure.argtypes = [ctypes.c_char_p]
        build_structure.restype = ctypes.c_char_p
        if not os.path.isabs(hugo_dir):
            hugo_dir = os.path.abspath(hugo_dir)

        structure_ptr = build_structure(hugo_dir.encode('utf-8'))
        return json.loads(ctypes.string_at(structure_ptr))
