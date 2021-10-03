#!/usr/bin/env python

import typer
import discord

from library import Library
from playlist import Playlist
from players import LibraryPlayer, DeezPlayer, YoutubePlayer

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
            results = player.search(player.strip_command(message.content))

            text = "I found a bunch of songs:\n" + "\n".join([
                f"{index + 1}: {song}" for (index, song) in enumerate(results)
            ])

            def enqueue_songchoice(songchoice):
                filename = songchoice.get_filename()
                song = library.get_song(filename)
                playlist.enqueue(song)
            enumerators[message.channel.id] = EnumeratedOption({
                str(index + 1): lambda: enqueue_songchoice(songchoice)
                for (index, songchoice) in enumerate(results)
            })

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

    if enumerators[message.channel.id].is_an_option(message.content):
        enumerators[message.channel.id].options[message.content]()
        del enumerators[message.channel.id]

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    #print(str(message) + ": '" + message.content + "'")

    if "music" in message.channel.name or "musik" in message.channel.name:
        await handle_music_message(message)


def main(api: str, deez_arl: str = None, folder: str = "music"):
    global library, playlist, players
    library = Library(folder)
    print(f"Library contains {library.size()} songs")
    playlist = Playlist(library)
    # playlist.play()
    players = [
        LibraryPlayer(library),
        YoutubePlayer(),
    ] + ([ DeezPlayer(deez_arl) ] if deez_arl != None else [])
    client.run(api)

typer.run(main)
