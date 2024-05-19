#!/usr/bin/env bash

COUNT=`hugo list all | tail -n +2 | wc -l | tr -d ' '`
LATEST=`hugo list all | tail -n +2 | cut -d ',' -f 4 | sort -r | head -1`
jq -n --arg count "$COUNT" --arg latest "$LATEST" '$ARGS.named' > data/stats.json
