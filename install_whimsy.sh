#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(pwd)"
PYTHON_BIN=""
MODE=""
INSTALL=false
TIME="08:00"

usage() {
  cat <<EOF
Usage: $0 (--launchd|--cron) [--install] [--project-dir DIR] [--python BIN] [--time HH:MM]

Options:
  --launchd        Generate a macOS launchd plist (and optionally install)
  --cron           Generate a crontab entry (and optionally install)
  --install        Actually install (load plist or write crontab). Without this, the script only writes the files and prints instructions.
  --project-dir    Path to project containing whimsy.py (default: current dir)
  --python         Python binary to use (default: .venv/bin/python or system python3)
  --time           Time to run daily in HH:MM (default: 08:00)
EOF
  exit 1
}

if [ "$#" -eq 0 ]; then
  usage
fi

while [ "$#" -gt 0 ]; do
  case "$1" in
    --launchd)
      MODE=launchd
      shift
      ;;
    --cron)
      MODE=cron
      shift
      ;;
    --install)
      INSTALL=true
      shift
      ;;
    --project-dir)
      PROJECT_DIR="$2"
      shift 2
      ;;
    --python)
      PYTHON_BIN="$2"
      shift 2
      ;;
    --time)
      TIME="$2"
      shift 2
      ;;
    -*|--*)
      echo "Unknown option $1"
      usage
      ;;
    *)
      shift
      ;;
  esac
done

# Resolve defaults
if [ -z "$PYTHON_BIN" ]; then
  if [ -x "$PROJECT_DIR/.venv/bin/python" ]; then
    PYTHON_BIN="$PROJECT_DIR/.venv/bin/python"
  else
    PYTHON_BIN="$(command -v python3 || true)"
  fi
fi

if [ -z "$PYTHON_BIN" ]; then
  echo "No python binary found; pass --python or create a .venv in project dir." >&2
  exit 2
fi

WHIMSY_PY="$PROJECT_DIR/whimsy.py"
if [ ! -f "$WHIMSY_PY" ]; then
  echo "Could not find $WHIMSY_PY" >&2
  exit 2
fi

if [ "$MODE" = "" ]; then
  echo "Please specify --launchd or --cron." >&2
  usage
fi

IFS=':' read -r HH MM <<< "${TIME//:/":"}"
if ! [[ $HH =~ ^[0-9]{1,2}$ ]] || ! [[ $MM =~ ^[0-9]{1,2}$ ]]; then
  echo "Invalid time format: $TIME" >&2
  exit 2
fi

if [ "$MODE" = "launchd" ]; then
  PLIST_DIR="$HOME/Library/LaunchAgents"
  PLIST_NAME="com.whimsy.daily.plist"
  PLIST_PATH="$PLIST_DIR/$PLIST_NAME"

  mkdir -p "$PLIST_DIR"

  cat > "$PLIST_PATH" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>com.whimsy.daily</string>
  <key>ProgramArguments</key>
  <array>
    <string>$PYTHON_BIN</string>
    <string>$WHIMSY_PY</string>
    <string>--send-now</string>
  </array>
  <key>StartCalendarInterval</key>
  <dict>
    <key>Hour</key>
    <integer>$HH</integer>
    <key>Minute</key>
    <integer>$MM</integer>
  </dict>
  <key>WorkingDirectory</key>
  <string>$PROJECT_DIR</string>
  <key>StandardOutPath</key>
  <string>$HOME/Library/Logs/com.whimsy.daily.log</string>
  <key>StandardErrorPath</key>
  <string>$HOME/Library/Logs/com.whimsy.daily.err.log</string>
  <key>RunAtLoad</key>
  <false/>
</dict>
</plist>
PLIST

  echo "Wrote launchd plist to: $PLIST_PATH"

  if [ "$INSTALL" = true ]; then
    echo "(Installing) Unloading existing plist if present..."
    launchctl unload "$PLIST_PATH" 2>/dev/null || true
    echo "(Installing) Loading plist..."
    launchctl load "$PLIST_PATH"
    echo "Installed and loaded $PLIST_NAME (runs daily at $TIME)."
  else
    echo "To install: run this script with --install, or load with:\n  launchctl load $PLIST_PATH"
  fi

elif [ "$MODE" = "cron" ]; then
  # Build cron line
  CRON_CMD="$PYTHON_BIN $WHIMSY_PY --send-now >/dev/null 2>&1"
  CRON_LINE="$MM $HH * * * $CRON_CMD # whimsy-daily-email"

  CRON_FILE="$(mktemp -t whimsy_cron.XXXX)"

  # Preserve existing crontab
  crontab -l 2>/dev/null || true > "$CRON_FILE"

  if grep -q "# whimsy-daily-email" "$CRON_FILE"; then
    echo "Existing whimsy cron entry already present in current crontab. Skipping adding." 
    rm -f "$CRON_FILE"
  else
    echo "$CRON_LINE" >> "$CRON_FILE"
    if [ "$INSTALL" = true ]; then
      crontab "$CRON_FILE"
      echo "Installed crontab entry (runs daily at $TIME)."
    else
      echo "Wrote candidate crontab to $CRON_FILE. To install, run:\n  crontab $CRON_FILE"
    fi
  fi
fi

echo "Done."
