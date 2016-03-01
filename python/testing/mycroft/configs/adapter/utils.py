#encoding=utf-8
import sys
import threading
from inspect import isgenerator
from django.utils.encoding import force_text
from django.utils.functional import Promise

def new_thread(isdaemon=False):
    def wrapper(func):
        def inner(*args, **kwargs):
            def f():
                func(*args, **kwargs)
                sys.exit()
            t = threading.Thread(target=f)
            t.daemon = isdaemon
            t.start()
        return inner
    return wrapper

def encode(data, charset):
    if isinstance(data, Promise):
        data = force_text(data)

    if isinstance(data, str):
        return data
    elif isinstance(data, unicode):
        return data.encode(charset)
    elif isinstance(data, dict):
        return type(data)((encode(k, charset), encode(v, charset)) for k,v in data.iteritems())
    elif isinstance(data, (list, tuple)):
        return type(data)(encode(d, charset) for d in data)
    elif isgenerator(data):
        return (encode(d, charset) for d in data)
    else:
        return data

def decode(data, charset):
    if isinstance(data, Promise):
        data = force_text(data)

    if isinstance(data, unicode):
        return data
    elif isinstance(data, str):
        return data.decode(charset)
    elif isinstance(data, dict):
        return type(data)((decode(k, charset), decode(v, charset)) for k,v in data.iteritems())
    elif isinstance(data, (list, tuple)):
        return type(data)(decode(d, charset) for d in data)
    elif isgenerator(data):
        return (decode(d, charset) for d in data)
    else:
        return data
