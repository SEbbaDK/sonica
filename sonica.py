#!/usr/bin/env python

from dataclasses import dataclass

import typer
from playsound import playsound
import discord
import deemix
from deezer import Deezer
from youtube_dl import YoutubeDL
from youtube_search import YoutubeSearch

from library import Library

library = None
client = discord.Client()
ytdl = YoutubeDL()
deezer = None

@dataclass
class EnumeratedOption:
    options = []
    type = None

enumerators = {}

async def handle_music_message(message):
    def line(title, artist):
        return f"**{title}** by *{artist}*"
    def show(count, lines):
        return f"Search returned {count} results\n" + "\n".join(lines)
    async def search(command, search_func, get_title, get_artist):
        if message.content.startswith(command + " "):
            query = message.content[len(command)+1:]
            results = search_func(query)
            lines = [ line(get_title(item), get_artist(item)) for item in results ]
            text = show(len(results), lines)
            return await message.channel.send(text)

    await search("play", library.search,
        lambda i: i.title, lambda i: i.artist)
    await search("deez", lambda q: dz.api.search(q)['data'],
        lambda i: i['title'], lambda i: i['artist']['name'])
    await search("yt", lambda q: YoutubeSearch(q).videos,
        lambda i: i['title'], lambda i: i['channel'])

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
    global library, dz
    if deez_arl != None:
        dz = Deezer()
        dz.login_via_arl(deez_arl)
    library = Library(folder)
    print(f"Library contains {library.size} songs")
    client.run(api)

typer.run(main)
