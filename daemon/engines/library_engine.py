from dataclasses import dataclass
from engine import Engine, SongChoice

class LibraryEngine(Engine):
    name = "Library"
    description = "Plays from the downloaded songs"
    # The library is instantaneous, so it should rank first
    rank = 1

    def __init__(self, library, options):
        self.library = library

    @dataclass
    class LibrarySongChoice(SongChoice):
        song : None

        def choose(self):
            return self.song.path

    def search(self, query: str):
        return [
            self.LibrarySongChoice(
                title = s.title,
                artist = s.artist,
                song = s,
            )
            for s in self.library.search(query)
        ]

