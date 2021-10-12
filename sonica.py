#!/usr/bin/env python

from _typeshed import OpenTextMode
import typer
import discord

from library import Library
from playlist import Playlist
from players import LibraryPlayer, DeezPlayer, SongChoice#, YoutubePlayer

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

enumerators = {}

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
                    await channel.send(f"I'll queue {songchoice}")
                    songchoice.choose(playlist.enqueue_file)
                return func

            options = {
                str(index + 1): callback(songchoice)
                for index, songchoice in enumerate(results)
            }

            enumerators[message.channel.id] = EnumeratedOption(options)

            if len(options) == 1:
                callback(1)
            else:
                text = "I found a bunch of songs:\n" + "\n".join([
                    f"{index + 1}: {songchoice}"
                    for index, songchoice in enumerate(results)
                ])

            return await message.channel.send(text)

    async def try_command(func, else_message, runIfPlaying = True):
        global playlist
        if runIfPlaying == playlist.is_playing():
            func()
        else:
            await message.channel.send(else_message)

    if message.content == "skip":
        return await try_command(playlist.skip, "I can't skip if i am not playing TwT")
    if message.content == "stop":
        return await try_command(playlist.stop, "I'm not playing anything you dummy >\:(")
    if message.content == "play":
        return await try_command(playlist.play, "I'm already playing!!", runIfPlaying = False)

    if message.content == "playlist" or message.content == "queue":
        if len(playlist.queue) == 0:
            if playlist.current == None:
                return await message.channel.send("No songs in queue yet :3")
            else:
                return await message.channel.send("I'm playing " + str(playlist.current) + " but I've nothing queued up")
        else:
            return await message.channel.send("\n".join([
                "Right now i'm playing " + str(playlist.current) + " and next I'll play:",
                "\n".join([ str(s) for s in playlist.queue ]),
            ]))

    channel_enum = enumerators[message.channel.id]
    if channel_enum.is_an_option(message.content):
        await channel_enum.options[message.content](message.channel)
        del enumerators[message.channel.id]
        return

@client.event
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

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    #print(str(message) + ": '" + message.content + "'")

    if message.content == "help":
        return await message.channel.send(help_message())
    if message.content == "changelog":
        return await message.channel.send(changelog_message())

    if "music" in message.channel.name or "musik" in message.channel.name:
        try:
            await handle_music_message(message)
        except Exception as e:
            await message.channel.send("I did an error :(\n```\n" + str(e) + "\n```")
            raise e


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
    client.run(api)

typer.run(main)
