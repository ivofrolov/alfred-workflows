#!/usr/bin/env python3

import argparse
import json
import os
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import urlopen


SHORT_ANSWER_API_URL = 'https://api.wolframalpha.com/v1/result'


def alfred_output(query: str, result: str):
    return json.dumps(
        {
            'items': [
                {
                    'title': result,
                    'arg': query,
                    'text': {'copy': result, 'largetype': result},
                }
            ]
        }
    )


def short_answer(query: str, *, api_key: str) -> str:
    try:
        response = urlopen(
            SHORT_ANSWER_API_URL + '?' + urlencode({'appid': api_key, 'i': query})
        )
    except HTTPError as error:
        # API provides quite readable error descriptions
        response = error
    return response.read().decode()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Gives answers to questions about life, the universe and everything.'
    )
    parser.add_argument('question')
    parser.add_argument(
        '--raw', action='store_true', help='print result as plain text.'
    )
    args = parser.parse_args()

    answer = short_answer(args.question, api_key=os.getenv('WOLFRAM_ALPHA_API_KEY', ''))
    if args.raw:
        print(answer)
    else:
        print(alfred_output(args.question, answer))
