#!/usr/bin/env python3

import argparse
import datetime
import decimal
from functools import wraps
import json
import os
from pathlib import Path
import sys
from typing import Callable, Dict
import urllib.request
import xml.etree.ElementTree as ET


LOCAL_CURRENCY = 'rub'
MOSCOW_TZ = datetime.timezone(datetime.timedelta(hours=3), name='Europe/Moscow')
RATES_FILENAME = 'rates.xml'


def day_cached(filepath: Path, tz: datetime.tzinfo = None) -> Callable:
    """Caches decorated function return value in file for a day."""

    def decorator(func: Callable[..., bytes]) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            filepath.parent.mkdir(exist_ok=True)
            if filepath.exists():
                modified = datetime.datetime.fromtimestamp(
                    filepath.stat().st_mtime, tz=tz
                )
                now = datetime.datetime.now(tz=tz)
                if now.date() == modified.date():
                    return filepath.read_bytes()

            content = func(*args, **kwargs)
            filepath.write_bytes(content)
            return content

        return wrapper

    return decorator


def parse_number(value: str) -> decimal.Decimal:
    cleaned_value = value.replace(',', '.')
    try:
        return decimal.Decimal(cleaned_value)
    except decimal.InvalidOperation:
        raise ValueError(
            f'invalid number {value} - it should conform 3.14 or 3,14 format'
        )


@day_cached(
    filepath=Path(os.getenv('alfred_workflow_cache', '.')) / RATES_FILENAME,
    tz=MOSCOW_TZ,
)
def get_cbr_rates() -> bytes:
    """Returns cbr.ru exchange rates xml text."""
    url = 'http://www.cbr.ru/scripts/XML_daily_eng.asp'
    with urllib.request.urlopen(url) as response:
        body = response.read()
        return body


def parse_cbr_rates(text: bytes) -> Dict[str, decimal.Decimal]:
    """Converts xml text to currency:rate mapping for easier usage."""
    exchange_rates = {}

    root = ET.fromstring(text)
    for child in root:
        currency_code = child.findtext('CharCode').lower()
        nominal = parse_number(child.findtext('Nominal'))
        value = parse_number(child.findtext('Value'))
        exchange_rates[currency_code] = value / nominal

    return exchange_rates


def alfred_error(message: str) -> str:
    return json.dumps(
        {
            'items': [
                {
                    'title': 'Please, enter the valid query',
                    'subtitle': message,
                    'valid': False,
                }
            ]
        }
    )


def alfred_output(
    result: decimal.Decimal, amount: decimal.Decimal, source: str, target: str
) -> str:
    title = '{0:n} {1:s} = {2:n} {3:s}'.format(
        round(amount, 2), source.upper(), round(result, 2), target.upper()
    )
    arg = '{0:n}'.format(round(result, 2))
    return json.dumps(
        {
            'items': [
                {
                    'title': title,
                    'subtitle': 'Action this item to copy result to the clipboard',
                    'arg': arg,
                    'text': {'copy': arg, 'largetype': title},
                }
            ]
        }
    )


def convert(
    amount: decimal.Decimal, source: str, target: str, base: str = LOCAL_CURRENCY
) -> decimal.Decimal:
    """Returns an amount converted from one currency to another."""
    exchange_rates = parse_cbr_rates(get_cbr_rates())
    try:
        result = amount * exchange_rates[source]
        if target != base:
            result /= exchange_rates[target]
    except KeyError as exc:
        raise ValueError('"{0}" is invalid currency code'.format(*exc.args))
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Converts an amount from one currency to another.'
    )
    parser.add_argument(
        'amount',
        type=parse_number,
        help='amount to convert',
    )
    parser.add_argument(
        'source',
        help='source currency',
    )
    parser.add_argument(
        'target',
        nargs='?',
        default=LOCAL_CURRENCY.upper(),
        help='target currency (default is %(default)s)',
    )

    # Alfred encloses the whole query in quotes so wee need to unwrap it
    if len(sys.argv) == 2:
        input_args = sys.argv[1].split(' ')
    else:
        input_args = sys.argv[1:]

    args = parser.parse_args(args=input_args)

    try:
        result = convert(args.amount, args.source.lower(), args.target.lower())
    except Exception as exc:
        print(alfred_error(str(exc)))
        raise exc
    print(alfred_output(result, args.amount, args.source, args.target))
