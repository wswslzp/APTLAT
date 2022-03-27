import os 

class FileFinder(object):
    def __init__(self):pass 

    def fileMatcher(self, f:str): ...

    def findFile(self, file_matcher):
        flist = []
        for p, _, fs in os.walk("."):
            for f in fs:
                path = os.path.join(p, f)
                if file_matcher(f):
                    flist.append(path)
        return flist

    def __call__(self):
        return self.findFile(self.fileMatcher)

class FileExtFinder(FileFinder):
    def __init__(self, ext:str): 
        FileFinder.__init__(self)
        self.ext = ext

    def fileMatcher(self, f: str):
        import re 
        return re.search(r"\w*\.{ext}".format(ext=self.ext), f)

class FileNameFinder(FileFinder):
    def __init__(self, name: str):
        FileFinder.__init__(self)
        self.name = name

    def fileMatcher(self, f:str):
        return f == self.name

if __name__ == "__main__":
    finder = FileExtFinder("py")
    print(finder())