#!/usr/bin/env python

import grpc
import typer
import discord
from discord.ext import commands

from sonica_pb2_grpc import SonicaStub
from sonica_pb2 import Empty, Search, Status

MAX_MSG_LENGTH = 2000

bot = commands.Bot(command_prefix='')

def surround(surround, string):
    return f'{surround}{string}{surround}'

def songformat(song):
    return surround('**', song.title) + ' - ' + surround('*', song.artist)

@bot.command()
async def play(ctx):
    r = daemon.Play(Empty())
    if not r.success:
        await ctx.message.channel.send(r.reason)
    else:
        await ctx.message.channel.send("Okie, i'll play")

@bot.command()
async def stop(ctx):
    r = daemon.Stop(Empty())
    if not r.success:
        await ctx.message.channel.send(r.reason)
    else:
        await ctx.message.channel.send("Okie, i'll stop then :(")

@bot.command()
async def skip(ctx):
    r = daemon.Skip(Empty())
    if not r.success:
        await ctx.message.channel.send(r.reason)
    else:
        await ctx.message.channel.send("I'm just playing what you ask me to, but okay :/")

enumerators = {}

@bot.command()
async def search(ctx, *queries):
    global enumerators
    query = ' '.join(queries)
    q = [query]
    r = daemon.Search(Search.Query( query = q ))

    # Note this is the same code as in the cli, so any bugs here will be shared there
    mes = 'Here you go ^-^\n'
    overflow_trail = "\n... And more I couldn't fit in 1 message! Try narrowing your search to a specific engine ;3"
    len_overflow = len(overflow_trail)
    counter = 0
    map = {}
    try:
        for e in r.results:
            mes = add_if_fits(mes, surround('**', e.name) + '\n', len_overflow, MAX_MSG_LENGTH)

            if len(e.possibilities) == 0:
                mes = add_if_fits(mes, 'Nothing\n', len_overflow, MAX_MSG_LENGTH)

            else:
                for id, song in e.possibilities.items():
                    counter += 1
                    mes = add_if_fits(mes, f'{counter}: {songformat(song)}\n', len_overflow, MAX_MSG_LENGTH)
                    map[counter] = (id, song)
            mes = add_if_fits(mes, '\n', len_overflow, MAX_MSG_LENGTH)
    except MessageOverflow:
        mes += overflow_trail

    enumerators[ctx.message.channel] = map
    await ctx.message.channel.send(mes)

@bot.command()
async def choose(ctx, *choices):
    global enumerators

    if not ctx.message.channel in enumerators:
        return await ctx.message.channel.send('I am not asking you to pick anything')

    treated_choices = []
    for c in choices:
        if c[-1] == '!':
            treated_choices.append( (int(c[:-1]), True) )
        else:
            treated_choices.append( (int(c), False) )

    for index, play_next in treated_choices:
        if not index in enumerators[ctx.message.channel]:
            return await ctx.message.channel.send('You asked me to queue something i don\'t understand »{id}«')

        id, song = enumerators[ctx.message.channel][index]
        daemon.Choose(Search.Choice( possibility_id = id, add_to_top = play_next ))
        await ctx.message.channel.send(f'Queued {songformat(song)}')

@bot.command()
async def status(ctx):
    r = daemon.Status(Status.Query( queue_max = -1, autoplay_max = 5 ))
    mes = ""
    if r.current.title == '' and r.current.artist == '':
        mes += "I'm not playing anything"
    else:
        mes += f"I'm playing {songformat(r.current)}"

    counter = 0
    mes += '\n' + surround('**', 'Queue') + '\n'
    for s in r.queue:
        counter += 1
        mes += f'{str(counter).rjust(3)}: {songformat(s)}\n'

    mes += '\n' + surround('**', 'Autoplay') + '\n'
    for s in r.autoplay:
        counter += 1
        mes += f'{str(counter).rjust(3)}: {songformat(s)}\n'

    await ctx.message.channel.send(mes)


@bot.event
async def on_ready():
    print(f"Logged on as {bot.user}!")


def add_if_fits(original: str, add: str, len_overflow: int, max_len: int):
    added = original + add
    if len(added) >= max_len - len_overflow:
        raise MessageOverflow
    else:
        return added


class MessageOverflow(Exception):
    pass


def main(token : str):
    global daemon
    channel = grpc.insecure_channel('localhost:7700')
    daemon = SonicaStub(channel)
    bot.run(token)

typer.run(main)
