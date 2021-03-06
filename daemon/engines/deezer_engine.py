from dataclasses import dataclass
from engine import Engine, SongChoice

import re
import deemix
import deemix.settings
from deemix.downloader import Downloader
from deezer import Deezer, TrackFormats
from deezer.errors import DataException

class DeezerEngine(Engine):
    name = "Deezer"
    description = "Plays from deezer"
    # Deezer has high-quality audio and great tagging
    rank = 2

    def __init__(self, library, options):
        if not 'arl' in options:
            raise Exception('No arl given to deezer engine, but required to function')
        self.dz = Deezer()
        self.dz.login_via_arl(options['arl'])
        self.library = library

    @dataclass
    class DeezerSongChoice(SongChoice):
        dz: Deezer
        link: str
        dir: str

        def choose(self):
            downloader = deemix.generateDownloadObject(
                self.dz,
                self.link,
                TrackFormats.MP3_128
            )
            self.dl = Downloader(self.dz, downloader, {
                **deemix.settings.DEFAULTS,
                'downloadLocation': self.dir,
            }, listener = self).start()
            return self.path

        def send(self, kind, message):
            if kind != 'updateQueue':
                return
            if 'downloaded' in message and message['downloaded']:
                self.path = message['downloadPath']

    def search(self, query: str):
        url_check = query
        if re.search("([a-z]*[.])\w+", url_check):
            return []
        results = self.dz.api.search(query)['data']
        res_list = [
            self.DeezerSongChoice(
                title = x['title'],
                artist = x['artist']['name'],
                dz = self.dz,
                link = x['link'],
                dir = self.library.path()
            )
            for x in results[0:20]
        ]
        # If there are no search results, try an id-search if the query can
        # be an int.
        if len(res_list) == 0:
            res_list = self.search_id(query)

        return res_list

    def search_id(self, id_query : str):
        # Just because the query is int()-able, doesn't mean it's actually
        # a deezer track id. In case it's not, we don't return any results.
        try:
            id = int(id_query)
            result = self.dz.api.get_track(id)
        except:
            return []

        return [self.DeezerSongChoice(
            title = result['title'],
            artist = result['artist']['name'],
            dz = self.dz,
            link = result['link']
        )]

