#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

docker compose down --remove-orphans >/dev/null 2>&1 || true
docker compose build
docker compose up -d dns_seed
sleep 1
docker compose up -d node_a
sleep 3
docker compose up -d node_b
sleep 3
docker compose up -d node_c
sleep 3
docker compose up -d lp_bot

docker compose logs -f
