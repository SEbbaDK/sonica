from typing import Callable, Coroutine
from dataclasses import dataclass


@dataclass
class Message:
    name: str


@dataclass
class Conversation:
    start: Message
    term: list[Message] = list
    nonterm: list[Message] = list


@dataclass
class Role:
    name: str
    conversations: list[Conversation]

    def converse(self, msg: Message, handlers):
        pass

# TEST SPEC HERE BELOW
class M_play(Message):
    pass


class M_exit(Message):
    pass


class M_status_query(Message):
    queue_amount: int
    autoplay_amount: int


class M_song(Message):
    artist: str
    title: str
    album: str


class M_status_answer(Message):
    queue: list[M_song]
    autoplay: list[M_song]


class R_daemon(Role):
    def local(status_query_handler: Callable[[M_status_query], Coroutine[None]],
              play_handler: Callable[[M_play], Coroutine[None]]):
        return R_daemon(False, {
            M_status_query: status_query_handler,
            M_play: play_handler,
        })

    def status_query(self,
                     queue_amount: int,
                     autoplay_amount: int,
                     status_answer_callback: Callable[[M_status_answer], Coroutine[None]]):
        self.converse(M_status_query(queue_amount, autoplay_amount), {
            M_status_answer: status_answer_callback
        })

    def play(self):
        pass


class R_client(Role):
    def local(play_handler: Callable[[M_play], Coroutine[None]],
              exit_handler: Callable[[M_exit], Coroutine[None]]):
        R_client(False, {
            M_play: play_handler,
            M_exit: exit_handler,
        })

    def play(self):
        self.converse(M_play(), {})

    def exit(self):
        self.converse(M_exit(), {})


# DLASKDJSAL
import sys


async def play_handler():
    pass


async def exit_handler():
    sys.exit(1)

client = R_client(play_handler, exit_handler)
client.listen("localhost", 4444)
