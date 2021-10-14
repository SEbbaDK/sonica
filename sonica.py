#!/usr/bin/env python

import typer
import discord
import asyncio

from library import Library
from playlist import Playlist
from players import LibraryPlayer, DeezPlayer#, YoutubePlayer
from song import Song

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


def update_presence(song: Song):
    # Set presence to "Playing [song] by [artist]"
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        pass

    act = discord.Game(f"{song.title} by {song.artist}")  # "Playing ..."
    # As an alternative, there is also the activity below.
    # listening = discord.ActivityType.listening
    # act = discord.Activity(type=listening, name=f"{song.title} by {song.artist}")  # "Listening to ..."
    loop.create_task(client.change_presence(activity=act))


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

    async def try_command(func, else_message, runIfPlaying=True):
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
        return await try_command(playlist.play, "I'm already playing!!", runIfPlaying=False)

    if message.content in ["playlist", "queue", "current", "playing", "now"]:
        return_message = ""
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

    if message.content == "shuffle":
        playlist.shuffle()
        return await message.channel.send("Queue shuffled!")

    if message.content == "shuffleall":
        playlist.shuffleall()
        return await message.channel.send("Queue and backlog shuffled!")

    channel_enum = enumerators[message.channel.id]
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


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    #print(str(message) + ": '" + message.content + "'")

    if message.content == "help":
        return await message.channel.send(help_message())
    if message.content == "changelog":
        return await message.channel.send(changelog_message())

    music_only_commands = ["play", "stop", "skip", "queue", "playlist", "shuffle", "shuffleall"]
    player_commands = [player.command for player in players]
    if any(music in message.channel.name for music in ["music", "musik"]):
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
    ] + ([DeezPlayer(deez_arl)] if deez_arl != None else [])
    playlist.song_changed_subscribe(update_presence)
    client.run(api)


typer.run(main)
