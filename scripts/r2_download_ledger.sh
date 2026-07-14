#!/usr/bin/env bash
set -euo pipefail
: "${R2_ENDPOINT:?R2_ENDPOINT is required}"
: "${R2_BUCKET:?R2_BUCKET is required}"
DEST="${1:-./tameike_ichiranR8.xlsx}"
KEY="${R2_LEDGER_KEY:-raw/tameike_ichiranR8.xlsx}"
aws s3 cp "s3://${R2_BUCKET}/${KEY}" "$DEST" --endpoint-url "$R2_ENDPOINT"
sha256sum "$DEST"
