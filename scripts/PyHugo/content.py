import os, io, re, glob, pathlib
import frontmatter

class Post:
    filePattern = "(_?)index(\.([a-zA-Z-]){2,5})?\.md"
    filePatternMatcher = re.compile(filePattern)

    def __init__(self, path, lang = None):
        self.files = {}
        self.post = {}
        self.section = False
        if isinstance(path, dict):
            self._fromDict(path)
        elif isinstance(path, str):
            self._load(self, lang, path)
        elif isinstance(path, pathlib.Path) and lang is None:
            files = Post._findContentFiles(path)
            self._fromDict(files)
        else:
            raise NotImplementedError(f"Handling {type(path)} is not implemented!")

        self.path = pathlib.Path(self.files[list(self.files.keys())[0]]).parents[0]
        if not None in self.post:
            self.post[None] = self.post[list(self.post.keys())[0]]
            self.files[None] = self.files[list(self.files.keys())[0]]
        if self.files[None].startswith('_'):
            self.section = True

    def _fromDict(self, dict):
        for lang, file in dict.items():
            self.files[lang] = file
            self._load(lang, file)

    def _findContentFiles(path: pathlib.Path):
        postFiles = {}
        for file in os.listdir(path):
            fileMatch = Post.filePatternMatcher.match(file)
            if fileMatch:
                lang = fileMatch.group(2)
                postFiles[lang] = os.path.join(path, file)
        return postFiles

    def _load(self, lang, path):
        with open(path) as f:
            self.post[lang] = frontmatter.load(f)

    def getContent(self, lang = None):
        return self.post[lang].content

    def getMetadata(self, lang = None):
        return self.post[lang].metadata

class Content:
    def __init__(self, path='content'):
        self.path = path
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

    def __iter__(self) :
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
