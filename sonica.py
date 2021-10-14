#!/usr/bin/env python

import typer
import discord
from discord.ext import commands

from library import Library
from playlist import Playlist
from players import LibraryPlayer, DeezPlayer  # , YoutubePlayer

bot = commands.Bot(command_prefix = '')

library = None
playlist = None
players = []

class EnumeratedOption:
    options = {}

    def __init__(self, options):
        self.options = options

    def is_an_option(self, string: str):
        return string in self.options.keys()


# This acts as the catchall as well (the last command checked)
enumerators = {}
@bot.command(brief = 'if you enter something i have asked (like 1 or 2)')
async def try_enumerators(ctx):
    global enumerators
    if not ctx.message.channel.id in enumerators:
        return

    channel_enum = enumerators[ctx.message.channel.id]
    selection = ctx.message.content.split(" ")
    if all(channel_enum.is_an_option(x) for x in selection):
        async with ctx.message.channel.typing():
            # Always at least 1 selection
            complete_message = await channel_enum.options[selection[0]](ctx.message.channel)
            # Then get the rest. If there are no more, nothing happens
            for select in selection[1:]:
                complete_message += "\n"
                complete_message += await channel_enum.options[select](ctx.message.channel)
            await ctx.message.channel.send(complete_message)
        del enumerators[message.channel.id]

async def try_command(func, else_message, runIfPlaying=True):
    global playlist
    if runIfPlaying == playlist.is_playing():
        func()
    else:
        await message.channel.send(else_message)

@bot.command(brief = 'makes me start playing music')
async def play(ctx):
    return await try_command(playlist.play, "I'm already playing!!", runIfPlaying=False)

@bot.command(brief = 'ill change song if someone asked me to play trash')
async def skip(ctx):
    return await try_command(playlist.skip, "I can't skip if i am not playing TwT")

@bot.command(brief = 'makes me stop my tunes')
async def stop(ctx):
    return await try_command(playlist.stop, "I'm not playing anything you dummy >\:(")

@bot.command(aliases = ['playlist', 'current', 'playing', 'now'], brief = 'i can tell you what i\'m playing')
async def queue(ctx):
    return_message = ''
    if playlist.current is None:
        return_message = "I'm not playing anything. Start me up! UwU"
    else:
        return_message = "I'm playing " + str(playlist.current)
        if len(playlist.queue) == 0:
            return_message += ", but I've nothing requested queued up"
        else:
            return_message += ", and next I'll play:\n"
            return_message += "\n".join([str(song) for song in playlist.queue])
        return_message += "\n\n"  # Add a full newline between potential queue and the autoplay
        return_message += "Coming up next from autoplay:\n"
        return_message += playlist.get_unplayed(5)
    return await ctx.message.channel.send(return_message)

@bot.command(brief = 'i can mix up the playlist')
async def shuffle(ctx):
    playlist.shuffle()
    return await ctx.message.channel.send("Queue shuffled!")

@bot.command(brief = 'if you need me to mix up my LP collection')
async def shuffleall(ctx):
    playlist.shuffleall()
    return await ctx.message.channel.send("Queue and backlog shuffled!")

async def handle_music_message(message):
    global players, enumerators, playlist, library
    for player in players:
        if player.is_command(message.content):
            query = player.strip_command(message.content)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.command(brief = 'shows my personal history')
def changelog(ctx):
    ctx.message.channel.send("\n".join([
        "Heres my personal history :D",
        "v0.1  *Basic deez downloading and playing",
    ])

def player_command(player):
    # Set up the command we'll call
    async def result(ctx, *, query):
        results = player.search(query)

        if len(results) == 0:
            return await ctx.message.channel.send(
                f'Couldn\'t find anything named »{query}« there :thinking:'
            )

        def callback(songchoice):
            async def func(channel):
                songchoice.choose(playlist.enqueue_file)
                return f"I've queued {songchoice}"
            return func

        options = {
            str(index + 1): callback(songchoice)
            for index, songchoice in enumerate(results)
        }

        enumerators[ctx.message.channel.id] = EnumeratedOption(options)

        text = "I found a bunch of songs:\n" + "\n".join([
            f"{index + 1}: {songchoice}"
            for index, songchoice in enumerate(results)
        ])

        return await ctx.message.channel.send(text)

    # Then return that command
    return result


def main(api: str, deez_arl: str = None, folder: str = "music"):
    global library, playlist, players
    library = Library(folder)
    print(f"Library contains {library.size()} songs")
    playlist = Playlist(library)
    # playlist.play()
    players = [
        LibraryPlayer(library),
        #YoutubePlayer(),
    ] + ([ DeezPlayer(deez_arl) ] if deez_arl != None else [])
    for p in players:
        c = commands.Command(func = player_command(p), name = p.command, brief = p.description)
        bot.add_command(c)
    bot.run(api)


typer.run(main)
