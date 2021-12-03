from engine import Engine, SongChoice
import tagger
from youtube_music_engine import ydownload

from dataclasses import dataclass
import tempfile
import re

from youtube_search import YoutubeSearch
import requests

class YoutubeEngine(Engine):
    name = "YouTube"
    description = "Plays from YouTube (Only use this for music not licensed via youtube music)"
    # YouTube has really flaky tagging
    # and downloads can take quite a while
    rank = 4

    def __init__(self, library, options):
        self.library = library

    @dataclass
    class YoutubeSongChoice(SongChoice):
        thumbnail : str
        video : str
        dir : str

        def choose(self):
            return ydownload(
                url = self.video,
                title = self.title,
                artist = self.artist,
                dir = self.dir,
                thumbnail = self.thumbnail,
            )

    def search(self, query : str):
        results = YoutubeSearch(query, max_results = 20)

        hyphens = '\u002D\u058A\u05BE\u1400\u1806\u2010\u2011\u2012\u2013\u2014\u2015\u2E3A\u2E3B\uFE58\uFE63\uFF0D'
        splitter = re.compile(f'\s+([{hyphens}|/:]|//)\s+')

        options = []
        for v in results.videos:
            s = splitter.split(v['title'], maxsplit = 1)
            if len(s) == 1:
                options.append((
                	v['title'],
                	v['channel'].replace('Vevo', '').replace(' - Topic', ''),
                	v
            	))
            elif len(s) == 2:
                options.append((s[0], s[1], v))
                options.append((s[1], s[0], v))

        return [
            self.YoutubeSongChoice(
                title = title,
                artist = artist,
                thumbnail = v['thumbnails'][-1],
                video = v['id'],
                dir = self.library.path(),
            )
            for title, artist, v in options[0:20]
        ]

