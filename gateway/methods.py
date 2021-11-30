from validate import validate

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


def dict_from_song(song: pb2.Song):
    return {
        "title": song.title,
        "artist": song.artist,
        "album": song.album,
    }


@api_method("status", {"queue_max": int, "autoplay_max": int})
def status(sonica, socket, value):
    print("Status", value)
    resp = sonica.Status(pb2.Status.Query(**value))
    return "status/info", {
        "current": dict_from_song(resp.current),
        "length": resp.length,
        "progress": resp.progress,
        "queue_length": resp.queue_length,
        "queue_hash": resp.queue_hash,
        "queue": [dict_from_song(s) for s in resp.queue],
        "autoplay": [dict_from_song(s) for s in resp.autoplay],
    }

