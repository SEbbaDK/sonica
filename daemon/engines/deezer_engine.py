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
                TrackFormats.MP3_320
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
        #print(results[0:9])
        res_list = [
            self.DeezerSongChoice(
                title = x['title'],
                artist = x['artist']['name'],
                dz = self.dz,
                link = x['link'],
                dir = self.library.path()
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

        return [self.DeezerSongChoice(
            title = result['title'],
            artist = result['artist']['name'],
            dz = self.dz,
            link = result['link']
        )]

