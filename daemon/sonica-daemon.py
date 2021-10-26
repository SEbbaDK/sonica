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

    # Playback commands
    
    def Play(self, request, context):
        playlist.play()
        return Status(success = True)

    def Stop(self, request, context):
        playlist.stop()
        return Status(success = True)

    def Skip(self, request, context):
        playlist.skip()
        return Status(success = True)

    # Queue commands

    def Clear(self, request, context):
        if request.value != playlist.queue_hash():
            return Status(success = False, reason = 'Hash mismatch')

        playlist.clear()
        return Status(success = True)

    def Shuffle(self, request, context):
        if request.hash.value != playlist.queue_hash():
            return Status(success = False, reason = 'Hash mismatch')

        playlist.shuffle()
        return Status(success = True)

    def Move(self, request, context):
        if request.hash.value != playlist.queue_hash():
            return Status(success = False, reason = 'Hash mismatch')

        if request.from_index >= len(playlist.queue):
            return Status(success = False, reason = 'From-value is not a valid index')

        if request.to_index >= len(playlist.queue):
            return Status(success = False, reason = 'From-value is not a valid index')

        playlist.move(request.from_index, request.to_index)
        return Status(success = True)

    def Remove(self, request, context):
        if request.hash.value != playlist.queue_hash():
            return Status(success = False, reason = 'Hash mismatch')

        if request.target >= len(playlist.queue):
            return Status(success = False, reason = 'No song with that id')

        playlist.remove(request.target)
        return Status(success = True)

    # Adding commands

    #def Search(self, request, context):
    #    results = []
    #    for p in self.players:
    #        results.append(EngineResult(p.name, p.search(request.query)


    # Info commands

    def Engines(self, request, context):
        return EngineList(engines = [ e.name for e in players ])

    def Status(self, request, context):
        return Status.Info(
            current = songify(playlist.current),
            length = 1, # TODO: This should actually do something
            progress = 0,

            queue_length = len(playlist.queue),
            queue_hash = playlist.queue_hash(),
            queue = playlist.queue[0:request.queue_max],
            autoplay = playlist.autoplay[0:request.autoplay_max],
        )

    def Library(self, request, context):
        return LibraryInfo(
            size = library.size(),
            songs = [ songify(s) for s in library.index ],
        )



def start_server(sonica):
    server = grpc.server(ThreadPoolExecutor(max_workers = 4))
    add_SonicaServicer_to_server(sonica, server)

    location = 'localhost:50051'
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
