#!/usr/bin/env python

import grpc
import typer

from sonica_pb2_grpc import SonicaStub
from sonica_pb2 import Empty, Search, Status

def ansi(code, text):
    return f'\x00\x1B[{code}m{text}\x00\x1B[m'

def songformat(song):
    return f'{ansi(1, song.title)} by {song.artist}'

cli = typer.Typer()
channel = grpc.insecure_channel('localhost:7700')
daemon = SonicaStub(channel)

@cli.command()
def play():
    daemon.Play(Empty())

@cli.command()
def stop():
    daemon.Stop(Empty())

@cli.command()
def skip():
    daemon.Skip(Empty())

@cli.command()
def search(query : str, engines : str = ''):
    q = [query] # The daemon asks for a list of queries
    e = engines.split(',') if engines != '' else ["deez"]
    r = daemon.Search(Search.Query( query = q, engines = e))

    counter = 0
    map = {}
    for e in r.results:
        print(ansi(1, e.name))
        if len(e.possibilities) == 0:
            print('Nothing')
        else:
            for id, song in e.possibilities.items():
                counter += 1
                print(f'{counter}: {songformat(song)}')
                map[counter] = id

    while True:
        next = False
        c = input('Select song: ')

        if c == '':
            print("No input entered")
            continue

        if c[-1] == '!':
            next = True
            c = c[:-1]

        try:
            selection = int(c)
            if not selection in map:
                print('Not a valid choice')
                continue

            choice = map[selection]
            r = daemon.Choose(Search.Choice(possibility_id = choice, add_to_top = next))
            print(r)
            return # We are done, quit
        except e:
            print(e)

@cli.command()
def engines():
    r = daemon.Engines(Empty())
    print(' '.join(r.engines))

@cli.command()
def status(queue_max : int = -1, autoplay_max : int = 10):
    r = daemon.Status(Status.Query( queue_max = queue_max, autoplay_max = autoplay_max ))
    if r.current.title == '' and r.current.artist == '':
        print('Not playing anything')
    else:
        print(f'Currently playing {songformat(r.current)}')

    counter = 0
    print('\n' + ansi(1, 'Queue'))
    for s in r.queue:
        counter += 1
        print(f'{str(counter).rjust(3)}: {songformat(s)}')

    print('\n' + ansi(1, 'Autoplay'))
    for s in r.autoplay:
        counter += 1
        print(f'{str(counter).rjust(3)}: {songformat(s)}')

cli()