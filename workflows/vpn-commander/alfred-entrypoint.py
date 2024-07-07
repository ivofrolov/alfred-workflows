#!/usr/bin/env python3

import os
import json
import re
import subprocess
from typing import Iterable, Iterator, Literal, NamedTuple, Tuple


class VpnService(NamedTuple):
    state: Literal["connected", "disconnected"]
    name: str
    uid: str


def get_vpn_services(
    protocol_filter: str,
    excluded_services: Tuple[str],
) -> Iterator[VpnService]:
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
        "(?P<name>.+)"
        \s+
        \[{protocol_filter}.+\]
        $
        """,
        re.X,
    )
    for line in process.stdout.splitlines():
        if match := re.match(pattern, line):
            if match["name"] in excluded_services:
                continue
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
    protocol_filter = "(PPP:L2TP|VPN)"
    excluded_services = tuple(os.getenv("EXCLUDED_SERVICES", "").split(","))
    print(
        alfred_output(
            get_vpn_services(
                protocol_filter=protocol_filter,
                excluded_services=excluded_services,
            )
        )
    )
