from dataclasses import dataclass
from collections.abc import Callable

import deemix
import deemix.settings
from deemix.downloader import Downloader
from deezer import Deezer, TrackFormats
from youtube_dl import YoutubeDL
from youtube_search import YoutubeSearch

from song import Song
from library import Library
from playlist import Playlist

@dataclass
class SongChoice:
    title: str
    artist: str
    # Function that calls the callback with the filename when done
    # (usually after downloading but not necessarily)
    choose: Callable[[Callable[[], None]], str]

    def __str__(self):
        return f"**{self.title}** by *{self.artist}*"

class Player:
    name: str = None
    description: str = None
    command: str = None

    def search(self, query: str):
        pass

    def is_command(self, command: str):
        return command.startswith(self.command + " ")
    def strip_command(self, string: str):
        return string[len(self.command) + 1:]

class LibraryPlayer(Player):
    name = "Library Player"
    description = "Plays from the downloaded songs"
    command = "library"

    def __init__(self, library):
        self.library = library

    def search(self, query: str):
        return [
            SongChoice(s.title, s.artist, lambda _: s.path)
            for s in self.library.search(query)
        ]

class DeezPlayer(Player):
    name = "Deezer Player"
    description = "Plays from deezer"
    command = "deez"

    def __init__(self, arl):
        self.dz = Deezer()
        self.dz.login_via_arl(arl)

    def search(self, query: str):
        results = self.dz.api.search(query)['data']

        def download(link: str, callback: Callable[[], None]):
            class Listener:
                name = ""
                def send(self, kind, message):
                    if kind == 'updateQueue' and 'downloaded' in message and message['downloaded']:
                        callback(message['downloadPath'])
            listener = Listener()
            downloader = deemix.generateDownloadObject(self.dz, link, TrackFormats.MP3_320)
            Downloader(self.dz, downloader, {
                **deemix.settings.DEFAULTS,
                'downloadLocation': './music',
            }, listener = listener).start()

        return [
            SongChoice(x['title'], x['artist']['name'], lambda callback: download(x['link'], callback))
            for x in results[0:9]
        ]


class YoutubePlayer(Player):
    name = "Youtube Player"
    description = "Plays from youtube"
    command = "yt"

    def __init__(self):
        self.ytdl = YoutubeDL()

    def search(self, query: str):
        results = YoutubeSearch(query).videos

        def download(link: str):
            pass

        return [
            SongChoice(x['title'], x['channel'], lambda: download(x['id']))
            for x in results[0:9]
        ]

