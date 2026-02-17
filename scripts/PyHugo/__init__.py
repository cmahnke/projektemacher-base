from .content import Site, Post, Content, Config
from .Posts import Posts, Published

class PyHugo:
    def __init__(self, base_dir):
        self.base_dir = base_dir
        self.site = Site(base_dir)
        self.config = Config(base_dir)