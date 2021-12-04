from engine import Engine, SongChoice
import tagger

from dataclasses import dataclass
import tempfile
import re

from yt_dlp import YoutubeDL
from ytmusicapi import YTMusic
import requests

def ydownload(url : str,
              dir : str,
              title : str,
              artist : str,
              thumbnail : str):
    filename = f'{title} - {artist}'
    downloaded = dir + filename + ".mp3"

    ytdl = YoutubeDL({
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '320',
        }],
        'paths': { 'temp': tempfile.gettempdir(), },
        'outtmpl': { 'default': dir + filename + ".%(ext)s" },
    })
    rv = ytdl.download([ url ])

    print(f'Getting thumbnail')
    r = requests.get(thumbnail)

    print(f'Tagging {downloaded}')
    f = tagger.TaggedFile(downloaded)
    f.set_title(title)
    f.set_artist(artist)
    f.set_art(r.headers['Content-Type'], r.content), 
    f.save()
    return downloaded

class YoutubeMusicEngine(Engine):
    name = "YouTube-Music"
    description = "Plays from YouTube via YouTube Music"
    # YouTube Music has decent but limited tagging
    # and downloads can take quite a while
    rank = 3

    def __init__(self, library, options):
        self.library = library

    @dataclass
    class YoutubeMusicSongChoice(SongChoice):
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
        results = YTMusic().search(query, limit = 100)
        results = [
            r for r in results
            if r['resultType'] in ['song', 'video']
        ]

        return [
            self.YoutubeMusicSongChoice(
                title = r['title'],
                artist = r['artists'][0]['name'],
                thumbnail = sorted(
                    r['thumbnails'],
                    key = lambda t: t['width']
                )[0]['url'],
                video = r['videoId'],
                dir = self.library.path(),
            )
            for r in results[0:20]
        ]

