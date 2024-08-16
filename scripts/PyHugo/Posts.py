import os, io, re, yaml, glob
from termcolor import cprint


class Posts:
    filePattern = "(_?)index(\.([a-zA-Z-]){2,5})?\.md"
    paths = []

    def __init__(self, paths):
        for path in paths:
            if "*" in path:
                self.paths.extend(glob.glob(path))
            else:
                self.paths.append(path)

    def postList(self):
        posts = []
        files = self.listFiles()
        for file in files:
            metadata = self.readMetadata(file)
            metadata.update({"__source": file})
            posts.append(metadata)

        return posts

    def listFiles(self):
        postFiles = []
        cFilePattern = re.compile(self.filePattern)
        for contentPath in self.paths:
            for subdir, dirs, files in os.walk(contentPath):
                for file in files:
                    fileMatch = cFilePattern.match(file)
                    if fileMatch:
                        lang = fileMatch.group(2)
                        contentFile = os.path.join(subdir, file)
                        postFiles.append(contentFile)

        return postFiles

    def readMetadata(self, file):
        post = io.open(file, mode="r", encoding="utf-8").read()
        header = re.sub(r"^---$.(.*?)^---$.*", "\\1", post, 0, re.MULTILINE | re.DOTALL)
        try:
            post = yaml.load(header, Loader=yaml.FullLoader)
        except yaml.YAMLError as exc:
            if hasattr(exc, "problem_mark"):
                mark = exc.problem_mark
                cprint(
                    "Error in {} position: ({}:{})".format(
                        file, mark.line + 1, mark.column + 1
                    ),
                    "red",
                )
        except Exception as inst:
            cprint("Error in %s".format(file), "red")

        return post
