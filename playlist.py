from _thread import start_new_thread
import random
from time import time, sleep

from pydub import AudioSegment
from simpleaudio import play_buffer

class Playlist:
    queue = []
    unplayed = []
    paused = False

    def __reset_player(self):
        self.current = None
        self.play_start = None
        self.playback = None

    def __init__(self, library):
        self.library = library
        self.__reset_player()

    def __refill(self):
        self.unplayed = [ s for s in self.library.index ]

    def __autonext(self):
        while self.playback != None and self.playback.is_playing():
            sleep(0.25)
        if not self.paused:
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
        self.__reset_player()
        self.paused = True

    def shuffle(self):
        random.shuffle(self.queue)
        random.shuffle(self.unplayed)

    def skip(self):
        self.stop()
        self.play()

