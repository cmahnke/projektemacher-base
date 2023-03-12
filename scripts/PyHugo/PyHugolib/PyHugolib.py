import os, inspect
from pathlib import Path
import ctypes
import logging

class PyHugolib:
    _library_pattern = '**/hugolib*.so'
    _handler = logging.StreamHandler()
    _formatter = logging.Formatter('{asctime}.{msecs:0<6.0f} {filename}:{lineno}: [{levelname}] {message}', datefmt='%H:%M:%S',  style='{')
    _handler.setFormatter(_formatter)
    logger = logging.getLogger(__name__)
    logger.setLevel(os.environ.get("LOGLEVEL", "WARN"))
    logger.addHandler(_handler)

    def __init__(self):
        self.library = self._load_lib()

    def _load_lib(self):
        candidates = list(Path(os.path.dirname(inspect.getfile(PyHugolib))).glob(PyHugolib._library_pattern))
        if len(candidates) < 1:
            raise "Can't find hugolib!"
        self.logger.info("Loading Library {}".format(candidates[0]))
        return ctypes.cdll.LoadLibrary(candidates[0])

    def _sanize_path(path):
        if not os.path.isabs(cfg_file):
            return os.path.abspath(cfg_file)
        return path

    def getDebug(self):
        get_debug = self.library.GetDebug
        get_debug.argtypes = None
        get_debug.restypes = ctypes.c_uint
        debug = get_debug(None)
        return bool(debug)

    def setDebug(self, debug):
        self.logger.setLevel('DEBUG')
        self.logger.info('Set Log level to debug')
        set_debug = self.library.SetDebug
        set_debug.argtypes = [ctypes.c_bool]
        set_debug(debug)

    def getEnv(self):
        get_env = self.library.GetEnv
        #get_env.argtypes = [ctypes.c_void_p]
        get_env.argtypes = None
        get_env.restypes = ctypes.c_char_p
        env_ptr = get_env()
        #return ctypes.cast(env_ptr, ctypes.c_char_p).value
        return ctypes.string_at(env_ptr)

    def setEnv(self, env):
        set_env = self.library.SetEnv
        set_env.argtypes = [ctypes.c_char_p]
        set_env(env.encode('utf-8'))

    def _strtobool (val):
        """Convert a string representation of truth to true (1) or false (0).
        True values are 'y', 'yes', 't', 'true', 'on', and '1'; false values
        are 'n', 'no', 'f', 'false', 'off', and '0'.  Raises ValueError if
        'val' is anything else.
        """
        val = val.lower()
        if val in ('y', 'yes', 't', 'true', 'on', '1'):
            return 1
        elif val in ('n', 'no', 'f', 'false', 'off', '0'):
            return 0
        else:
            raise ValueError("invalid truth value %r" % (val,))
