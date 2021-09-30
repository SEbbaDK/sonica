import os

from mediafile import MediaFile

from song import Song

class Library:
    def __init__(self, folder: str):
        self.base = folder
        self.current_set = None
        self.index = []
        self.reindex()

    def reindex(self):
        for (name, folders, files) in os.walk(self.base):
            for f in files:
                path = name + "/" + f
                print(path)
                m = MediaFile(path)
                print(sorted([f for f in m.fields()]))
                m.update({ 'tags': ['test', 'test2'] })
                m.save()


    def search(self, query: str):
        return []

