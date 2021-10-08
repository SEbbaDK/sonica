from _thread import start_new_thread
import random
from time import time, sleep

from pydub import AudioSegment
from simpleaudio import play_buffer

from song import Song

class Playlist:
    current: Song = None
    queue: list[Song] = []
    unplayed: list[Song] = []
    paused = False

    def __reset_player(self):
        self.play_start = None
        self.playback = None

    def __init__(self, library):
        self.library = library
        self.__reset_player()

    def __refill(self):
        next_library = [s for s in self.library.index]
        random.shuffle(next_library)
        self.unplayed += next_library

    def __autonext(self):
        while self.playback != None and self.playback.is_playing():
            sleep(0.25)
        if self.playback != None and not self.paused:
            self.current = None
            self.__reset_player()
            self.play()

    def play(self):
        if self.playback != None:
            raise Exception("Can't play while playing")

        if self.current == None:
            if len(self.queue) != 0:
                self.current = self.queue.pop(0)
            else:
                if len(self.unplayed) == 0:
                    self.__refill()
                self.current = self.unplayed.pop(0)

        # Unpause
        self.paused = False

        # Load the file
        s = AudioSegment.from_mp3(self.current.path)

        # Taken from the way pydub.playback.__play_with_simpleaudio does it
        # https://github.com/jiaaro/pydub/blob/master/pydub/playback.py#L41
        self.playback = play_buffer(
            s.raw_data,
            num_channels = s.channels,
            bytes_per_sample = s.sample_width,
            sample_rate = s.frame_rate
        )

        # Note the current time so we can check progression (and pause)
        self.play_start = time()

        # Start a thread to keep an eye on the playing song
        # and play a new one when done
        start_new_thread(self.__autonext, ())

    def is_playing(self):
        return self.playback != None

    def stop(self):
        if self.playback == None:
            raise Exception("Cannot stop playing when already stopped")
        self.playback.stop()
        self.paused = True
        self.__reset_player()

    def shuffle(self):
        random.shuffle(self.queue)
        random.shuffle(self.unplayed)

    def skip(self):
        was_playing = self.is_playing()
        self.stop()
        self.current = self.queue.pop(0) if len(self.queue) != 0 else None
        if was_playing:
            self.play()

    def enqueue(self, song: Song):
        if len(self.queue) == 0 and self.current == None:
            self.current = song
        else:
            self.queue.append(song)

    def enqueue_file(self, path):
        self.enqueue(self.library.get_song(path))

    def get_unplayed(self, amount: int = 3):
        if len(self.unplayed) < amount:
            self.__refill()
        return "\n".join([str(song) for song in self.unplayed[:amount]])
