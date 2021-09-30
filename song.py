from dataclasses import dataclass

@dataclass
class Song:
    path: str
    title: str
    artist: str
    tags: list

