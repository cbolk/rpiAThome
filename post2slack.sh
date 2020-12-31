#!/bin/bash

WEBHOOK=https://hooks.slack.com/services/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
mytext=$1

curl -X post -H 'content-type: application/json' --data = "{'text':'$mytext : sunny: '}" $WEBHOOK

