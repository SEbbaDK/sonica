from dataclasses import dataclass
from engine import Engine, SongChoice

import re
from youtube_dl import YoutubeDL
#from youtube_search import YoutubeSearch
from ytmusicapi import YTMusic

#hyphens = '\u002D\u058A\u05BE\u1400\u1806\u2010\u2011\u2012\u2013\u2014\u2015\u2E3A\u2E3B\uFE58\uFE63\uFF0D'
#splitter = re.compile(f'\s+[{hyphens}]\s+')

class YoutubeEngine(Engine):
    name = "Youtube"
    description = "Plays from youtube"


    def __init__(self, library, options):
        self.ytdl = YoutubeDL()
        self.ytapi = YTMusic()

    def search(self, query : str):
        results = self.ytapi.search(query, limit = 100)
        results = [
            r for r in results
            if r['resultType'] in ['song', 'album', 'video']
        ]
        print(results)
        return [
			SongChoice(
				title = r['resultType'] + " : " + r['title'],
				artist = r['artists'][0]['name'],
			)
			for r in results
        ]

#    def search(self, query: str):
#        results = YoutubeSearch(query).videos
#        splitresults = [
#           self.splitter.split(v['title'], 1)
#           for v in results
#           if ' - ' in v['title']
#       ]
#
#        return [
#           SongChoice(
#               title = t,
#               artist = a,
#           )
#           for a, t in splitresults[0:10]
#        ] + [
#            SongChoice(
#               title = x['title'],
#               artist = x['channel'],
#           )
#            for x in results[0:10]
#        ]

