from __future__ import division, absolute_import, unicode_literals

from datetime import datetime


def datetime_to_timestamp(dt, epoch=datetime(1970,1,1)):
    """takes a python datetime object and converts it to a Unix timestamp.

    This is a non-timezone-aware function.

    :param dt: datetime to convert to timestamp
    :param epoch: datetime, option specification of start of epoch [default: 1/1/1970]
    :return: timestamp
    """
    td = dt - epoch
    return (td.microseconds + (td.seconds + td.days * 86400) * 10**6) / 10**6
