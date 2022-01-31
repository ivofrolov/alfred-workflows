#!/usr/bin/env python3

import argparse
import json
import os
from urllib.error import HTTPError
from urllib.request import Request, urlopen


TRANSLATE_API_URL = 'https://translate.api.cloud.yandex.net/translate/v2/translate'


def alfred_output(query: str, result: str) -> str:
    return json.dumps(
        {
            'items': [
                {
                    'title': result,
                    'arg': query,
                    'text': {'copy': result, 'largetype': result},
                }
            ]
        },
        ensure_ascii=False,
    )


def translate(text: str, target_lang: str, *, api_key: str) -> str:
    request = Request(
        url=TRANSLATE_API_URL,
        data=json.dumps(
            {
                'targetLanguageCode': target_lang,
                'texts': [text],
            }
        ).encode(),
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Api-Key {api_key}',
        },
    )
    try:
        with urlopen(request) as response:
            return json.load(response)['translations'][0]['text']
    except HTTPError as error:
        return f'Error: {error.reason}'


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Translates words and phrases to english and russian.'
    )
    parser.add_argument(
        '--raw', action='store_true', help='print result as plain text.'
    )
    parser.add_argument('-t', '--target', help='target language code (en, ru, ...)')
    parser.add_argument('text')

    args = parser.parse_args()

    answer = translate(
        args.text, args.target, api_key=os.getenv('YANDEX_TRANSLATE_API_KEY', '')
    )

    if args.raw:
        print(answer)
    else:
        print(alfred_output(args.text, answer))
