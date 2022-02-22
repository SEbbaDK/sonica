from dataclasses import dataclass
import typing


class ValidationException(Exception):
    pass


@dataclass
class NonMatchingTypeException(ValidationException):
    expected: "typing.Any"
    got: "typing.Any"

    def __str__(self):
        return f"unexpected element type '{self.got}', expected '{self.expected}'"


@dataclass
class MissingElementException(ValidationException):
    elem: str

    def __str__(self):
        return f"element '{self.elem}' missing"


def validate(scheme, thing):
    if scheme is None:
        return thing
    if type(scheme) is dict:
        if type(thing) is dict:
            try:
                return {key: validate(t, thing[key])
                        for key, t in scheme.items()}
            except KeyError as e:
                raise MissingElementException(e.args[0])
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
