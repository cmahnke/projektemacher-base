import os, io, re, glob, pathlib, mimetypes, toml, logging
from pathlib import Path
import frontmatter
from .Util import Wikidata

class Site:
    _content_path = "./content/"
    config_files = ["config.toml", "hugo.toml"]

    def __init__(self, base_dir):
        config_file = self.guess_base(base_dir)
        self.base_dir = os.path.dirname(config_file)
        self.config = toml.load(config_file)
        self.translations = self.load_i18n()

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

    def load_i18n(self):
        translations = {}

        def _load_dir(path):
            if not os.path.exists(path) or not os.path.isdir(path):
                return
            for file in os.listdir(path):
                if file.endswith(".toml"):
                    lang = file[:-5][-2:]
                    if lang not in translations:
                        translations[lang] = {}
                    with open(os.path.join(path, file), "r") as f:
                        data = toml.load(f)
                        for key, value in data.items():
                            if key not in translations:
                                translations[key] = {}
                            translations[key][lang] = value

        themes = self.config.get("theme", [])
        if isinstance(themes, str):
            themes = [themes]
        themes_dir = self.config.get("themesDir", "themes")

        for theme in themes:
            theme_i18n = os.path.join(self.base_dir, themes_dir, theme, "i18n")
            _load_dir(theme_i18n)

        site_i18n = os.path.join(self.base_dir, "i18n")
        _load_dir(site_i18n)

        return translations

class Config(Site):
    def __init__(self, base_dir):
        if isinstance(base_dir, Site):
            base_dir = base_dir.base_dir
        super().__init__(base_dir)
        self.logger = logging.getLogger(__name__)
        self.base_dir = os.path.abspath(base_dir)
        self.config_file = self.guess_base(self.base_dir)
        if self.config_file is None:
            raise Exception(f"No config file found in {self.base_dir}")
        self.config = self.load_hugo_config()
        self.langs = list(self.config.get("languages", {"default": {}}).keys())
        self.defaultLanguage = self.config.get("defaultContentLanguage", None)
        if self.defaultLanguage is None:
            self.defaultLanguage = self.config.get("defaultcontentlanguage", None)
        

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

    def getAuthors(self):
        params = self.config.get("params", {})
        authors_data = params.get("authors", params.get("author"))
        if not authors_data:
            return []
        if isinstance(authors_data, list):
            return authors_data
        return [authors_data]

    def translate(self, key, lang=None):
        if not self.translations:
            self.logger.warning("No translations loaded, cannot translate key.")
            return None
        if lang is None:
            lang = self.defaultLanguage
            self.logger.warning(f"No language specified for translation key '{key}', using default language '{lang}'")
        if lang and lang in self.translations and key in self.translations and lang in self.translations[key]:
            translation = self.translations[key][lang]
            if "other" in translation:
                return translation["other"]
            if "many" in translation:
                return translation["many"]
            if "one" in translation:
                return translation["one"]
            return None
        return None

class Post:
    filePattern = r"(_?)index(\.([a-zA-Z-]){2,5})?\.md"
    filePatternMatcher = re.compile(filePattern)

    def __init__(self, path, lang=None, config=None):
        self.files = {}
        self.post = {}
        self.section = False
        self.resources = {}
        self.config = config
        if isinstance(path, dict):
            self._fromDict(path)
        elif isinstance(path, str):
            self._load(path, lang)
        elif isinstance(path, pathlib.Path) and lang is None:
            files = self._findContentFiles(path)
            self._fromDict(files)
        elif isinstance(path, pathlib.Path) and lang is not None:
            files = self._findContentFiles(path)
            if config and config.defaultLanguage and lang == config.defaultLanguage:
                lang = None
                self._fromDict(files[lang])
            else:
                raise NotImplementedError(f"Handling pathlib.Path with lang is not implemented yet! (path: {path}, lang: {lang}, config: {config}), files found: {files}")
        else:
            raise NotImplementedError(f"Handling {type(path)} is not implemented!")
        self._findResources(lang)
        self.path = pathlib.Path(self.files[list(self.files.keys())[0]]).parents[0]
        if not None in self.post:
            self.post[None] = self.post[list(self.post.keys())[0]]
            self.files[None] = self.files[list(self.files.keys())[0]]
        if self.files[None].startswith("_") or os.path.basename(self.files[None]).startswith("_"):
            self.section = True
        self.outputDir = self._outputDir(lang)
        self.draft = self.getDraft(lang)
        if config and config.defaultLanguage:
            self.post[config.defaultLanguage] = self.post[None]
        if config and not self.draft:
            self.url = self.config.baseURL().rstrip("/") + "/" + os.path.relpath(self.files[None], self.config.content_dir()).replace(".md", ".html").replace("\\", "/")
        else:
            self.url = None

    def _fromDict(self, dict):
        for lang, file in dict.items():
            self.files[lang] = file
            self._load(file, lang)

    def _findContentFiles(self, path: pathlib.Path):
        postFiles = {}
        for file in os.listdir(path):
            fileMatch = Post.filePatternMatcher.match(file)
            if fileMatch:
                lang = fileMatch.group(2)
                if lang is not None:
                    lang = lang.lstrip(".")
                postFiles[lang] = os.path.join(path, file)
                if lang is None and self.config and self.config.defaultLanguage:
                    postFiles[self.config.defaultLanguage] = os.path.join(path, file)
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

    def _findSection(self, lang):
        if self.section:
            return self
        parent = self.path.parent
        if parent == self.path:
            return None
        try:
            parentPost = Post(parent, lang, self.config)
            if parentPost.section:
                return parentPost
            else:
                return parentPost._findSection(lang)
        except Exception as e:
            logging.debug(f"No post found in {parent} for lang {lang}: {e}")
            return None

    def getOutputs(self, lang=None):
        outputs = []
        if "outputs" in self.post[lang].metadata:
            outputs.append(self.post[lang].metadata["outputs"])
        if self.config and "outputs" in self.config.config:
            outputs.append(self.config.config["outputs"])
        if not self.section:
            section = self._findSection(lang)
            if section and "outputs" in section.post[lang].metadata:
                outputs.append(section.post[lang].metadata["outputs"])
        return list(set(outputs))

    def getOutputDirs(self):
        outputDirs = {}
        if self.config is not None and "publishDir" in self.config.config and self.config.defaultLanguage:
            publish_dir = self.config.publishDir()
            rel_path = Path(os.path.relpath(self.files[None], self.config.content_dir())).parent
            outputDirs[self.config.defaultLanguage] = os.path.join(publish_dir, rel_path)
            for lang in self.config.langs:
                if lang != self.config.defaultLanguage:
                  outputDirs[lang] = os.path.join(publish_dir, lang, rel_path)
        return outputDirs

    def _outputDir(self, lang):
        if self.config is None:
            return None
        publish_dir = self.config.publishDir()
        rel_path = Path(os.path.relpath(self.files[lang], self.config.content_dir())).parent
        outputDirs = {}
        if lang and self.config and lang is not self.config.defaultLanguage:
            for l in self.config.langs:
                if l == lang:
                    outputDirs[l] = os.path.join(publish_dir, lang, rel_path)
        else:
            outputDirs[None] = os.path.join(publish_dir, rel_path)
        return outputDirs

    def _findOutputs(self, lang):
        buildins = ["index.html"]
        outputs = self.getOutputs(lang)
        outputfiles = []
        outputs.remove("html")
        if self.config is not None and "outputFormats" in self.config.config:
            for output in outputs:
                if output in self.config.config["outputFormats"]:
                    outputfiles.append(self.config.config["outputFormats"][output]["baseName"] + "." + output)
        if self.config is None:
            return None
        publish_dir = self.config.publishDir()
        rel_path = os.path.relpath(self.files[lang], self.config.content_dir()).replace(".md", ".html")
        if rel_path.endswith("index.html"):
            rel_path = rel_path[:-10]
        raise NotImplementedError(f"Output formats {outputs} are not implemented yet! (config: {self.config.config})")
    
    def getURL(self):
        return self.url

    def getContent(self, lang=None):
        if hasattr(self, "post"):
            return self.post[lang].content
        return None

    def getMetadata(self, lang=None):
        if hasattr(self, "post"):
            return self.post[lang].metadata
        return None

    def getWikidata(self, lang=None):
        metadata = self.getMetadata(lang)
        if metadata is None:
            return []
        wikidata = metadata.get("wikidata")
        if wikidata:
            if isinstance(wikidata, list):
                return wikidata
            return [wikidata]
        return []

    def addMetadata(self, key, value, lang=None):
        if self.config and lang == self.config.defaultLanguage:
            lang = None
        if hasattr(self, "post") and lang in self.post:
            self.post[lang].metadata[key] = value
            with open(self.files[lang], "wb") as f:
                frontmatter.dump(self.post[lang], f)

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

    def getDraft(self, lang=None):
        if "draft" in self.post[lang].metadata:
            return self.post[lang].metadata["draft"]
        return False

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

    def getKeywords(self, lang=None):
        keywords = set()
        
        if self.config:
          tags = self.getTags(lang)
          for tag_name, tag_obj in tags.items():
              translated_tag = self.config.translate(tag_name, lang)
              if translated_tag is not None:
                  keywords.add(translated_tag)
              else:
                keywords.add(tag_name)
              
              wd_items = tag_obj.getWikidata(lang)
              for wd in wd_items:
                  label = Wikidata.getLabel(wd, lang)
                  if label:
                      keywords.add(label)

        wd_items = self.getWikidata(lang)
        for wd in wd_items:
            label = Wikidata.getLabel(wd, lang)
            if label:
                keywords.add(label.strip())

        meta = self.getMetadata(lang)
        if meta and "keywords" in meta and meta["keywords"] is not None:
            for k in meta["keywords"].split(","):
                keywords.add(k.strip())

        return list(keywords)

    def __repr__(self):
        return f"{self.__class__.__name__}(files='{self.files}')"

class Content:
    DEFAULT_CONTENT_DIR = "./content/"

    def __init__(self, path=DEFAULT_CONTENT_DIR, sub_path="",config=None, sections=True):
        self.path = path
        self.sub_path = sub_path
        self.sections = sections
        self.config = config
        self.site = Site(Path(self.path).absolute().parent)
        self.posts = []
        self.iterPos = -1
        postsPaths = self._findPosts()
        for path in postsPaths.keys():
            post_variants = {}
            for lang, file in postsPaths[path]:
                post_variants[lang] = os.path.join(path, file)
            if post_variants:
                #p = Post(post_variants)
                self.posts.append(Post(post_variants, config=self.config))
        mimetypes.init()

    def __iter__(self):
        return self

    def __next__(self):

        self.iterPos += 1
        if self.iterPos < len(self.posts):
            if self.posts[self.iterPos].section:
                self.iterPos += 1
            return self.posts[self.iterPos]
        else:
            raise StopIteration

    def _findPosts(self):
        postFiles = {}
        search_path = self.path
        if self.sub_path != "" and self.sub_path is not None:
            search_path = os.path.join(search_path, self.sub_path)
        for subdir, dirs, files in os.walk(search_path):
            postFiles[subdir] = []
            for file in files:
                fileMatch = Post.filePatternMatcher.match(file)
                if fileMatch:
                    lang = fileMatch.group(2)
                    if lang is not None:
                        lang = lang.lstrip(".")
                    else:
                        if self.config and self.config.defaultLanguage:
                            postFiles[subdir].append((self.config.defaultLanguage, file))
                    postFiles[subdir].append((lang, file))
                    #if self.config and self.config.defaultLanguage:
                    #    postFiles[subdir].append((self.config.defaultLanguage, file))

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

class Published:
    def __init__(self, config, pattern="*.html"):
        self.config = config
        self.publishDir = config.publishDir()
        self.baseUrl = config.baseURL().rstrip("/")
        self.pattern = pattern
    
    def postList(self, subDir=""):
        urls = []
        search_path = self.publishDir / subDir
        for file_path in search_path.rglob(self.pattern):
            relative_path = file_path.relative_to(self.publishDir)
            url_path = relative_path.as_posix()

            if url_path.endswith("index.html"):
                url_path = url_path[:-10]

            full_url = f"{self.baseUrl}/{url_path}".rstrip("/") + "/"
            urls.append(full_url)
        return urls