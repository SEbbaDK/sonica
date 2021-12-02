import os

import tagger
from song import Song

class Library:
    def __init__(self, folder: str):
        self.base = folder
        self.current_set = None
        self.index: list[Song] = []

        self.reindex()

    def path(self):
        return self.base

    def reindex(self):
        self.index = []
        for (pathname, folders, files) in os.walk(self.base):
            for filename in files:
                path = pathname + "/" + filename
                self.index_file(path)

    def size(self):
        return len(self.index)

    def search(self, query: str):
        q = query.lower()
        return [
            s for s in self.index
            if q in s.title.lower() or q in s.artist.lower()
        ]

    def all_tags(self):
        return set(sum([ s.tags for s in self.index ], []))

    def index_file(self, path):
        f = tagger.TaggedFile(path)
        song = Song(
            path,
            f.title(),
            f.artist(),
            f.album(),
            f.art(),
        )
        self.index.append(song)
        return song

    def get_song(self, path):
        for s in self.index:
            if s.path == path:
                return s
        return self.index_file(path)
        raise Exception("No song with path: " + path)

