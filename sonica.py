#!/usr/bin/env python

from dataclasses import dataclass

import typer
import discord
import deemix
from deezer import Deezer
from youtube_dl import YoutubeDL
from youtube_search import YoutubeSearch

from library import Library
from playlist import Playlist

library = None
playlist = None
client = discord.Client()
ytdl = YoutubeDL()
deezer = None

@dataclass
class EnumeratedOption:
    options = []
    type = None

enumerators = {}

async def handle_music_message(message):
    async def search(command, search_func, get_title_and_artist):
        query = message.content[len(command):]
        results = search_func(query)
        top_results = map(get_title_and_artist, results[0:10])
        lines = [
            f"{index+1}: **{title}** by *{artist}*"
        	for index, (title, artist) in enumerate(top_results)
        ]
        text = f"Search returned {len(results)} results\n" + "\n".join(lines)
        await message.channel.send(text)

    if message.content.startswith("play "):
        return await search("play ", library.search,
            lambda i: (i.title, i.artist))

    if message.content.startswith("deez "):
        return await search("deez ", lambda q: dz.api.search(q)['data'],
            lambda i: (i['title'], i['artist']['name']))

    if message.content.startswith("yt "):
        return await search("yt ", lambda q: YoutubeSearch(q).videos,
            lambda i: (i['title'], i['channel']))

    async def try_command(func, else_message, runIfPlaying = True):
        global playlist
        if runIfPlaying == playlist.is_playing():
            func()
        else:
            await message.channel.send(else_message)

    global playlist
    if message.content == "skip":
        return await try_command(playlist.skip, "I can't skip if i am not playing TwT")
    if message.content == "stop":
        return await try_command(playlist.stop, "I'm not playing anything you dummy >\:(")
    if message.content == "play":
        return await try_command(playlist.play, "I'm already playing!!", runIfPlaying = False)

    try:
        index = int(message.content) - 1 # We add show them 1-indexed
        return await message.channel.send(f"I will try playing {index}")
    except Exception:
        pass


@client.event
async def on_ready():
    print(f"Logged in as {client.user}")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    print(str(message) + ": '" + message.content + "'")

    if "music" in message.channel.name or "musik" in message.channel.name:
        await handle_music_message(message)


def main(api: str, deez_arl: str = None, folder: str = "music"):
    global library, playlist, dz
    if deez_arl != None:
        dz = Deezer()
        dz.login_via_arl(deez_arl)
    library = Library(folder)
    print(f"Library contains {library.size} songs")
    playlist = Playlist(library)
    # playlist.play()
    client.run(api)

typer.run(main)
