#!/usr/bin/env python

import typer
import grpc
from sonica_pb2_grpc import SonicaStub
from sonica_pb2 import Status
import curses
from curses.textpad import Textbox, rectangle

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

def write_song(win, line, song):
	win.addstr(line,1, song.title)
	win.addstr(" - ")
	win.addstr(song.artist, curses.A_ITALIC)

def write_status(win):
	status = conn.status

	win.addstr(1,1, status.current.title, curses.A_BOLD)
	win.addstr(" - ")
	win.addstr(status.current.artist, curses.A_ITALIC)

	line = 3

	win.addstr(line,1, "QUEUE:", curses.A_BOLD)
	line += 1

	for s in status.queue:
		write_song(win, line, s)
		line += 1

	line += 1
	win.addstr(line,1, "AUTOPLAY:", curses.A_BOLD)
	line += 1

	for s in status.autoplay:
		win.addstr(line,1, s.title)
		win.addstr(" - ")
		win.addstr(s.artist, curses.A_ITALIC)
		line += 1

def sonica_tui(win):
	win.clear()
	curses.curs_set(0)
	height, width = win.getmaxyx()
	split = int(width * 0.5)

	left = curses.newwin(height, split, 0, 0)
	left.border()
	write_status(left)

	right = curses.newwin(height, width - split, 0, split + 1)
	right.border()
	right.addstr(1,1,'hi')

	left.refresh()
	right.refresh()

	while True:
		k = left.getch()
		print(k)
		if k == 27 or k == 113: # <ESC> or q
			exit()

def sonica_tui_cli(
		host : str = "localhost",
		port : int = 7700
	):
	global conn
	conn = Connection(host, port)
	curses.wrapper(sonica_tui)

if __name__ == "__main__":
	typer.run(sonica_tui_cli)

