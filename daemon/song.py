from dataclasses import dataclass

@dataclass
class Song:
    path: str
    title: str
    artist: str
    album: str
    tags: list

    def __str__(self):
        return f"**{self.title}** by *{self.artist}*"

    def __hash__(self):
        return hash(self.path)
