#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RESULTS_DIR="$SCRIPT_DIR/../results"

mkdir -p "$RESULTS_DIR"

UDP_LOG="$RESULTS_DIR/udp_logs.log"
TCP_LOG="$RESULTS_DIR/tcp_logs.log"

python3 main.py udp > "$UDP_LOG" 2>&1 &
python3 main.py tcp > "$TCP_LOG" 2>&1 &

wait

echo "Both scripts have finished running. Logs are in $RESULTS_DIR"
