import logging
import os
from .content import Site, Post, Content, Config, Published, Tags, Tag
from .Util import ArchiveOrg


class PyHugo:
    """Convenience wrapper bundling a `Config` and a `Site` for one Hugo site."""

    def __init__(self, base_dir, debug=False):
        self.base_dir = base_dir
        self.site = Site(base_dir)
        self.config = Config(base_dir)
        self.setDebug(debug)
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(os.environ.get("LOGLEVEL", "WARN"))

    def getDebug(self):
        return self.debug

    def setDebug(self, debug):
        if debug:
            self.logger.setLevel("DEBUG")
            self.logger.info("Set log level to debug")
        self.debug = debug

    def getSite(self):
        return self.site

    def getConfig(self):
        return self.config

    def getContent(self, sub_path=""):
        return Content(self.site.contentDir(), sub_path=sub_path, config=self.config)
