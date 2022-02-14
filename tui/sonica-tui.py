#!/usr/bin/env python

import typer
import grpc
from sonica_pb2_grpc import SonicaStub
from sonica_pb2 import Status
import urwid

class Connection:
	channel = None
	daemon = None

	def __init__(self, host, port):
		self.channel = grpc.insecure_channel(f"{host}:{port}")
		self.daemon = SonicaStub(self.channel)
		self.refresh()

	status = None
	def refresh(self):
		self.status = self.daemon.Status(
			Status.Query( queue_max = -1, autoplay_max = -1 )
		)

def Song(song):
	return urwid.Columns([
    	('weight', 2, urwid.Text(('bold', song.title))),
		('weight', 1, urwid.Text(('italic', song.artist))),
	])

search = ""

def sonica_tui():
    return urwid.ListBox([
    	urwid.LineBox(
        	Song(conn.status.current)
    	),
		urwid.Pile([
			urwid.LineBox(urwid.Pile([
    			urwid.Text(('bold', 'Queue:')),
    			urwid.Pile([ Song(s) for s in conn.status.queue ]),
			])),
			urwid.LineBox(urwid.Pile([
    			urwid.Text(('bold', 'Autoplay:')),
    			urwid.Pile([ Song(s) for s in conn.status.autoplay ]),
			])),
		])
	])

def events(keys, raw):
    return keys

def sonica_tui_cli(
		host : str = "localhost",
		port : int = 7700
	):
	global conn
	conn = Connection(host, port)
	loop = urwid.MainLoop(sonica_tui(), input_filter=events)
	loop.run()

if __name__ == "__main__":
	typer.run(sonica_tui_cli)

