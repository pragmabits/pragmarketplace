#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SRC_DIR="$SCRIPT_DIR/src"
OUTPUT="$SCRIPT_DIR/git-staging.pyz"
DULWICH_VERSION="0.22.8"

echo "==> Installing dulwich $DULWICH_VERSION into $SRC_DIR"
pip install "dulwich==$DULWICH_VERSION" \
    --target="$SRC_DIR" \
    --no-deps \
    --no-binary=:all: \
    --quiet

echo "==> Stripping unnecessary dulwich modules"
cd "$SRC_DIR"
rm -rf \
    dulwich/tests \
    dulwich/contrib \
    dulwich/cloud \
    dulwich/server.py \
    dulwich/client.py \
    dulwich/lfs.py \
    dulwich/web.py \
    dulwich/cli.py \
    dulwich/fastexport.py \
    dulwich/credentials.py \
    dulwich/bundle.py \
    dulwich/archive.py \
    dulwich/stash.py \
    dulwich/mailmap.py \
    dulwich/greenthreads.py \
    dulwich/porcelain.py \
    2>/dev/null || true

echo "==> Building .pyz"
python3 -m zipapp "$SRC_DIR" \
    --output="$OUTPUT" \
    --python="/usr/bin/env python3" \
    --compress

echo "==> Cleaning vendored files from src/"
rm -rf \
    "$SRC_DIR/dulwich" \
    "$SRC_DIR"/*.dist-info \
    "$SRC_DIR/bin"

PYZ_SIZE=$(du -h "$OUTPUT" | cut -f1)
echo "==> Built: $OUTPUT ($PYZ_SIZE)"
echo "==> Done"
