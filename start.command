#!/bin/sh
cd "$(dirname "$0")" || exit 1
if command -v python3 >/dev/null 2>&1; then
  python3 serve.py --open
else
  echo "Python 3 is required. Install from https://www.python.org/downloads/"
fi
printf '\nPress Enter to close... '
read answer
