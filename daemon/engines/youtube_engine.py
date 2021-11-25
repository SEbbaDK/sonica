from dataclasses import dataclass
from engine import Engine, SongChoice

import re
from youtube_dl import YoutubeDL
from youtube_search import YoutubeSearch

class YoutubeEngine(Engine):
    name = "Youtube"
    description = "Plays from youtube"

    def __init__(self, library, options):
        self.ytdl = YoutubeDL()

    def search(self, query: str):
        results = YoutubeSearch(query).videos

        def download(link: str):
            pass

        return [
            SongChoice(x['title'], x['channel'], lambda: download(x['id']))
            for x in results[0:9]
        ]

