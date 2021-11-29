from dataclasses import dataclass
import typing


@dataclass
class NonMatchingTypeException(Exception):
    expected: "typing.Any"
    got: "typing.Any"


@dataclass
class MissingElementException(Exception):
    elem: str


def validate(scheme, thing):
    if scheme is None:
        return thing
    if type(scheme) is dict:
        if type(thing) is dict:
            return {key: validate(scheme[key], e)
                    for key, e in thing.items()}
            pass
        else:
            raise NonMatchingTypeException(dict, type(thing))

    elif type(scheme) is list:
        if type(thing) is list:
            etype = scheme[0]
            return [validate(etype, e) for e in thing]
        else:
            raise NonMatchingTypeException(list, type(thing))

    elif scheme is type(thing):
        return thing

    else:
        raise NonMatchingTypeException(scheme, type(thing))
