#!/usr/bin/env bash

COUNT=`hugo list all future | tail -n +2 | wc -l | tr -d ' '`
LATEST=`hugo list all future | sed -n 2p | cut -d ',' -f 4`
jq -n --arg count "$COUNT" --arg latest "$LATEST" '$ARGS.named' > data/stats.json
