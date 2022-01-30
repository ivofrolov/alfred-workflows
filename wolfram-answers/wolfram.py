from os import getenv
from urllib import urlencode
from urllib2 import urlopen, HTTPError
from functools import wraps
import json


SHORT_ANSWER_API_URL = 'https://api.wolframalpha.com/v1/result'


def alfred_format(f):
    @wraps(f)
    def wrapper(query, *args, **kwargs):
        result = f(query, *args, **kwargs)
        return json.dumps({'items': [{
            'title': result,
            'arg': query,
            'text': {'copy': result, 'largetype': result}
        }]})
    return wrapper


@alfred_format
def short_answer(query):
    q = urlencode({'appid': getenv('WOLFRAM_ALPHA_API_KEY'), 'i': query})
    try:
        response = urlopen(SHORT_ANSWER_API_URL + '?' + q)
    except HTTPError as error:
        # API provides quite readable error descriptions
        response = error 
    return response.read()


if __name__ == '__main__':
    import sys
    result = json.loads(short_answer(' '.join(sys.argv[1:])))
    if result.get('items'):
        print result['items'][0].get('title', '')
