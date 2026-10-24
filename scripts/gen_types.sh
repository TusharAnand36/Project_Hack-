#!/usr/bin/env bash
# Generate TypeScript types from the running FastAPI schema (single source of truth for the API shape).
set -euo pipefail
API_URL="${API_URL:-http://localhost:8000}"
cd "$(dirname "$0")/../web"
npx openapi-typescript "${API_URL}/openapi.json" -o src/api/types.ts --default-non-nullable false
echo "wrote web/src/api/types.ts from ${API_URL}/openapi.json"
