from validate import validate
from typing import Tuple, List

import sonica_pb2 as pb2


api_methods = {}


def api_method(name: str, scheme = None):
    def decor(method_func):
        global api_methods

        def wrapper(sonica, socket, value):
            return method_func(sonica, socket, validate(scheme, value))

        api_methods[name] = wrapper
        return wrapper
    return decor


# The scheme is in the form (names, func)
# where names is either a list of names or a single name,
# and func maps from message field value to a serializable value
def dict_from_msg(msg, scheme):
    res = {}
    for (names, func) in scheme:
        # Map a single value to a list with said value
        names = [names] if type(names) is not list else names
        # Map None to id function
        func = (lambda x: x) if func is None else func

        for name in names:
            res[name] = func(getattr(msg, name))
    return res


def dict_from_song(song: pb2.Song):
    return dict_from_msg(song, [
        (["title", "artist", "album"], None)
    ])


@api_method("status", {"queue_max": int, "autoplay_max": int})
def status(sonica, socket, value):
    resp = sonica.Status(pb2.Status.Query(**value))
    return "status/info", dict_from_msg(resp, [
        ("current", dict_from_song),
        (["length", "progress", "queue_length", "queue_hash"], None),
        (["queue", "autoplay"], lambda x: [dict_from_song(s) for s in x])
    ])

