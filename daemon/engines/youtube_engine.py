from engine import Engine, SongChoice
import tagger

from dataclasses import dataclass
import tempfile
import re

from yt_dlp import YoutubeDL
#from youtube_search import YoutubeSearch
from ytmusicapi import YTMusic
import requests

#hyphens = '\u002D\u058A\u05BE\u1400\u1806\u2010\u2011\u2012\u2013\u2014\u2015\u2E3A\u2E3B\uFE58\uFE63\uFF0D'
#splitter = re.compile(f'\s+[{hyphens}]\s+')

class YoutubeEngine(Engine):
    name = "Youtube"
    description = "Plays from youtube"

    def __init__(self, library, options):
        self.ytapi = YTMusic()
        self.library = library

    @dataclass
    class YoutubeSongChoice(SongChoice):
        art : str
        video : str
        dir : str

        def filename(self, extension = "mp3"):
            return self.dir + f'{self.artist} - {self.title}.{extension}'

        def choose(self):
            ytdl = YoutubeDL({
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '320',
                }],
                'progress_hooks': [ lambda h: self.hook(h) ],
                'paths': { 'temp': tempfile.gettempdir(), },
                'outtmpl': { 'default': self.filename("%(ext)s") },
            })
            rv = ytdl.download([ self.video ])
            print(f'Getting thumbnail')
            r = requests.get(self.art)
            print(f'Tagging {self.filename()}')
            f = tagger.TaggedFile(self.filename())
            f.set_title(self.title)
            f.set_artist(self.artist)
            f.set_art(r.headers['Content-Type'], r.content), 
            f.save()
            return self.filename()

        def hook(self, h):
            if h['status'] == 'finished':
                self.path = h['filename']

    def search(self, query : str):
        results = self.ytapi.search(query, limit = 100)
        results = [
            r for r in results
            if r['resultType'] in ['song', 'video']
        ]

        #print([ (r['resultType'], 'videoId' in r) for r in results ])

        return [
            self.YoutubeSongChoice(
                title = r['title'],
                artist = r['artists'][0]['name'],
                art = sorted(r['thumbnails'], key = lambda t: t['width'])[0]['url'],
                video = r['videoId'],
                dir = self.library.path(),
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

