#!/usr/bin/env python3

import json
import re
import subprocess
from typing import Iterable, Iterator, Literal, NamedTuple


class VpnService(NamedTuple):
    state: Literal['connected', 'disconnected']
    name: str


def get_vpn_services(filter_: str) -> Iterator[VpnService]:
    pattern = re.compile(rf'^\*\s+\((?P<state>\w+)\).+"(?P<name>.+)"\s+\[{filter_}\]$')
    command = ['scutil', '--nc', 'list']
    process = subprocess.run(command, capture_output=True, text=True, check=True)
    for line in process.stdout.splitlines():
        if match := re.match(pattern, line):
            yield VpnService(state=match['state'].lower(), name=match['name'])


def alfred_output(services: Iterable[VpnService]) -> str:
    items = []
    for state, name in services:
        command = 'connect' if state == 'disconnected' else 'disconnect'
        items.append(
            {
                'title': f'{command.title()} {name}',
                'arg': f'{name}',
                'variables': {
                    'command': command,
                },
            }
        )
    return json.dumps({'items': items})


if __name__ == '__main__':
    services_filter = '(PPP:L2TP|VPN:.+)'
    print(alfred_output(get_vpn_services(services_filter)))
