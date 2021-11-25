#!/usr/bin/env python

from typing import List

import grpc
import typer

from sonica_pb2_grpc import SonicaStub
from sonica_pb2 import Empty, Search, Status

def ansi(code, text):
    return f'\x00\x1B[{code}m{text}\x00\x1B[m'

def songformat(song):
    return f'{ansi(1, song.title)} - {ansi(3, song.artist)}'

cli = typer.Typer()

@cli.command()
def play():
    r = daemon.Play(Empty())
    if not r.success:
        print(ansi(31, r.reason))

@cli.command()
def stop():
    r = daemon.Stop(Empty())
    if not r.success:
        print(ansi(31, r.reason))

@cli.command()
def skip():
    r = daemon.Skip(Empty())
    if not r.success:
        print(ansi(31, r.reason))

@cli.command()
def search(query : List[str], engines : str = ''):
    q = [' '.join(query)] # The daemon asks for a list of queries
    e = engines.split(',') if engines != '' else []
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
                map[counter] = (id, song)

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

            chosen_id, chosen_song = map[selection]
            r = daemon.Choose(Search.Choice(possibility_id = chosen_id, add_to_top = next))
            if r.success:
            	print(f'Queued: {songformat(chosen_song)}')
            	exit(0)
            else:
                print(ansi(31, f'Addition failed: »{r.reason}«'))
                exit(1)
        except Exception as e:
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

@cli.callback()
def callback(host: str = 'localhost', port: int = 7700):
    global daemon
    connection = f'{host}:{port}'
    channel = grpc.insecure_channel(connection)
    daemon = SonicaStub(channel)

cli()
