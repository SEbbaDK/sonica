#!/usr/bin/env python

import grpc
import typer
import discord
from discord.ext import commands

from sonica_pb2_grpc import SonicaStub
from sonica_pb2 import Empty

bot = commands.Bot(command_prefix='')
channel = grpc.insecure_channel('localhost:7700')
print("Trying to connect to Sonica daemon...")
# TODO: Implement some timeout wait if the daemon isn't running or something goes wrong
daemon = SonicaStub(channel)

@bot.command()
async def play(ctx):
    res = daemon.Play(Empty())
    await ctx.message.channel.send(f'result: {str(res.success)}')


@bot.event
async def on_ready():
    print(f"Logged on as {bot.user}!")

def main(token : str):
    print("Logging in...")
    bot.run(token)

typer.run(main)

