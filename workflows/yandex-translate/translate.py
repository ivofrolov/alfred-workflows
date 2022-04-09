#!/usr/bin/env python3

import argparse
from itertools import chain
import json
import os
from typing import Iterable, Iterator, List, NamedTuple
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


TRANSLATE_API_URL = 'https://translate.api.cloud.yandex.net/translate/v2/translate'
DICTIONARY_API_URL = 'https://dictionary.yandex.net/api/v1/dicservice.json/lookup'


class DictionaryError(Exception):
    ...


class DictionaryResult(NamedTuple):
    definition: str
    synonyms: List[str] = []
    meanings: List[str] = []

    def __str__(self) -> str:
        result = self.definition
        if self.synonyms:
            result = ', '.join([result] + self.synonyms)
        if self.meanings:
            result += '\n' + ', '.join(self.meanings)
        return result


def alfred_output(query: str, results: Iterable[DictionaryResult]) -> str:
    items = []

    for result in results:
        title = result.definition
        if result.synonyms:
            title = ', '.join([title] + result.synonyms)

        subtitle = ', '.join(result.meanings)

        largetype = title + '\n' + subtitle

        items.append(
            {
                'arg': query,
                'title': title,
                'subtitle': subtitle,
                'text': {'copy': result.definition, 'largetype': largetype},
            }
        )

    return json.dumps({'items': items}, ensure_ascii=False)


def lookup(
    word: str, source_lang: str, target_lang: str, *, api_key: str
) -> Iterator[DictionaryResult]:
    query = urlencode(
        {'text': word, 'lang': f'{source_lang}-{target_lang}', 'key': api_key}
    )
    try:
        with urlopen(f'{DICTIONARY_API_URL}?{query}') as response:
            dict_result = json.load(response)
            for definition in dict_result['def']:
                for translation in definition['tr']:
                    synonyms = [
                        synonym['text'] for synonym in translation.get('syn', [])
                    ]
                    meanings = [mean['text'] for mean in translation.get('mean', [])]
                    yield DictionaryResult(
                        definition=translation['text'],
                        synonyms=synonyms,
                        meanings=meanings,
                    )
    except HTTPError as exc:
        error = json.load(exc)
        raise DictionaryError(error['message']) from exc


def translate(
    text: str, source_lang: str, target_lang: str, *, api_key: str
) -> Iterator[DictionaryResult]:
    request = Request(
        url=TRANSLATE_API_URL,
        data=json.dumps(
            {
                'sourceLanguageCode': source_lang,
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
            text = json.load(response)['translations'][0]['text']
            yield DictionaryResult(definition=text)
    except HTTPError as exc:
        raise DictionaryError(f'Error: {exc.reason}') from exc


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Translates words and phrases to english and russian.'
    )
    parser.add_argument(
        '--raw', action='store_true', help='print result as plain text.'
    )
    parser.add_argument('-s', '--source', help='source language code (en, ru, ...)')
    parser.add_argument('-t', '--target', help='target language code (en, ru, ...)')
    parser.add_argument('text')

    args = parser.parse_args()

    answers = chain(
        translate(
            args.text,
            args.source,
            args.target,
            api_key=os.getenv('YANDEX_TRANSLATE_API_KEY', ''),
        ),
        lookup(
            args.text,
            args.source,
            args.target,
            api_key=os.getenv('YANDEX_DICTIONARY_API_KEY', ''),
        ),
    )

    if args.raw:
        print('\n\n'.join(map(str, answers)))
    else:
        print(alfred_output(args.text, answers))
