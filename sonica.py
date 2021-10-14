#!/usr/bin/env python

import typer
from discord.ext import commands

from library import Library
from playlist import Playlist
from players import LibraryPlayer, DeezPlayer  # , YoutubePlayer

bot = commands.Bot(command_prefix = '')

library = None
playlist = None
client = discord.Client()
players = []

class EnumeratedOption:
    options = {}

    def __init__(self, options):
        self.options = options

    def is_an_option(self, string: str):
        return string in self.options.keys()


# This acts as the catchall as well (the last command checked)
enumerators = {}
@bot.command()
async def try_enumerators(ctx):
    global enumerators
    if not ctx.message.channel.id in enumerators:
		return

    channel_enum = enumerators[ctx.message.channel.id]
    selection = message.content.split(" ")
    if all(channel_enum.is_an_option(x) for x in selection):
        async with message.channel.typing():
            # Always at least 1 selection
            complete_message = await channel_enum.options[selection[0]](message.channel)
            # Then get the rest. If there are no more, nothing happens
            for select in selection[1:]:
                complete_message += "\n"
                complete_message += await channel_enum.options[select](message.channel)
            await message.channel.send(complete_message)
        del enumerators[message.channel.id]

async def try_command(func, else_message, runIfPlaying=True):
    global playlist
    if runIfPlaying == playlist.is_playing():
        func()
    else:
        await message.channel.send(else_message)

@bot.command(name = 'play')
async def play():
    return await try_command(playlist.play, "I'm already playing!!", runIfPlaying=False)

@bot.command(name = 'skip')
async def skip():
    return await try_command(playlist.skip, "I can't skip if i am not playing TwT")

@bot.command(name = 'stop')
async def stop():
    return await try_command(playlist.stop, "I'm not playing anything you dummy >\:(")

@bot.command(name = 'queue', aliases = ['playlist', 'queue', 'current', 'playing', 'now'])
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
    return await message.channel.send(return_message)

@bot.command(name = 'shuffle'):
def shuffle(ctx):
    playlist.shuffle()
    return await message.channel.send("Queue shuffled!")

@bot.command(name = 'shuffleall'):
def shuffleall(ctx):
    playlist.shuffleall()
    return await message.channel.send("Queue and backlog shuffled!")

async def handle_music_message(message):
    global players, enumerators, playlist, library
    for player in players:
        if player.is_command(message.content):
            query = player.strip_command(message.content)
            results = player.search(query)

            if len(results) == 0:
                return await message.channel.send(
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

            enumerators[message.channel.id] = EnumeratedOption(options)

            text = "I found a bunch of songs:\n" + "\n".join([
                f"{index + 1}: {songchoice}"
                for index, songchoice in enumerate(results)
            ])

            return await message.channel.send(text)

@bot.event
async def on_ready():
    print(f"Logged in as {client.user}")


def help_message():
    global players
    return "\n".join([
        "Okiii :3",
        "**BASIC:**",
        "  **help**      This command",
        "  **play**      Start playing current song",
        "  **stop**      Stop playing current song",
        "  **skip**      Skip current song",
        "  **queue**     Displays current queue of songs",
        "  **playlist**  Ditto",
        "  **shuffle**   Shuffles the current queue",
        "  **shuffleall** Shuffles the current queue AND backlog",
        "  **<option>**  Select one of the options",
        "  **changelog** Show the changelog",
        "**PLAYERS:**",
    ] + [
        f"  **{player.command}** <search query>\t{player.description}"
        for player in players
    ])


def changelog_message():
    return "\n".join([
        "Heres my personal history :D",
        "v0.1  *Basic deez downloading and playing",
    ])

def main(api: str, deez_arl: str = None, folder: str = "music"):
    global library, playlist, players
    library = Library(folder)
    print(f"Library contains {library.size()} songs")
    playlist = Playlist(library)
    # playlist.play()
    players = [
        LibraryPlayer(library),
        #YoutubePlayer(),
    ] + ([DeezPlayer(deez_arl)] if deez_arl != None else [])
    client.run(api)


typer.run(main)
