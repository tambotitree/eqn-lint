#!/usr/bin/env bash
# strip_nonascii.sh - remove non-ASCII characters from all .sh scripts

set -euo pipefail

for f in "$@"; do
    if [ ! -f "$f" ]; then
        echo "Skipping $f (not a file)"
        continue
    fi
    echo "Stripping non-ASCII from $f"
    LC_ALL=C tr -cd '\11\12\15\40-\176' < "$f" > "${f}.tmp" && mv "${f}.tmp" "$f"
done
