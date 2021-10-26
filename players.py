from dataclasses import dataclass
from collections.abc import Callable

import re
import deemix
import deemix.settings
from deemix.downloader import Downloader
from deezer import Deezer, TrackFormats
from deezer.errors import DataException
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

class LibraryPlayer(Player):
    name = "Library Player"
    description = "Plays from the downloaded songs"
    command = "lib"

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
        url_check = query
        if re.search("([a-z]*[.])\w+", url_check):
            return []
        results = self.dz.api.search(query)['data']
        #print(results[0:9])
        res_list = [
            self.DeezSongChoice(
                title = x['title'],
                artist = x['artist']['name'],
                dz = self.dz,
                link = x['link']
            )
            for x in results[0:9]
        ]
        # If there are no search results, try an id-search if the query can
        # be an int.
        if not res_list and int(query):
            res_list = self.search_id(int(query))

        return res_list

    def search_id(self, id_query: int):
        # Just because the query is int()-able, doesn't mean it's actually
        # a deezer track id. In case it's not, we don't return any results.
        try:
            result = self.dz.api.get_track(id_query)
        except DataException:
            return []

        return [self.DeezSongChoice(
            title = result['title'],
            artist = result['artist']['name'],
            dz = self.dz,
            link = result['link']
        )]

class YoutubePlayer(Player):
    name = "Youtube Player"
    description = "Plays from youtube"
    command = "yt"

    def __init__(self):
        self.ytdl = YoutubeDL()

    @dataclass
    class YTSongChoice(SongChoice):
        ytdl: YoutubeDL()
        link: str

        def choose(self, callback):
            self.callback = callback

    def search(self, query: str):
        results = YoutubeSearch(query).videos

        def download(link: str):
            pass

        return [
            SongChoice(x['title'], x['channel'], lambda: download(x['id']))
            for x in results[0:9]
        ]
