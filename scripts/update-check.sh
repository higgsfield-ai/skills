#!/usr/bin/env bash
# higgsfield-skills update-check — opt-in version check.
# Prints one of:
#   JUST_UPGRADED <old> <new>       — marker found from a recent upgrade
#   UPGRADE_AVAILABLE <old> <new>   — remote VERSION differs from local
#   (nothing)                       — up to date, snoozed, disabled, or fetch failed
#
# Usage:
#   ./scripts/update-check.sh           # quiet check
#   ./scripts/update-check.sh --force   # bust cache and snooze
#
# Env overrides (testing):
#   SKILL_DIR        — override repo root
#   SKILLS_STATE     — override ~/.higgsfield-skills state directory
#   REMOTE_URL       — override remote VERSION URL
set -euo pipefail

SKILL_DIR="${SKILL_DIR:-$(cd "$(dirname "$0")/.." && pwd)}"
STATE_DIR="${SKILLS_STATE:-$HOME/.higgsfield-skills}"
CACHE_FILE="$STATE_DIR/last-update-check"
MARKER_FILE="$STATE_DIR/just-upgraded-from"
SNOOZE_FILE="$STATE_DIR/update-snoozed"
VERSION_FILE="$SKILL_DIR/VERSION"
REMOTE_URL="${REMOTE_URL:-https://raw.githubusercontent.com/higgsfield-ai/skills/main/VERSION}"

# ─── Force flag ───────────────────────────────────────────
if [ "${1:-}" = "--force" ]; then
  rm -f "$CACHE_FILE" "$SNOOZE_FILE"
fi

# ─── Disabled? ────────────────────────────────────────────
if [ -f "$STATE_DIR/update-check-disabled" ]; then
  exit 0
fi

# ─── Snooze helper ────────────────────────────────────────
# Snooze file format: <version> <level> <epoch>
# Levels: 1=24h, 2=48h, 3+=7d. New version resets snooze.
check_snooze() {
  local remote_ver="$1"
  [ ! -f "$SNOOZE_FILE" ] && return 1
  local v l e
  v="$(awk '{print $1}' "$SNOOZE_FILE")"
  l="$(awk '{print $2}' "$SNOOZE_FILE")"
  e="$(awk '{print $3}' "$SNOOZE_FILE")"
  [ -z "$v" ] || [ -z "$l" ] || [ -z "$e" ] && return 1
  case "$l" in *[!0-9]*) return 1 ;; esac
  case "$e" in *[!0-9]*) return 1 ;; esac
  [ "$v" != "$remote_ver" ] && return 1   # new version → ignore stale snooze
  local d
  case "$l" in
    1) d=86400 ;;
    2) d=172800 ;;
    *) d=604800 ;;
  esac
  local now expires
  now="$(date +%s)"
  expires=$(( e + d ))
  [ "$now" -lt "$expires" ] && return 0
  return 1
}

# ─── Step 1: local version ────────────────────────────────
[ ! -f "$VERSION_FILE" ] && exit 0
LOCAL="$(tr -d '[:space:]' < "$VERSION_FILE")"
[ -z "$LOCAL" ] && exit 0

# ─── Step 2: just-upgraded marker ─────────────────────────
if [ -f "$MARKER_FILE" ]; then
  OLD="$(tr -d '[:space:]' < "$MARKER_FILE")"
  rm -f "$MARKER_FILE" "$SNOOZE_FILE"
  [ -n "$OLD" ] && echo "JUST_UPGRADED $OLD $LOCAL"
fi

# ─── Step 3: cache freshness ──────────────────────────────
# UP_TO_DATE: 60min TTL.  UPGRADE_AVAILABLE: 720min TTL (nag less).
if [ -f "$CACHE_FILE" ]; then
  CACHED="$(cat "$CACHE_FILE")"
  case "$CACHED" in
    UP_TO_DATE*)        TTL=60 ;;
    UPGRADE_AVAILABLE*) TTL=720 ;;
    *)                  TTL=0 ;;
  esac
  STALE=$(find "$CACHE_FILE" -mmin +$TTL 2>/dev/null || true)
  if [ -z "$STALE" ] && [ "$TTL" -gt 0 ]; then
    case "$CACHED" in
      UP_TO_DATE*)
        CV="$(echo "$CACHED" | awk '{print $2}')"
        [ "$CV" = "$LOCAL" ] && exit 0
        ;;
      UPGRADE_AVAILABLE*)
        CO="$(echo "$CACHED" | awk '{print $2}')"
        if [ "$CO" = "$LOCAL" ]; then
          CN="$(echo "$CACHED" | awk '{print $3}')"
          check_snooze "$CN" && exit 0
          echo "$CACHED"
          exit 0
        fi
        ;;
    esac
  fi
fi

# ─── Step 4: fetch remote ─────────────────────────────────
mkdir -p "$STATE_DIR"
REMOTE="$(curl -sf --max-time 5 "$REMOTE_URL" 2>/dev/null | tr -d '[:space:]' || true)"

# Validate: looks like a semver. Reject HTML error pages.
if ! echo "$REMOTE" | grep -qE '^[0-9]+\.[0-9.]+$'; then
  echo "UP_TO_DATE $LOCAL" > "$CACHE_FILE"
  exit 0
fi

if [ "$LOCAL" = "$REMOTE" ]; then
  echo "UP_TO_DATE $LOCAL" > "$CACHE_FILE"
  exit 0
fi

echo "UPGRADE_AVAILABLE $LOCAL $REMOTE" > "$CACHE_FILE"
check_snooze "$REMOTE" && exit 0
echo "UPGRADE_AVAILABLE $LOCAL $REMOTE"
