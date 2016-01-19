from __future__ import division, absolute_import, unicode_literals

from datetime import datetime, timedelta

def datetime_to_timestamp(dt, epoch=datetime(1970,1,1)):
    '''takes a python datetime object and converts it to a Unix timestamp.

    This is a non-timezone-aware function.

    Args:
        dt (datetime): Python datetime to convert to timestamp
        epoch (datetime): optional specification of start of epoch [default: 1/1/1970]

    Returns:
        timestamp (float)
    '''
    td = dt - epoch
    # return td.total_seconds()
    return (td.microseconds + (td.seconds + td.days * 86400) * 10**6) / 10**6 

