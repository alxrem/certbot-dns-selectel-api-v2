try:
    from requests.exceptions import JSONDecodeError
except ImportError:
    try:
        from simplejson import JSONDecodeError
    except ImportError:
        from json import JSONDecodeError
