from validate import validate
from typing import Tuple, List

import sonica_pb2 as pb2


api_methods = {}


class ApiException(Exception):
    def serial(self):
        return str(self)


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
def dict_from_lookup(msg, scheme, lookup):
    res = {}
    for (names, func) in scheme:
        # Map a single value to a list with said value
        names = [names] if type(names) is not list else names
        # Map None to id function
        func = (lambda x: x) if func is None else func

        for name in names:
            res[name] = func(lookup(msg, name))
    return res


def dict_from_msg(msg, scheme):
    return dict_from_lookup(msg, scheme, getattr)


def dict_from_dict(msg, scheme):
    def lookup(thing, key):
        return thing[key]
    return dict_from_lookup(msg, scheme, lookup)


def dict_from_song(song: pb2.Song):
    return dict_from_msg(song, [
        (["title", "artist", "album"], None)
    ])


def response_from_result(res: pb2.Result):
    if res.success:
        return "Return", {}
    else:
        return "Error", { "message" : res.reason }


type_hash = {"value": int}
type_target = {"index": int}


@api_method("Play", {})
def play(sonica, socket, value):
    resp = sonica.Play(pb2.Empty())
    return response_from_result(resp)


@api_method("Stop", {})
def stop(sonica, socket, value):
    resp = sonica.Stop(pb2.Empty())
    return response_from_result(resp)


@api_method("Skip", {})
def skip(sonica, socket, value):
    resp = sonica.Skip(pb2.Empty())
    return response_from_result(resp)


@api_method("Clear", type_hash)
def clear(sonica, socket, value):
    resp = sonica.Clear(pb2.Queue.Hash(**value))
    return response_from_result(resp)


@api_method("Shuffle", {"hash": type_hash, "queue": bool, "autoplay": bool})
def shuffle(sonica, socket, value):
    resp = sonica.Shuffle(pb2.Queue.ShuffleTargets(**dict_from_dict(value, [
        ("hash", pb2.Queue.Hash),
        (["queue", "autoplay"], None),
    ])))
    return response_from_result(resp)


@api_method("Move", {"hash": type_hash, "from_index": type_target, "to_index": type_target})
def move(sonica, socket, value):
    resp = sonica.Move(pb2.Queue.Pair(**dict_from_dict(value, [
        ("hash", lambda x: pb2.Queue.Hash(**x)),
        (["from_index", "to_index"], lambda x: pb2.Queue.Target(**x))
    ])))
    return response_from_result(resp)


@api_method("Remove", type_target)
def remove(sonica, socket, value):
    resp = sonica.Remove(pb2.Queue.Target(**value))
    return response_from_result(resp)


@api_method("Search", {"query": [str], "engines": [str]})
def search(sonica, socket, value):
    resp = sonica.Search(pb2.Search.Query(**value))
    return "ReturnSearch", dict_from_msg(resp, [
        ("results", lambda x: [dict_from_msg(res, [
                ("name", None),
                ("possibilities", lambda x: {k: dict_from_song(v) for k, v in x.items()}),
            ]) for res in x]),
    ])


@api_method("Choose", {"possibility_id": str, "add_to_top": bool})
def choose(sonica, socket, value):
    value['possibility_id'] = int(value['possibility_id'])
    resp = sonica.Choose(pb2.Search.Choice(**value))
    return response_from_result(resp)


@api_method("Engines", {})
def engines(sonica, socket, value):
    resp = sonica.Engines(pb2.Empty())
    return "ReturnEngines", dict_from_msg(resp, [
        ("engines", lambda x: [e for e in x])
    ])


@api_method("Status", {"queue_max": int, "autoplay_max": int})
def status(sonica, socket, value):
    resp = sonica.Status(pb2.Status.Query(**value))
    return "ReturnStatus", dict_from_msg(resp, [
        ("current", dict_from_song),
        (["length", "progress", "queue_length", "queue_hash"], None),
        (["queue", "autoplay"], lambda x: [dict_from_song(s) for s in x])
    ])


@api_method("Library", {})
def library(sonica, socket, value):
    resp = sonica.Library(pb2.Empty())
    return "ReturnLibrary", dict_from_msg(resp, [
        ("size", None),
        ("songs", lambda x: [dict_from_song(s) for s in x]),
    ])
