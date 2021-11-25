from engine import Engine, SongChoice

class LibraryEngine(Engine):
    name = "Library"
    description = "Plays from the downloaded songs"

    def __init__(self, library, options):
        self.library = library

    class LibrarySongChoice(SongChoice):
        def __init__(self, song):
            self.song = song

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

