#!/usr/bin/env python

from concurrent.futures import ThreadPoolExecutor
from random import randint

import grpc
import typer

from sonica_pb2 import Status, Result, Song, Search, LibraryInfo, EngineList
from sonica_pb2_grpc import SonicaServicer, add_SonicaServicer_to_server

import song
from library import Library
from playlist import Playlist
from players import LibraryPlayer, DeezPlayer

def randint64():
    return randint(-9223372036854775808, 9223372036854775807)

def songify(song):
    if song is None:
        return None
    else:
        return Song(
            title = song.title,
            artist = song.artist,
            album = song.album,
        )

class Sonica(SonicaServicer):
    def __init__(self, library, players):
        self.library = library
        self.playlist = Playlist(library)
        self.players = players
        self.choices = {}

    # Playback commands
    
    def Play(self, request, context):
        try:
            self.playlist.play()
            return Result(success = True, reason = '')
        except Exception as e:
            return Result(success = False, reason = str(e))

    def Stop(self, request, context):
        try:
            self.playlist.stop()
            return Result(success = True, reason = '')
        except Exception as e:
            return Result(success = False, reason = str(e))

    def Skip(self, request, context):
        try:
            self.playlist.skip()
            return Result(success = True, reason = '')
        except Exception as e:
            return Result(success = False, reason = str(e))

    # Queue commands

    def Clear(self, request, context):
        if request.value != self.playlist.queue_hash():
            return Result(success = False, reason = 'Hash mismatch')

        self.playlist.clear()
        return Result(success = True, reason = '')

    def Shuffle(self, request, context):
        if request.hash.value != self.playlist.queue_hash():
            return Result(success = False, reason = 'Hash mismatch')

        if request.queue:
            self.playlist.shuffle_queue()
        if request.autoplay:
            self.playlist.shuffle_autoplay()
        if not request.queue and not request.autoplay:
            return Result(success = False, reason = "Shuffling flags were both false")
        return Result(success = True, reason = '')

    def Move(self, request, context):
        if request.hash.value != self.playlist.queue_hash():
            return Result(success = False, reason = 'Hash mismatch')

        if request.from_index >= len(self.playlist.queue):
            return Result(success = False, reason = 'From-value is not a valid index')

        if request.to_index >= len(self.playlist.queue):
            return Result(success = False, reason = 'To-value is not a valid index')

        self.playlist.move(request.from_index, request.to_index)
        return Result(success = True, reason = '')

    def Remove(self, request, context):
        if request.hash.value != self.playlist.queue_hash():
            return Result(success = False, reason = 'Hash mismatch')

        if request.target >= len(self.playlist.queue):
            return Result(success = False, reason = 'No song with that id')

        self.playlist.remove(request.target)
        return Result(success = True, reason = '')

    # Adding commands

    def Search(self, request, context):
        # This should change when players actually differentiate strings for repeated search
        querystring = ' '.join(request.query)

        results = []
        for p in self.players:
            search = p.search(querystring)
            map = {}

            for r in search:
                id = randint64()
                self.choices[id] = r
                map[id] = Song( title = r.title, artist = r.artist, album = '')

            engine_result = Search.Result.EngineResult(
                name = p.name,
                possibilities = map,
            )
            results.append(engine_result)

        return Search.Result(results = results)

    def Choose(self, request, context):
        id = request.possibility_id
        if not id in self.choices:
            return Result(success = False, reason = 'Not a valid possibilityid')

        filename = self.choices[id].choose()
        self.playlist.enqueue_file(filename, request.add_to_top)
        return Result(success = True, reason = '')


    # Info commands

    def Engines(self, request, context):
        return EngineList(engines = [ e.name for e in self.players ])

    def Status(self, request, context):
        queue = [ songify(s) for s in self.playlist.queue ]
        if request.queue_max != -1 and len(queue) != 0:
            queue = list(queue[0:request.queue_max])

        autoplay = [ songify(s) for s in self.playlist.get_unplayed() ]
        if request.autoplay_max != -1 and len(autoplay) != 0:
            autoplay = list(autoplay[0:request.autoplay_max])

        return Status.Info(
            current = songify(self.playlist.current),
            length = 1, # TODO: This should actually do something
            progress = 0,

            # Note these work on the full list
            queue_length = len(self.playlist.queue),
            queue_hash = self.playlist.queue_hash(),

            queue = queue,
            autoplay = autoplay,
        )

    def Library(self, request, context):
        return LibraryInfo(
            size = self.library.size(),
            songs = [ songify(s) for s in self.library.index ],
        )



def start_server(sonica):
    server = grpc.server(ThreadPoolExecutor(max_workers = 4))
    add_SonicaServicer_to_server(sonica, server)

    location = 'localhost:7700'
    server.add_insecure_port(location)
    server.start()
    print(f'Server started on {location}')
    server.wait_for_termination()

def main(deez_arl : str = None, dir : str = 'music'):
    library = Library(dir)
    print(f"Library contains {library.size()} songs")

    players = []
    players.append( LibraryPlayer(library) )
    #players.append( YoutubePlayer() )
    if deez_arl:
        players.append( DeezPlayer(deez_arl) )

    start_server(Sonica(library, players))

typer.run(main)
