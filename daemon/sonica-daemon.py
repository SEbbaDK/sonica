#!/usr/bin/env python

from concurrent.futures import ThreadPoolExecutor

import grpc
import typer

from sonica_pb2 import Status, Result, EngineList, Song
from sonica_pb2_grpc import SonicaServicer, add_SonicaServicer_to_server

import song
from library import Library
from playlist import Playlist
from players import LibraryPlayer, DeezPlayer

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
        self.playlist.play()
        return Result(True)

    def Stop(self, request, context):
        self.playlist.stop()
        return Result(True)

    def Skip(self, request, context):
        self.playlist.skip()
        return Result(True)

    # Queue commands

    def Clear(self, request, context):
        if request.value != self.playlist.queue_hash():
            return Result(False, 'Hash mismatch')

        self.playlist.clear()
        return Result(True)

    def Shuffle(self, request, context):
        if request.hash.value != self.playlist.queue_hash():
            return Result(False, 'Hash mismatch')

		if request.queue
            self.playlist.shuffle_queue()
        if request.autoplay
        	self.playlist.shuffle_autoplay()
        if not request.queue and not request.autoplay
        	return Result(False, "Shuffling flags were both false")
        return Result(True)

    def Move(self, request, context):
        if request.hash.value != self.playlist.queue_hash():
            return Result(False, 'Hash mismatch')

        if request.from_index >= len(self.playlist.queue):
            return Result(False, 'From-value is not a valid index')

        if request.to_index >= len(self.playlist.queue):
            return Result(False, 'To-value is not a valid index')

        self.playlist.move(request.from_index, request.to_index)
        return Result(True)

    def Remove(self, request, context):
        if request.hash.value != self.playlist.queue_hash():
            return Result(False, 'Hash mismatch')

        if request.target >= len(self.playlist.queue):
            return Result(False, 'No song with that id')

        self.playlist.remove(request.target)
        return Result(True)

    # Adding commands

    def Search(self, request, context):
        results = []
        for p in self.players:
            search = p.search(request.query)
            map = {}

            for r in search:
                id = randint64()
                self.choices[id] = r
                map[id] = Song(r.title, r.artist, '')

            engine_result = EngineResult(p.name, map)
            results.append(engine_result)

        return Search.Result(results = results)

    def Choose(self, request, context):
        id = request.possibility_id
        if not id in self.choices:
            return Result(False, 'Not a valid possibilityid')

        filename = self.choices[id].choose()
        self.playlist.enqueue_file(filename)
        return Result(True)


    # Info commands

    def Engines(self, request, context):
        return EngineList(engines = [ e.name for e in players ])

    def Status(self, request, context):
        return Status.Info(
            current = songify(self.playlist.current),
            length = 1, # TODO: This should actually do something
            progress = 0,

            queue_length = len(self.playlist.queue),
            queue_hash = self.playlist.queue_hash(),
            queue = self.playlist.queue[:request.queue_max],
            autoplay = self.playlist.autoplay[:request.autoplay_max],
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
