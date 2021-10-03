from dataclasses import dataclass
from collections.abc import Callable

import deemix
from deezer import Deezer, TrackFormats
from youtube_dl import YoutubeDL
from youtube_search import YoutubeSearch

from song import Song

@dataclass
class SongChoice:
    title: str
    artist: str
    # Function that returns the filename
    # (usually after downloading)
    get_filename: Callable[[], str]

    def __str__(self):
        return f"**{self.title}** by *{self.artist}*"

class Player:
    def get_command(self):
        pass
    def search(self, query: str):
        pass

    def is_command(self, command: str):
        return command.startswith(self.get_command() + " ")
    def strip_command(self, string: str):
        return string[len(self.get_command()) + 1:]

class LibraryPlayer(Player):
    def __init__(self, library):
        self.library = library

    def get_command(self):
        return "play"
    def search(self, query: str):
        return [
        	SongChoice(s.title, s.artist, lambda: s.path)
        	for s in self.library.search(query)
        ]

class DeezPlayer(Player):
    def __init__(self, arl):
        self.dz = Deezer()
        self.dz.login_via_arl(arl)

    def get_command(self):
        return "deez"
    def search(self, query: str):
        results = self.dz.api.search(query)['data']

        def download(link: str):
            downloader = deemix.generateDownloadObject(self.dz, link, TrackFormats.MP3_320)
            Downloader(self.dz, downloader).start()

        return [
            SongChoice(x['title'], x['artist']['name'], lambda: download(x['link']))
            for x in results[0:9]
        ]


class YoutubePlayer(Player):
    def __init__(self):
        self.ytdl = YoutubeDL()

    def get_command(self):
        return "yt"
    def search(self, query: str):
        results = YoutubeSearch(query).videos

        def download(link: str):
            pass

        return [
            SongChoice(x['title'], x['artist'], lambda: download(x['id']))
            for x in results[0:9]
        ]

