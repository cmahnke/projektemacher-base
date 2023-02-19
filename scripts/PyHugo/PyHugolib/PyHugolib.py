import os, glob
import ctypes

class PyHugolib:
    def __init__(self, lib = 'hugolib'):
        libfile = glob.glob("build/{}*.so".format(lib))[0]
        self.library = ctypes.cdll.LoadLibrary(libfile)

    def sanize_path(self, path):
        if not os.path.isabs(cfg_file):
            return os.path.abspath(cfg_file)
        return path
