#!/usr/bin/env bash

# takes a json file as input and renders the issues to the wiki

declare TEMPLATE
TEMPLATE="[#\(.number)](\(.resourcePath)) \(.titleHTML)"

echo "# Issues"

echo
echo "## Open 🔥"
cat $1 | jq -c -r \
  ".data.repository.issues.nodes[] | select(.state == \"OPEN\") | \"* $TEMPLATE\""

echo
echo "## Closed ✅"
cat $1 | jq -c -r \
  ".data.repository.issues.nodes[] | select(.state == \"CLOSED\") | \"* ~~$TEMPLATE~~\""

echo
echo "---"
echo
echo "_🤖 auto rendered from [GH issues](https://github.com/esnvutbrno/fiesta-plus/labels/%F0%9F%9F%B0%20bug)_"
