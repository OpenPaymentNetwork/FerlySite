
"""Parameter parsing functions"""


import datetime
import re


datetime_re = re.compile(
    r'(\d{4})-(\d\d)-(\d\d)'             # date
    r'[T ](\d\d):(\d\d):(\d\d)(\.\d+)?'  # time
    r'(Z|[\+\-]\d\d:?\d\d)?$')           # time zone


def to_datetime(input_str, allow_none=False):
    """Convert a datetime.isoformat() string back to a datetime.

    Accepts a time zone, but converts the datetime to UTC.  (Python's
    support for time zone awareness would add unnecessary complexity to
    most code that uses this function.)
    """
    if allow_none and input_str is None:
        return None
    mo = datetime_re.match(input_str)
    if mo is None:
        raise ValueError("Not a valid datetime: %s" % repr(input_str))
    y, m, d, H, M, S, SS, tz = mo.groups()
    if SS:
        if len(SS) < 7:
            # Pad to microseconds.
            SS = (SS + '000000')[:7]
        ms = int(SS[1:7])
    else:
        ms = 0
    res = datetime.datetime(int(y), int(m), int(d), int(H), int(M), int(S), ms)
    if tz and tz not in ('Z', '+00:00', '-00:00'):
        # Convert to UTC.
        hours = int(tz[:3])
        minutes = int(tz[4:])
        sign = -1 if hours < 0 else 1
        offset = hours * 3600 + sign * minutes * 60
        res -= datetime.timedelta(seconds=offset)
    return res
