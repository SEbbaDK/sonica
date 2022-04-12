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
    def play(self):
        self.converse(M_play(), {})

    def exit(self):
        self.converse(M_exit(), {})
