#!/bin/sh

blueutil=${blueutil:-blueutil}
jq=${jq:-jq}

JQ_FILTER_DEVICES="[.[] | select(.paired)]"
JQ_ALFRED_OUTPUT="{items: [.[] | {
    title: (if .connected then \"Disonnect \(.name)\" else \"Connect \(.name)\" end),
    arg: .name,
    uid: .address,
    variables: {
        device: .name,
        address: .address,
        connected: .connected
    }
}]}"

"$blueutil" --paired --format json | "$jq" "$JQ_FILTER_DEVICES" | "$jq" "$JQ_ALFRED_OUTPUT"
