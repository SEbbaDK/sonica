from dataclasses import dataclass

@dataclass
class SongChoice:
    title: str
    artist: str
    # Function that calls the callback with the filename when done
    # (usually after downloading but not necessarily)
    def choose(self, callback):
        raise Exception("Choose was called but not implemented")

    def __str__(self):
        return f"**{self.title}** by *{self.artist}*"

class Engine:
    name: str = None
    description: str = None
    command: str = None

    def search(self, query: str):
        pass

