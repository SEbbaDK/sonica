import os

import taglib

from song import Song

class Library:
    def __init__(self, folder: str):
        self.base = folder
        self.current_set = None
        self.index = []
        self.size = 0

        self.reindex()

    def reindex(self):
        new_index = []
        for (pathname, folders, files) in os.walk(self.base):
            for filename in files:
                path = pathname + "/" + filename
                f = taglib.File(path)
                s = Song(path, f.tags['TITLE'][0], f.tags['ARTIST'][0], f.tags['TAGS'])
                new_index.append(s)
        self.size = len(new_index)
        self.index = new_index


    def search(self, query: str):
        q = query.lower()
        return [
            s for s in self.index
            if q in s.title.lower() or q in s.artist.lower()
        ]

    def all_tags(self):
        return set(sum([ s.tags for s in self.index ], []))

