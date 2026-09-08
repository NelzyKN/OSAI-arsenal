#!/usr/bin/env bash
# capture.sh — start a logged shell for exam documentation.
# Every command + output is tee'd into logs/ with a timestamp, ready to paste
# into the OSAI report (documentation requirements are strict — capture as you go).
#
# Usage:  bash capture.sh <label>
# Example: bash capture.sh chain1-host1-recon
mkdir -p logs
LABEL="${1:-session}"
STAMP="$(date +%Y%m%d_%H%M%S)"
LOG="logs/${STAMP}_${LABEL}.log"
echo "[*] logging to ${LOG} — everything you type and see is captured. 'exit' to stop."
exec script -q -f "${LOG}"
