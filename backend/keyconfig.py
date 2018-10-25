
from configparser import RawConfigParser


class ClassifiedDict(dict):
    """A dict of sensitive info. Avoids accidental logging.

    Intended for use as request.registry.settings['keys'] in Pyramid apps.
    """

    def __repr__(self):
        return '<ClassifiedDict {0}>'.format(id(self))

    def __str__(self):
        return repr(self)


def read_keys(fn):
    cp = RawConfigParser()
    cp.read([fn])
    res = ClassifiedDict()
    for name, value in cp.items('keys'):
        res[name] = value
    return res
