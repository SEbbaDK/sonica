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
    print("Music message")
    if message.content.startswith("play "):
        query = message.content[len("play "):]
        search = library.search(query)
        lines = [ f"**{song['title']}** by *{song['artist']['name']}*" for song in search ]
        message = f"Search returned {len(search)} results\n" + "\n".join(lines)
        return await message.channel.send()
    if message.content.startswith("deez "):
        query = message.content[len("deez "):]
        search = dz.api.search(query)['data']
        lines = [ f"**{song['title']}** by *{song['artist']['name']}*" for song in search ]
        message = f"Search returned {len(search)} results\n" + "\n".join(lines)
        return await message.channel.send()
    if message.content.startswith("yt "):
        query = message.content[len("yt "):]
        search = YoutubeSearch(query).videos
        lines = [ f"**{video['title']}** by *{video['channel']}*" for video in search ]
        message = f"Search returned {len(search)} results\n" + "\n".join(lines)
        return await message.channel.send(message)

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
    client.run(api)

typer.run(main)
