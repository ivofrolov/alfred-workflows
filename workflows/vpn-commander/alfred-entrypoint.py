#!/usr/bin/env python3

import json
import re
import subprocess
from typing import Iterable, Iterator, Literal, NamedTuple


class VpnService(NamedTuple):
    state: Literal["connected", "disconnected"]
    name: str
    uid: str


def get_vpn_services(filter_: str) -> Iterator[VpnService]:
    command = ["scutil", "--nc", "list"]
    process = subprocess.run(command, capture_output=True, text=True, check=True)
    pattern = re.compile(
        rf"""
        ^
        \*
        \s+
        \((?P<state>\w+)\)
        \s+
        (?P<uid>[\w-]+)
        \s+
        (?:\w+)
        \s+
        \((?:[\w.]+)\)
        \s+
        "(?P<name>\S+)"
        \s+
        \[{filter_}\]
        $
        """,
        re.X,
    )
    for line in process.stdout.splitlines():
        if match := re.match(pattern, line):
            yield VpnService(
                state=match["state"].lower(),
                name=match["name"],
                uid=match["uid"],
            )


def alfred_output(services: Iterable[VpnService]) -> str:
    items = []
    for state, name, uid in sorted(services):
        command = "connect" if state == "disconnected" else "disconnect"
        items.append(
            {
                "arg": f"{name}",
                "match": name.replace("-", " "),
                "title": f"{command.title()} {name}",
                "uid": uid,
                "variables": {
                    "command": command,
                },
            }
        )
    return json.dumps({"items": items})


if __name__ == "__main__":
    services_filter = "(PPP:L2TP|VPN:.+)"
    print(alfred_output(get_vpn_services(services_filter)))
