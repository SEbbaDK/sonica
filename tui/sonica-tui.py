#!/usr/bin/env python

import typer
import grpc
from sonica_pb2_grpc import	SonicaStub
from sonica_pb2	import Status
import urwid

class Connection:
	channel	= None
	daemon = None

	def	__init__(self, host, port):
		self.channel = grpc.insecure_channel(f'{host}:{port}')
		self.daemon	= SonicaStub(self.channel)
		self.refresh()

	status = None
	def	refresh(self):
		self.status	= self.daemon.Status(
			Status.Query( queue_max	= -1, autoplay_max = -1	)
		)

def	Song(song):
	return urwid.Columns([
		(3,	urwid.Text(' • ')),
		('weight', 2, urwid.Text(('bold', song.title))),
		('weight', 1, urwid.Text(('italic',	song.artist))),
	])

def	CurrentBar(song):
	has_current	= (song.title != '')
	return urwid.Columns([
		('pack', urwid.Text(('bold', ' ⏹ ' if has_current else ' ▶ '))),
		('pack', urwid.Text(('bold', ' ⏭  '))),
		('pack', urwid.Text([
			('bold', song.title),
			' -	' if has_current else '',
			('italic', song.artist),
		])),
	])

search_mode	= False

def	sonica_tui():
	base = urwid.ListBox([
		urwid.LineBox(
			CurrentBar(conn.status.current)
		),
		urwid.Pile([
			urwid.LineBox(
				title =	'Queue',
				title_attr = 'bold',
				original_widget = urwid.Pile([
					urwid.Pile([ Song(s) for s in conn.status.queue	]),
				]),
			),
			urwid.LineBox(
				title =	'Autoplay',
				title_attr = 'bold',
				original_widget = urwid.Pile([
					urwid.Pile([ Song(s) for s in conn.status.autoplay ]),
				]),
			),
		])
	])
	search = urwid.LineBox(
		urwid.ListBox([
			urwid.Edit(caption = ('dark red', 'Search: ')),
		]),
		title =	'Search',
		title_attr = 'bold',
	)
	if search_mode:
		return urwid.Overlay(search, base, 'center', ('relative', 75), 'middle', 3)
	else:
		return base

def	events(key):
	global search_mode
	if key == 'esc':
		if search_mode:
			search_mode	= False
			loop.widget	= sonica_tui()
		else:
			raise urwid.ExitMainLoop()
	if key == 's':
		search_mode	= True
		loop.widget	= sonica_tui()
	if key == 'enter':
		search_mode	= False
		loop.widget	= sonica_tui()
	return key

def	sonica_tui_cli(
		host : str = 'localhost',
		port : int = 7700
	):
	global conn, loop
	conn = Connection(host,	port)
	loop = urwid.MainLoop(sonica_tui(),	unhandled_input=events,	handle_mouse=False)
	loop.run()

if __name__	== '__main__':
	typer.run(sonica_tui_cli)

