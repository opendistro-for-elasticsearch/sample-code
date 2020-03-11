'''
Copyright 2020, Amazon Web Services Inc.
This code is licensed under MIT license (see LICENSE.txt for details)

Python 3

Provides a buffer object that holds log lines in Elasticsearch _bulk
format. As each line is added, the buffer stores the control line
as well as the log line.
'''

import re
import time


from datetime import datetime
from dateutil import tz
from pytz import timezone


def now_pst():
    '''Return the current time in PST timezone'''
    now_utc = datetime.now(timezone('UTC'))
    return now_utc.astimezone(timezone('US/Pacific'))


def utc_to_local_datetime(timestamp):
    ''' Takes a UTC timestamp (as seconds since the epoch) and converts to a
        local datetime object '''
    # Could validate data type
    tdt = datetime.fromtimestamp(timestamp, tz=tz.tzlocal())
    tdt = tdt.replace(tzinfo=tz.gettz('UTC'))
    return tdt.astimezone(tz.tzlocal())


def has_path(dic, path_elts):
    '''Given dict dic, and path path_elts, successively dereference the keys
       from path_elts, returning True. Returns False if the path is not in the
       dictionary'''
    if not isinstance(dic, dict) and path_elts:
        return False
    if not path_elts:
        return True
    if path_elts[0] in dic:
        return has_path(dic[path_elts[0]],
                        path_elts[1:])
    return False


def valid_key(key_in):
    '''Mutates key_in, making it a valid field name for Elasticsearch (and
       hence, a suitable key for a dict.)'''
    pattern = re.compile('[^a-zA-Z0-9@_]')
    return pattern.sub('_', key_in)


def flatten(current, key, result):
    '''Takes a path to an element in a nested dict (e.g., JSON) and recursively
       walks the whole tree, returning a 1-layer dict, with elements where the
       keys are the path elements joined with '_' and the values are the leaf
       values from the dict.
       flatten({'a': {'b':'c', 'd': 'e'}}, '', {}) =>
           {'a_b': 'c', 'a_d': 'e'}'''
    if isinstance(current, dict):
        for thiskey in current:
            valid_k = valid_key(str(thiskey))
            new_key = "{0}_{1}".format(key, valid_k) if len(key) > 0 else valid_k
            flatten(current[thiskey], new_key, result)
    else:
        result[key] = current
    return result


def valid_request_body(body):
    ''' Helper function to ensure request bodies terminate with a new line
        and to replace None with the empty string.'''
    if body and not body.endswith("\n"):
        body += "\n"
    elif not body:
        body = ""
    return body


def wall_time(func, *args, **kwargs):
    ''' Helper function to wrap the request and return wall time along with
        the result of the call. Not using clock() since the processing
        happens remotely.'''
    start = time.time()
    result = func(*args, **kwargs)
    end = time.time()
    return (result, end - start)
