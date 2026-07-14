#!/usr/bin/env bash
set -euo pipefail
: "${R2_ENDPOINT:?R2_ENDPOINT is required}"
: "${R2_BUCKET:?R2_BUCKET is required}"
SRC="${1:?local import result path is required}"
KEY="${2:-imports/$(basename "$SRC") }"
KEY="${KEY% }"
aws s3 cp "$SRC" "s3://${R2_BUCKET}/${KEY}" --endpoint-url "$R2_ENDPOINT"
