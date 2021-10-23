#!/usr/bin/env python

from concurrent.futures import ThreadPoolExecutor

import grpc
import typer

from sonica_pb2 import Status, Result
from sonica_pb2_grpc import SonicaServicer, add_SonicaServicer_to_server

from library import Library
from playlist import Playlist
from players import LibraryPlayer, DeezPlayer

class Sonica(SonicaServicer):
    def __init__(self, library, players)
        self.library = library
        self.playlist = Playlist(library)
        self.players = players

    def Play(self, request, context):
        playlist.play()
        return Status(success = True, reason = '')

    def Pause(self, request, context):
        playlist.pause()
        return Status(success = True, reason = '')

    def Skip(self, request, context):
        playlist.skip()
        return Status(success = True, reason = '')

    def Shuffle(self, request, context):
        playlist.shuffle()
        return Status(success = True, reason = '')

    def Search(self, request, context):
        results = []
        for p in self.players:



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
