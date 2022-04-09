#!/bin/sh

PASSPHRASE=$(./passphrase)

cat << EOB
{"items": [
    {
        "title": "$PASSPHRASE",
        "subtitle": "Action this item to copy result to the clipboard",
        "arg": "$PASSPHRASE",
        "text": {
            "copy": "$PASSPHRASE",
            "largetype": "$PASSPHRASE"
        }
    }
]}
EOB
