import os, inspect
from pathlib import Path
import ctypes

class PyHugolib:
    def __init__(self, lib = 'hugolib'):
        candidates = list(Path(os.path.dirname(inspect.getfile(PyHugolib))).glob("**/{}*.so".format(lib)))
        if len(candidates) < 1:
            raise "Cant find hugolib!"
        libfile = candidates[0]
        self.library = ctypes.cdll.LoadLibrary(libfile)

    def sanize_path(self, path):
        if not os.path.isabs(cfg_file):
            return os.path.abspath(cfg_file)
        return path

    def getDebug(self):
        get_debug = self.library.GetDebug
        get_debug.restypes = ctypes.c_bool
        debug_ptr = get_debug()
        ctypes.boolean_at(debug_ptr)

    def setDebug(self, debug):
        set_debug = self.library.SetDebug
        set_debug.argtypes = [ctypes.c_bool]
        set_debug(debug)

    def getEnv(self):
        get_env = self.library.GetEnv
        get_env.restypes = ctypes.c_char_p
        env_ptr = get_env()
        ctypes.string_at(env_ptr)

    def setEnv(self, env):
        set_env = self.library.SetEnv
        set_env.argtypes = [ctypes.c_char_p]
        set_env(env.encode('utf-8'))
