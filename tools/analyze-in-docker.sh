#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
IMAGE="${WHITAKER_IMAGE:-whitaker-mcp}"
docker run --rm \
  -v "$(pwd):/work" \
  -w /work \
  -e WHITAKER_BIN=/opt/whitakers-words/bin/words \
  -e WHITAKER_DIR=/opt/whitakers-words \
  "$IMAGE" \
  python tools/analyze_wordlist.py "$@"
