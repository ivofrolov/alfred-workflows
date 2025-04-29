#!/bin/dash

FD="${FD:-/opt/homebrew/bin/fd}"
JQ="${JQ:-/usr/bin/jq}"

PATTERN=$(echo "${1:-.}" | sed "s/[[:blank:]][[:blank:]]*/.*/g")
SEARCH_PATHS=$(echo "$SEARCH_PATHS" | xargs -n 1 | sed "s,^~,$HOME,")

JQ_FILTER=$(/bin/cat <<'EOF'
{
    uid: .,
    title: rtrimstr("/") | split("/") | last,
    subtitle: .,
    arg: .,
    icon: {
        type: "fileicon",
        path: .
    },
    type: "file:skipcheck"
}
EOF
)

$FD --full-path --max-results 18 "$PATTERN" $SEARCH_PATHS |
    sed "s,^$HOME,~," |
    $JQ -R "$JQ_FILTER" | $JQ -s '{items: .}'
