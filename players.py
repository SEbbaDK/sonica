from dataclasses import dataclass
from collections.abc import Callable

import deemix
import deemix.settings
from deemix.downloader import Downloader
from deezer import Deezer, TrackFormats
#from youtube_dl import YoutubeDL
#from youtube_search import YoutubeSearch

from song import Song
from library import Library
from playlist import Playlist

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

    @dataclass
    class LibrarySongChoice(SongChoice):
        song: Song

        def choose(self, callback):
            callback(self.song.path)

    def search(self, query: str):
        return [
            self.LibrarySongChoice(
                title = s.title,
                artist = s.artist,
                song = s,
            )
            for s in self.library.search(query)
        ]

class DeezPlayer(Player):
    name = "Deezer Player"
    description = "Plays from deezer"
    command = "deez"

    def __init__(self, arl):
        self.dz = Deezer()
        self.dz.login_via_arl(arl)

    @dataclass
    class DeezSongChoice(SongChoice):
        dz: Deezer
        link: str

        def choose(self, callback):
            self.callback = callback
            downloader = deemix.generateDownloadObject(
                self.dz,
                self.link,
                TrackFormats.MP3_320
            )
            self.dl = Downloader(self.dz, downloader, {
                **deemix.settings.DEFAULTS,
                'downloadLocation': './music',
            }, listener = self).start()

        def send(self, kind, message):
            if kind != 'updateQueue':
                return
            if 'downloaded' in message and message['downloaded']:
                self.callback(message['downloadPath'])


    def search(self, query: str):
        results = self.dz.api.search(query)['data']
        #print(results[0:9])
        return [
            self.DeezSongChoice(
                title = x['title'],
                artist = x['artist']['name'],
                dz = self.dz,
                link = x['link']
            )
            for x in results[0:9]
        ]


#class YoutubePlayer(Player):
#    name = "Youtube Player"
#    description = "Plays from youtube"
#    command = "yt"
#
#    def __init__(self):
#        self.ytdl = YoutubeDL()
#
#    def search(self, query: str):
#        results = YoutubeSearch(query).videos
#
#        def download(link: str):
#            pass
#
#        return [
#            SongChoice(x['title'], x['channel'], lambda: download(x['id']))
#            for x in results[0:9]
#        ]

