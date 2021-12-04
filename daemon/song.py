from dataclasses import dataclass

@dataclass
class Song:
    path: str
    title: str
    artist: str
    album: str
    art: (str, bytes)
    length: float

    def __str__(self):
        return f"**{self.title}** by *{self.artist}*"

    def __hash__(self):
        return hash(self.path)
