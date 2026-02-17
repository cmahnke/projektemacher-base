import logging
import os
from .content import Site, Post, Content, Config
from .Posts import Posts, Published

class PyHugo:
    def __init__(self, base_dir, debug=False):
        _handler = logging.StreamHandler()
        _formatter = logging.Formatter(
            "{asctime}.{msecs:0<6.0f} {filename}:{lineno}: [{levelname}] {message}",
            datefmt="%H:%M:%S",
            style="{",
        )
        _handler.setFormatter(_formatter)
        self.base_dir = base_dir
        self.site = Site(base_dir)
        self.config = Config(base_dir)
        self.setDebug(debug)
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(os.environ.get("LOGLEVEL", "WARN"))
        #logger.addHandler(_handler)

    def getDebug(self):
        return self.debug 

    def setDebug(self, debug):
        self.logger.setLevel("DEBUG")
        self.logger.info("Set Log level to debug")
        self.debug = debug