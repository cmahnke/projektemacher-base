import os, io, re, glob, pathlib, mimetypes, toml, logging, sys
from pathlib import Path
import frontmatter
#sys.path.append(str(Path(__file__).parent))
from PyHugo.Util import Wikidata


def _deepMerge(base, overlay):
    """Merge `overlay` into `base`, recursing into dicts instead of replacing them."""
    for key, value in overlay.items():
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            _deepMerge(base[key], value)
        else:
            base[key] = value

class Site:
    CONTENT_PATH = "./content/"
    config_files = ["config.toml", "hugo.toml", "config/_default/config.toml", "config/_default/hugo.toml"]

    def __init__(self, base_dir):
        config_file = self.guess_base(base_dir)
        if config_file is None:
            raise ValueError(f"Could't find config file in {base_dir}")
        # Configurations in the config directory are relative to the site root
        if os.path.basename(os.path.dirname(config_file)) == "_default":
            self.base_dir = os.path.dirname(os.path.dirname(os.path.dirname(config_file)))
        else:
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

    def contentDir(self):
        return os.path.join(self.base_dir, self.CONTENT_PATH)

    def load_i18n(self):
        translations = {}

        def _load_dir(path):
            if not os.path.exists(path) or not os.path.isdir(path):
                return
            for file in os.listdir(path):
                if not file.endswith(".toml"):
                    continue
                # Language is the last dotted segment of the file name (theme.en.toml -> en, en.toml -> en)
                lang = os.path.splitext(os.path.splitext(file)[0])[1].lstrip(".")
                if not lang:
                    logging.debug(f"Skipping i18n file '{file}' without language suffix")
                    continue
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
                            _deepMerge(config, data)
                        else:
                            if key in config and isinstance(config[key], dict) and isinstance(data, dict):
                                _deepMerge(config[key], data)
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
        self._unsuffixed = False
        if isinstance(path, dict):
            self._fromDict(path)
        elif isinstance(path, str):
            self.post[lang] = self._load(path, lang)
            self.files[lang] = path
            self._unsuffixed = lang is None
        elif isinstance(path, pathlib.Path):
            files = self._findContentFiles(path)
            if not files:
                raise ValueError(f"No content files found in {path}")
            if lang is not None and lang in files:
                self._fromDict({lang: files[lang]})
            elif lang is not None and lang not in files and not (config and config.defaultLanguage and lang == config.defaultLanguage):
                raise NotImplementedError(f"Handling pathlib.Path with lang is not implemented yet! (path: {path}, lang: {lang}, config: {config}), files found: {files}")
            else:
                # Without a language (or for the default language) the unsuffixed file is used
                self._fromDict({None: files[None]})
        else:
            raise NotImplementedError(f"Handling {type(path)} is not implemented!")
        self._findResources()
        self.path = pathlib.Path(self.files[list(self.files.keys())[0]]).parents[0]
        if None not in self.post:
            self.post[None] = self.post[list(self.post.keys())[0]]
            self.files[None] = self.files[list(self.files.keys())[0]]
        if os.path.basename(self.files[None]).startswith("_"):
            self.section = True
        self.outputDir = self._outputDir(lang)
        self.draft = self.getDraft(lang)
        # The unsuffixed file represents the default language
        if config and config.defaultLanguage and self._unsuffixed and config.defaultLanguage not in self.post:
            self.post[config.defaultLanguage] = self.post[None]
            if config.defaultLanguage not in self.files:
                self.files[config.defaultLanguage] = self.files[None]
        if config and not self.draft:
            self.url = self.config.baseURL().rstrip("/") + "/" + os.path.relpath(self.files[None], self.config.contentDir()).replace(".md", ".html").replace("\\", "/")
        else:
            self.url = None

    def _resolveLang(self, lang=None):
        """Resolve `lang` to a loaded language, falling back to the post's default."""
        if lang in self.post:
            return lang
        if None in self.post:
            return None
        if self.post:
            return next(iter(self.post))
        return None

    def _fromDict(self, dict):
        loaded = {}
        for lang, file in dict.items():
            self.files[lang] = file
            # The same file can be referenced by multiple languages (unsuffixed default language)
            if file not in loaded:
                loaded[file] = self._load(file, lang)
            self.post[lang] = loaded[file]
        self._unsuffixed = None in dict

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

    def _findResources(self, lang=None):
        langs = [lang] if lang is not None else list(self.post.keys())
        for l in langs:
            if l not in self.resources:
                self.resources[l] = []
            if "resources" in self.post[l].metadata:
                for resource in self.post[l].metadata["resources"]:
                    self.resources[l].append(resource)

    def _load(self, path, lang):
        if os.path.isdir(path):
            raise Exception(f"{path} is a directory")
        with open(path) as f:
            return frontmatter.load(f)

    def _findSection(self, lang):
        if self.section:
            return self
        parent = self.path.parent
        if parent == self.path:
            return None
        try:
            parentPost = Post(pathlib.Path(parent), lang, self.config)
            if parentPost.section:
                return parentPost
            else:
                return parentPost._findSection(lang)
        except Exception as e:
            logging.debug(f"No post found in {parent} for lang {lang}: {e}")
            return None

    def getOutputs(self, lang=None):
        lang = self._resolveLang(lang)
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
            rel_path = Path(os.path.relpath(self.files[None], self.config.contentDir())).parent
            outputDirs[self.config.defaultLanguage] = os.path.join(publish_dir, rel_path)
            for lang in self.config.langs:
                if lang != self.config.defaultLanguage:
                  outputDirs[lang] = os.path.join(publish_dir, lang, rel_path)
        return outputDirs

    def _outputDir(self, lang):
        if self.config is None:
            return None
        publish_dir = self.config.publishDir()
        rel_path = Path(os.path.relpath(self.files[lang], self.config.contentDir())).parent
        outputDirs = {}
        if lang and self.config and lang != self.config.defaultLanguage:
            for l in self.config.langs:
                if l == lang:
                    outputDirs[l] = os.path.join(publish_dir, lang, rel_path)
        else:
            outputDirs[None] = os.path.join(publish_dir, rel_path)
        return outputDirs

    def getFile(self, lang=None):
        return self.files[self._resolveLang(lang)]

    def getURL(self):
        return self.url

    def getContent(self, lang=None):
        if hasattr(self, "post") and self.post:
            return self.post[self._resolveLang(lang)].content
        return None

    def getMetadata(self, lang=None):
        if hasattr(self, "post") and self.post:
            return self.post[self._resolveLang(lang)].metadata
        return {}

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
            with open(self.files[lang], "w", encoding="utf-8") as f:
                frontmatter.dump(self.post[lang], f)

    def getResources(self, lang=None):
        lang = self._resolveLang(lang)
        if lang not in self.resources and None in self.resources:
            lang = None
        if len(self.resources.get(lang, [])) == 0:
            return None
        return self.resources[lang]

    def getResourcesByType(self, type, lang=None):
        lang = self._resolveLang(lang)
        if lang not in self.resources and None in self.resources:
            lang = None
        retRes = []
        if len(self.resources.get(lang, [])) == 0:
            return None
        for r in self.resources[lang]:
            if "src" in r:
                t = mimetypes.guess_type(r["src"])
                if t[0] is not None and t[0].startswith(type):
                    retRes.append(r)
        if len(retRes) == 0:
            return None
        return retRes

    def getDraft(self, lang=None):
        metadata = self.getMetadata(lang)
        if "draft" in metadata:
            return metadata["draft"]
        return False

    def getTags(self, lang=None):
        tags = {}
        metadata = self.getMetadata(lang)
        if "tags" in metadata:
            tag_names = metadata["tags"]
            if isinstance(tag_names, str):
                tag_names = [tag_names]
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

    def getParam(self, name: str, lang=None):
        metadata = self.getMetadata(lang)
        found_in_root = name in metadata
        params = metadata.get("params")
        found_in_params = isinstance(params, dict) and name in params

        if found_in_root and found_in_params:
            raise RuntimeError(f"Key '{name}' was found in both root and 'params'.")

        if found_in_root:
            return metadata[name]

        if found_in_params:
            return params[name]

        return None

    def __repr__(self):
        return f"{self.__class__.__name__}(files='{self.files}')"

class Content:
    DEFAULT_CONTENT_DIR = Site.CONTENT_PATH

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
    def __init__(self, path="tags", config=None):
        super().__init__(path=path, config=config)

class Tag(Post):
    _tag_path = "./tags/"

    def __init__(self, tag, lang=None, ctx = None):
        self.tag = tag
        self.lang = lang
        self.files = {}
        self.post = {}
        self.resources = {}
        self.section = False
        self.config = None
        if ctx is not None:
            self.site = Site(ctx)
            self.tag_dir = Path(self.site.contentDir()).joinpath(self._tag_path, tag.replace(" ", "-"))
            if os.path.exists(self.tag_dir):
                # Load all language variants of the tag page
                super().__init__(self.tag_dir)

class Published:
    def __init__(self, config, pattern="*.html"):
        self.config = config
        # Hugo resolves a relative publishDir against the site's base directory
        self.publishDir = Path(config.base_dir) / config.publishDir()
        self.baseUrl = config.baseURL().rstrip("/")
        self.pattern = pattern

    def postList(self, subDir=""):
        urls = []
        search_path = self.publishDir
        if subDir:
            search_path = search_path / subDir
        for file_path in search_path.rglob(self.pattern):
            relative_path = file_path.relative_to(self.publishDir)
            url_path = relative_path.as_posix()

            if url_path.endswith("index.html"):
                url_path = url_path[:-10]

            full_url = f"{self.baseUrl}/{url_path}".rstrip("/") + "/"
            urls.append(full_url)
        return urls
