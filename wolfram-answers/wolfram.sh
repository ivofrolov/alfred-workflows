#!/usr/bin/env sh

SHORT_ANSWER_API_URL="https://api.wolframalpha.com/v1/result"

ANSWER=$(curl --silent --get --data-urlencode appid="$WOLFRAM_ALPHA_API_KEY" --data-urlencode i="$1" $SHORT_ANSWER_API_URL)

cat << EOB
{
    "items": [
        {
            "title": "$ANSWER",
            "arg": "$1",
            "text": {
                "copy": "$ANSWER",
                "largetype": "$ANSWER"
            }
        }
    ]
}
EOB
