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
        await update_presence()

@bot.command()
async def stop(ctx):
    r = daemon.Stop(Empty())
    if not r.success:
        await ctx.message.channel.send(r.reason)
    else:
        await ctx.message.channel.send("Okie, i'll stop then :(")
        await update_presence(no_presence=True)

@bot.command()
async def skip(ctx):
    r = daemon.Skip(Empty())
    if not r.success:
        await ctx.message.channel.send(r.reason)
    else:
        await ctx.message.channel.send("I'm just playing what you ask me to, but okay :/")
        await update_presence()

enumerators = {}

@bot.command()
async def search(ctx, *queries):
    global enumerators
    query = ' '.join(queries)
    q = [query]
    r = daemon.Search(Search.Query( query = q ))

    # Note this is the same code as in the cli, so any bugs here will be shared there
    mes = 'Here you go ^-^\n'
    counter = 0
    map = {}
    for e in r.results:
        mes += surround('**', e.name) + '\n'

        if len(e.possibilities) == 0:
            mes += 'Nothing\n'
        else:
            for id, song in e.possibilities.items():
                counter += 1
                mes += f'{counter}: {songformat(song)}\n'
                map[counter] = (id, song)
        mes += '\n'

    enumerators[ctx.message.channel] = map
    await safe_send(ctx, mes, overflow="\n... And more I couldn't fit in 1 message! Try narrowing your search ;3")

@bot.command()
async def choose(ctx, *choices):
    global enumerators

    if ctx.message.channel not in enumerators:
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

    await safe_send(ctx, mes)


@bot.event
async def on_ready():
    print(f"Logged on as {bot.user}!")


async def update_presence(no_presence = False):
    if not no_presence:
        r = daemon.Status(Status.Query(queue_max=0, autoplay_max=0))
        song = r.current
        game = discord.Game(f'{song.title} by {song.artist}')
        await bot.change_presence(activity=game)
    else:
        await bot.change_presence(activity=None)


def trunc_to_max_with_message(original: str, overflow_msg: str, seperator: str, max_len: int):
    if len(original) > max_len:
        while (len(original) + len(overflow_msg)) > max_len:
            original = original.rsplit(seperator, 1)[0]
        return original + overflow_msg
    else:
        return original


async def safe_send(ctx, mes, overflow="\n... And more I couldn't fit in 1 message! ;O", sep='\n'):
    mes = trunc_to_max_with_message(mes, overflow, sep, MAX_MSG_LENGTH)
    await ctx.message.channel.send(mes)


def main(token : str):
    global daemon
    channel = grpc.insecure_channel('localhost:7700')
    daemon = SonicaStub(channel)
    bot.run(token)

typer.run(main)
