from __future__ import division, absolute_import
from datetime import datetime, timedelta

def datetime_to_timestamp(dt, epoch=datetime(1970,1,1)):
    '''takes a python datetime object and converts it to a Unix timestamp.

    This is a non-timezone-aware function.

    :param: dt (datetime)
    :return: timestamp (float)
    '''
    td = dt - epoch
    # return td.total_seconds()
    return (td.microseconds + (td.seconds + td.days * 86400) * 10**6) / 10**6 

