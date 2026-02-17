import os, io, re, glob, pathlib, mimetypes, toml, logging
from pathlib import Path
import frontmatter

class Site:
    _content_path = "./content/"
    config_files = ["config.toml", "hugo.toml"]

    def __init__(self, base_dir):
        config_file = self.guess_base(base_dir)
        self.base_dir = os.path.dirname(config_file)
        self.config = toml.load(config_file)

    def guess_base(self, start_dir, configs = config_files):
        current_dir = os.path.abspath(start_dir)

        while True:
            for filename in configs:
                config_path = os.path.join(current_dir, filename)
                if os.path.exists(config_path) and os.path.isfile(config_path):
                    return config_path

            parent_dir = os.path.dirname(current_dir)
            if parent_dir == current_dir:
                break
            current_dir = parent_dir
        return None

    def content_dir(self):
        return os.path.join(self.base_dir, self._content_path)

class Config(Site):
    def __init__(self, base_dir):
        self.logger = logging.getLogger(__name__)
        self.base_dir = os.path.abspath(base_dir)
        self.config_file = self.guess_base(self.base_dir)
        if self.config_file is None:
            raise Exception(f"No config file found in {self.base_dir}")
        self.config = self.load_hugo_config()

    def load_hugo_config(self):
        self.logger.debug(f"Loading Hugo config from {self.base_dir} ({self.config_file})")
        config = {}
        config_dir = os.path.join(self.base_dir, "config", "_default")
        
        with open(self.config_file, "r") as f:
            config = toml.load(f)
        if os.path.exists(config_dir):
            for filename in os.listdir(config_dir):
                if filename.endswith(".toml"):
                    with open(os.path.join(config_dir, filename), "r") as f:
                        data = toml.load(f)
                        key = filename.replace(".toml", "")
                        if key == "hugo" or key == "config":
                            config.update(data)
                        else:
                            config[key] = data
        return config
    
    def baseURL(self):
        return self.config.get("baseURL", "http://localhost:1313/")
    
    def publishDir(self):
        return self.config.get("publishDir", "public")

class Post:
    filePattern = r"(_?)index(\.([a-zA-Z-]){2,5})?\.md"
    filePatternMatcher = re.compile(filePattern)

    def __init__(self, path, lang=None):
        self.files = {}
        self.post = {}
        self.section = False
        self.resources = {}
        if isinstance(path, dict):
            self._fromDict(path)
        elif isinstance(path, str):
            self._load(path, lang)
        elif isinstance(path, pathlib.Path) and lang is None:
            files = Post._findContentFiles(path)
            self._fromDict(files)
        else:
            raise NotImplementedError(f"Handling {type(path)} is not implemented!")
        self._findResources(lang)
        self.path = pathlib.Path(self.files[list(self.files.keys())[0]]).parents[0]
        if not None in self.post:
            self.post[None] = self.post[list(self.post.keys())[0]]
            self.files[None] = self.files[list(self.files.keys())[0]]
        if self.files[None].startswith("_"):
            self.section = True

    def _fromDict(self, dict):
        for lang, file in dict.items():
            self.files[lang] = file
            self._load(file, lang)

    def _findContentFiles(path: pathlib.Path):
        postFiles = {}
        for file in os.listdir(path):
            fileMatch = Post.filePatternMatcher.match(file)
            if fileMatch:
                lang = fileMatch.group(2)
                postFiles[lang] = os.path.join(path, file)
        return postFiles

    def _findResources(self, lang):
        if not lang in self.resources:
            self.resources[lang] = []
        if "resources" in self.post[lang].metadata:
            for resource in self.post[lang].metadata["resources"]:
                self.resources[lang].append(resource)

    def _load(self, path, lang):
        if os.path.isdir(path):
            raise Exception(f"{path} is a directory")
        with open(path) as f:
            self.post[lang] = frontmatter.load(f)

    def getContent(self, lang=None):
        if hasattr(self, "post"):
            return self.post[lang].content
        return None

    def getMetadata(self, lang=None):
        if hasattr(self, "post"):
            return self.post[lang].metadata
        return None

    def getResources(self, lang=None):
        if len(self.resources[lang]) == 0:
            return None
        return self.resources[lang]

    def getResourcesByType(self, type, lang=None):
        retRes = []
        if len(self.resources[lang]) == 0:
            return None
        for r in self.resources[lang]:
            if "src" in r:
                t = mimetypes.guess_type(r["src"])
                if t[0].startswith(type):
                    retRes.append(r)
        if len(retRes) == 0:
            return None
        return retRes

    def getTags(self, lang=None):
        tags = {}
        if "tags" in self.post[lang].metadata:
            tag_names = self.post[lang].metadata["tags"]
            for tag in tag_names:
                if tag == "":
                    continue
                path = self.path
                if isinstance(path, str):
                    path = Path(path)
                tags[tag] = Tag(tag, lang, path)
        return tags

    def __repr__(self):
        return f"{self.__class__.__name__}(files='{self.files}')"

class Content:
    def __init__(self, path="content"):
        self.path = path
        self.site = Site(Path(self.path).absolute().parent)
        self.posts = []
        self.iterPos = -1
        postsPaths = self._findPosts()
        for path in postsPaths.keys():
            post_variants = {}
            for lang, file in postsPaths[path]:
                post_variants[lang] = os.path.join(path, file)
            if post_variants:
                p = Post(post_variants)
                self.posts.append(Post(post_variants))
        mimetypes.init()

    def __iter__(self):
        return self

    def __next__(self):
        self.iterPos += 1
        if self.iterPos < len(self.posts):
            return self.posts[self.iterPos]
        else:
            raise StopIteration

    def _findPosts(self):
        postFiles = {}
        for subdir, dirs, files in os.walk(self.path):
            postFiles[subdir] = []
            for file in files:
                fileMatch = Post.filePatternMatcher.match(file)
                if fileMatch:
                    lang = fileMatch.group(2)
                    postFiles[subdir].append((lang, file))

        return postFiles

class Tags(Content):
    def __init__(self, path="tags"):
        super(path)

class Tag (Post):
    _tag_path = "./tags/"

    def __init__(self, tag, lang=None, ctx = None):
        self.tag = tag
        self.lang = lang
        self.files = {}
        if ctx is not None:
            self.site = Site(ctx)
            self.tag_dir = Path(self.site.content_dir()).joinpath(self._tag_path, tag.replace(" ", "-"))
            if os.path.exists(self.tag_dir):
                super().__init__(self.tag_dir, self.lang)
